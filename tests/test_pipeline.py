"""流水线冒烟测试：用假 LLM 跑通「挖掘 → 评分 → 加权总分」闭环。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from leadforge.config import load_config
from leadforge.datasources.mock import MockDataSource
from leadforge.llm import LLMClient
from leadforge.models import LeadJudgment, LeadScore
from leadforge.pipeline import Pipeline

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class FakeLLM(LLMClient):
    def __init__(self):
        self.api_key = "fake"
        self.base_url = "fake"
        self.model = "fake"
        self.client = None

    def chat_structured(self, messages, result_cls, temperature=0.0):
        name = result_cls.__name__
        if name == "LeadJudgment":
            # 只把「健康理疗/户外运动/穿戴设备/家纺/消费电子」判为目标客户
            user = messages[-1]["content"]
            is_target = any(k in user for k in ["健康理疗", "户外运动", "穿戴设备", "家纺", "消费电子"])
            return result_cls(is_target=is_target, industry="示例行业", reason="匹配目标画像")
        if name == "OutreachMessage":
            return result_cls(subject="开场", content="示例话术")
        # LeadScore
        return result_cls(match_score=80, capability_score=70, channel_score=60, reason="示例评分")


def main() -> None:
    config = load_config(str(PROJECT_ROOT / "config" / "enterprise.yaml"))
    pipeline = Pipeline(config, FakeLLM(), MockDataSource())
    leads = pipeline.run()

    assert len(leads) > 0, "应识别出目标客户"
    # 权重 0.4/0.3/0.3，分数 80/70/60 → 总分 71.0
    for lead in leads:
        assert abs(lead.total_score - 71.0) < 0.01, f"总分计算错误: {lead.total_score}"
    print(f"PIPELINE OK —— 识别出 {len(leads)} 个目标客户，总分计算正确")


if __name__ == "__main__":
    main()
