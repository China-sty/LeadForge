"""企业配置加载（多租户：每个企业一份配置，引擎通用）。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import yaml


@dataclass
class ScoringDimension:
    name: str
    weight: float


@dataclass
class EnterpriseConfig:
    name: str
    products: List[str]
    industry_keywords: List[str]
    scale_prefer: List[str]
    region: str
    scoring_dimensions: List[ScoringDimension]
    scale_min: int
    scale_max: int
    threshold: float

    @property
    def total_weight(self) -> float:
        return sum(d.weight for d in self.scoring_dimensions) or 1.0


def load_config(path: str) -> EnterpriseConfig:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    ent = raw["enterprise"]
    tc = raw["target_customer"]
    sc = raw["scoring"]

    return EnterpriseConfig(
        name=ent.get("name", "示例企业"),
        products=list(ent.get("products", [])),
        industry_keywords=list(tc.get("industry_keywords", [])),
        scale_prefer=list(tc.get("scale_prefer", [])),
        region=tc.get("region", "全国"),
        scoring_dimensions=[
            ScoringDimension(name=d["name"], weight=float(d["weight"]))
            for d in sc.get("dimensions", [])
        ],
        scale_min=int(sc.get("scale_min", 0)),
        scale_max=int(sc.get("scale_max", 100)),
        threshold=float(sc.get("threshold", 60)),
    )
