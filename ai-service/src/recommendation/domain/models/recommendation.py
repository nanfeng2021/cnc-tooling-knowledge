"""
Recommendation Domain Models

推荐服务的领域模型。
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ParameterRange:
    """参数范围值对象"""

    min_value: float
    max_value: float
    avg_value: float
    unit: str = ""

    def __post_init__(self) -> None:
        if self.min_value > self.max_value:
            raise ValueError("min_value cannot exceed max_value")


@dataclass(frozen=True)
class RecommendationResult:
    """推荐结果"""

    workpiece_material: str
    iso_code: str
    operation_type: str
    parameters: dict[str, ParameterRange] = field(default_factory=dict)
    source_documents: list[dict[str, Any]] = field(default_factory=list)
    target_diameter: float | None = None

    @property
    def candidate_count(self) -> int:
        return len(self.source_documents)
