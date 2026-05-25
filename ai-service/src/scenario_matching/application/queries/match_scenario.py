"""
Scenario Matching Queries

场景匹配查询对象。
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MatchScenarioQuery:
    """场景匹配查询"""

    category: str
    material_iso_code: str
    subcategory: str | None = None
    variant: str | None = None
    target_diameter: float | None = None
    manufacturer_id: str | None = None
    top_k: int = 10
    min_score: float = 0.0
