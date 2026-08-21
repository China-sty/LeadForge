"""数据源接口。"""
from __future__ import annotations

import abc
from typing import List

from ..models import Company


class DataSource(abc.ABC):
    """按关键词拉取候选企业列表。"""

    @abc.abstractmethod
    def fetch_companies(self, keywords: List[str]) -> List[Company]:
        raise NotImplementedError
