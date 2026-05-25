"""
Machining Scenario Domain Models

场景匹配的领域模型。
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class MachiningScenario:
    """加工场景值对象"""

    category: str
    material_iso_code: str
    subcategory: str | None = None
    variant: str | None = None
    target_diameter: float | None = None
    manufacturer_id: str | None = None

    def __post_init__(self) -> None:
        if not self.category:
            raise ValueError("Category is required")
        if not self.material_iso_code:
            raise ValueError("Material ISO code is required")


@dataclass(frozen=True)
class ScenarioMatchResult:
    """场景匹配结果"""

    document_id: str
    score: float
    score_breakdown: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"Score must be in [0, 1], got {self.score}")
