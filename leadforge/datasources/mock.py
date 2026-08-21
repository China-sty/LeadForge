"""示例数据源（MVP 演示用，脱敏，不涉及真实企业）。"""
from __future__ import annotations

from typing import List

from ..models import Company
from .base import DataSource

# 示例候选企业：相关行业 + 无关行业混合，用于演示「挖掘 agent 的筛选能力」
_MOCK_COMPANIES = [
    Company("康健理疗科技有限公司", "健康理疗", "理疗设备、按摩器械研发与销售", "中型", "广东"),
    Company("户外先锋运动用品有限公司", "户外运动", "户外装备、运动服饰设计销售", "中型", "浙江"),
    Company("暖芯智能穿戴有限公司", "穿戴设备", "智能穿戴设备、发热产品研发", "小型", "深圳"),
    Company("柔暖家纺集团有限公司", "家纺", "家纺用品、保暖产品生产销售", "大型", "江苏"),
    Company("悦享生活电器有限公司", "消费电子", "小家电、生活电器研发销售", "中型", "上海"),
    Company("康宁医疗器械有限公司", "医疗器械", "理疗器械、康复设备", "中型", "北京"),
    Company("暖冬服饰品牌有限公司", "服装", "服饰、保暖服装设计与品牌运营", "中型", "福建"),
    Company("味美餐饮管理有限公司", "餐饮", "餐饮管理、连锁加盟", "小型", "成都"),
    Company("恒达房地产开发有限公司", "房地产", "房地产开发、销售", "大型", "北京"),
    Company("精工机械制造有限公司", "机械制造", "工业机械、零部件加工", "中型", "山东"),
    Company("启航教育培训有限公司", "教育", "教育培训、课程服务", "小型", "武汉"),
    Company("绿源环保科技有限公司", "环保", "环保设备、污水处理", "中型", "江苏"),
]


class MockDataSource(DataSource):
    """返回固定示例企业列表。"""

    def fetch_companies(self, keywords: List[str]) -> List[Company]:
        return list(_MOCK_COMPANIES)
