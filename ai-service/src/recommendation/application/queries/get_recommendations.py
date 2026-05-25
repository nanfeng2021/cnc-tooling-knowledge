"""
Recommendation Queries

推荐查询对象。
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class GetRecommendationsQuery:
    """获取推荐参数查询"""

    workpiece_material: str
    operation_type: str
    target_diameter: float | None = None
    max_results: int = 5
