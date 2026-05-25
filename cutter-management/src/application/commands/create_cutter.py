"""
Create Cutter Command

创建刀具的CQRS命令。
"""

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass(frozen=True)
class CreateCutterCommand:
    """创建刀具命令"""

    name: str
    category: str
    substrate: str
    diameter: float
    length: float
    subcategory: str = ""
    variant: str | None = None
    coating_type: str | None = None
    hardness_hrc: float | None = None
    iso_class: str | None = None
    material_grade: str | None = None
    flute_length: float = 0.0
    number_of_flutes: int = 4
    helix_angle: float = 30.0
    corner_radius: float = 0.0
    recommended_parameters: dict[str, float] = field(default_factory=dict)
    usage_guidelines: str = ""
    compatible_materials: list[str] = field(default_factory=list)
    manufacturer_id: UUID | None = None
    model_number: str | None = None
    image_url: str | None = None
    cutter_id: UUID | None = None

    def validate(self) -> list[str]:
        """验证命令数据"""
        errors = []
        if not self.name or not self.name.strip():
            errors.append("Name is required")
        if not self.category or not self.category.strip():
            errors.append("Category is required")
        if self.diameter <= 0:
            errors.append("Diameter must be positive")
        if self.length <= 0:
            errors.append("Length must be positive")
        if self.number_of_flutes < 1:
            errors.append("Number of flutes must be at least 1")
        return errors
