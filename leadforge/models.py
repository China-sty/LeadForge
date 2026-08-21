"""数据结构与结构化输出模型。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from pydantic import BaseModel, Field


# —— 数据源返回的公司（候选企业） ——

@dataclass
class Company:
    name: str
    industry: str
    scope: str          # 经营范围描述
    scale: str          # 规模：小型/中型/大型
    region: str
    source: str = "mock"


# —— LLM 结构化输出 ——

class LeadJudgment(BaseModel):
    """潜客挖掘：判断候选企业是否为目标客户。"""
    is_target: bool = Field(description="是否为目标客户")
    industry: str = Field(description="识别出的行业")
    reason: str = Field(description="一句话判断理由")


class LeadScore(BaseModel):
    """线索评分：各维度打分。"""
    match_score: float = Field(description="行业匹配度 0~100")
    capability_score: float = Field(description="采购能力 0~100")
    channel_score: float = Field(description="渠道价值 0~100")
    reason: str = Field(description="评分理由")


class OutreachMessage(BaseModel):
    """智能触达：个性化话术。"""
    subject: str = Field(description="开场白/标题")
    content: str = Field(description="触达话术正文")


class EnquiryResponse(BaseModel):
    """询盘承接：回复 + 报价初稿。"""
    reply: str = Field(description="回复话术")
    quote_draft: str = Field(description="报价初稿")
    next_action: str = Field(description="下一步建议")


# —— 线索阶段（获客漏斗） ——

STAGES = ["待触达", "已触达", "已回复", "报价中", "打样中", "已成交"]


# —— 落库的线索 ——

@dataclass
class Lead:
    company: Company
    is_target: bool
    industry: str
    reason: str
    scores: dict = field(default_factory=dict)
    total_score: float = 0.0
    outreach: str = ""
    stage: str = "待触达"
