"""CLI 入口：命令行跑一次挖掘流水线并打印结果。"""
from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv

from .config import load_config
from .datasources.mock import MockDataSource
from .llm import LLMClient
from .pipeline import Pipeline

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    load_dotenv()
    parser = argparse.ArgumentParser(description="LeadForge：AI 获客引擎")
    parser.add_argument("--config", default=str(PROJECT_ROOT / "config" / "enterprise.yaml"))
    args = parser.parse_args()

    config = load_config(args.config)
    llm = LLMClient()
    pipeline = Pipeline(config, llm, MockDataSource())

    print(f"企业：{config.name}（{('、'.join(config.products))}）")
    print(f"目标行业关键词：{('、'.join(config.industry_keywords))}\n")

    leads = pipeline.run()
    leads.sort(key=lambda l: -l.total_score)
    print(f"共识别出 {len(leads)} 个目标客户：\n")
    for i, lead in enumerate(leads, 1):
        print(f"{i}. {lead.company.name}（{lead.industry}，{lead.company.scale}）")
        print(f"   综合分 {lead.total_score} | {lead.reason}")
        print(f"   匹配 {lead.scores['行业匹配度']} / 采购 {lead.scores['采购能力']} / 渠道 {lead.scores['渠道价值']}")
        print(f"   触达话术：{lead.outreach}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
