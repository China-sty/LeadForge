"""智能触达 Agent：为每个目标客户生成个性化触达话术。"""
from __future__ import annotations

from ..config import EnterpriseConfig
from ..llm import LLMClient
from ..models import Company, OutreachMessage

_SYSTEM = """你是 B2B 制造业获客的资深销售。企业「{enterprise}」生产「{products}」。
为下面的目标客户写一条**个性化触达话术**（微信/邮件开场），要求：
- 用客户所在行业/经营范围切入，点出对方可能的痛点
- 突出我方「{products}」的价值
- 自然、不油腻，第一句就能抓住对方
- 简短（100~200字），适合直接发送
只输出触达话术。"""


class OutreachAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def generate(self, company: Company, config: EnterpriseConfig) -> str:
        system = _SYSTEM.format(enterprise=config.name, products="、".join(config.products))
        user = (
            f"目标客户：\n"
            f"- 名称：{company.name}\n"
            f"- 行业：{company.industry}\n"
            f"- 经营范围：{company.scope}\n"
            f"- 规模：{company.scale}\n"
            f"- 地区：{company.region}\n\n"
            f"请写触达话术。"
        )
        msg = self.llm.chat_structured(
            [{"role": "system", "content": system}, {"role": "user", "content": user}],
            OutreachMessage,
            temperature=0.5,
        )
        return f"{msg.subject}\n{msg.content}"
