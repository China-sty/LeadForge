"""线索评分 Agent：对目标客户按维度打分。"""
from __future__ import annotations

from ..config import EnterpriseConfig
from ..llm import LLMClient
from ..models import Company, LeadScore

_SYSTEM = """你是 B2B 获客线索评分专家。企业「{enterprise}」生产「{products}」，目标行业关键词：{keywords}。

对目标客户按三个维度打分（0~100）：
- match_score 行业匹配度：行业与目标画像的契合程度
- capability_score 采购能力：规模、渠道、是否具备采购/贴牌能力
- channel_score 渠道价值：作为品牌方/渠道商/OEM 客户的价值

只输出评分结果，不要输出分析过程。"""


class ScorerAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def score(self, company: Company, config: EnterpriseConfig) -> LeadScore:
        system = _SYSTEM.format(
            enterprise=config.name,
            products="、".join(config.products),
            keywords="、".join(config.industry_keywords),
        )
        user = (
            f"目标客户：\n"
            f"- 名称：{company.name}\n"
            f"- 行业：{company.industry}\n"
            f"- 经营范围：{company.scope}\n"
            f"- 规模：{company.scale}\n"
            f"- 地区：{company.region}\n\n"
            f"请打分。"
        )
        return self.llm.chat_structured(
            [{"role": "system", "content": system}, {"role": "user", "content": user}],
            LeadScore,
            temperature=0.0,
        )
