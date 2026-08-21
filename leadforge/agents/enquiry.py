"""询盘承接 Agent：自动回复询盘、生成报价初稿。"""
from __future__ import annotations

from ..config import EnterpriseConfig
from ..llm import LLMClient
from ..models import Company, EnquiryResponse

_SYSTEM = """你是 B2B 制造业的销售客服。企业「{enterprise}」生产「{products}」。
针对客户询盘，给出：
- reply：回复话术（确认需求 + 澄清关键信息）
- quote_draft：报价初稿（含单价范围、起订量、交期、打样说明）
- next_action：下一步建议
只输出结构化结果。"""


class EnquiryAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def respond(self, company: Company, enquiry: str, config: EnterpriseConfig) -> EnquiryResponse:
        system = _SYSTEM.format(enterprise=config.name, products="、".join(config.products))
        user = (
            f"客户：{company.name}（{company.industry}）\n"
            f"询盘内容：{enquiry}\n\n"
            f"请回复。"
        )
        return self.llm.chat_structured(
            [{"role": "system", "content": system}, {"role": "user", "content": user}],
            EnquiryResponse,
            temperature=0.3,
        )
