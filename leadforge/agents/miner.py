"""潜客挖掘 Agent：判断候选企业是否为目标客户。"""
from __future__ import annotations

from ..config import EnterpriseConfig
from ..llm import LLMClient
from ..models import Company, LeadJudgment

_SYSTEM = """你是一位 B2B 制造业获客专家。企业「{enterprise}」生产「{products}」，目标客户画像的行业关键词为：{keywords}。

判断候选公司是否为目标客户（潜在品牌方 / 渠道商 / OEM 贴牌客户）。
判断标准：该公司所处行业或经营范围是否与「{products}」相关，是否可能采购、贴牌或代理这类产品。
只输出判断结果，不要输出分析过程。"""


class MinerAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def judge(self, company: Company, config: EnterpriseConfig) -> LeadJudgment:
        system = _SYSTEM.format(
            enterprise=config.name,
            products="、".join(config.products),
            keywords="、".join(config.industry_keywords),
        )
        user = (
            f"候选公司：\n"
            f"- 名称：{company.name}\n"
            f"- 行业：{company.industry}\n"
            f"- 经营范围：{company.scope}\n"
            f"- 规模：{company.scale}\n"
            f"- 地区：{company.region}\n\n"
            f"请判断是否为目标客户。"
        )
        return self.llm.chat_structured(
            [{"role": "system", "content": system}, {"role": "user", "content": user}],
            LeadJudgment,
            temperature=0.0,
        )
