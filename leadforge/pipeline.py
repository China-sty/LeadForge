"""获客流水线：拉取候选企业 → 潜客挖掘 → 线索评分 → 汇总。"""
from __future__ import annotations

from typing import List

from .agents.miner import MinerAgent
from .agents.scorer import ScorerAgent
from .config import EnterpriseConfig
from .datasources.base import DataSource
from .llm import LLMClient
from .models import Company, Lead


class Pipeline:
    def __init__(self, config: EnterpriseConfig, llm: LLMClient, datasource: DataSource):
        self.config = config
        self.llm = llm
        self.datasource = datasource
        self.miner = MinerAgent(llm)
        self.scorer = ScorerAgent(llm)

    def run(self) -> List[Lead]:
        companies = self.datasource.fetch_companies(self.config.industry_keywords)
        dims = self.config.scoring_dimensions
        leads: List[Lead] = []

        for company in companies:
            judgment = self.miner.judge(company, self.config)
            if not judgment.is_target:
                continue
            score = self.scorer.score(company, self.config)

            # 加权总分（确定性计算，不交给 LLM）
            raw_scores = [score.match_score, score.capability_score, score.channel_score]
            weighted = sum(s * d.weight for s, d in zip(raw_scores, dims))
            total = weighted / self.config.total_weight

            leads.append(
                Lead(
                    company=company,
                    is_target=True,
                    industry=judgment.industry,
                    reason=judgment.reason,
                    scores={
                        "行业匹配度": score.match_score,
                        "采购能力": score.capability_score,
                        "渠道价值": score.channel_score,
                    },
                    total_score=round(total, 1),
                )
            )
        return leads
