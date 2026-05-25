"""
Update Cutter Command

更新刀具的CQRS命令。
"""

from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True)
class UpdateCutterCommand:
    """更新刀具命令"""

    cutter_id: UUID
    name: str | None = None
    category: str | None = None
    subcategory: str | None = None
    variant: str | None = None
    substrate: str | None = None
    coating_type: str | None = None
    hardness_hrc: float | None = None
    iso_class: str | None = None
    material_grade: str | None = None
    diameter: float | None = None
    length: float | None = None
    flute_length: float | None = None
    number_of_flutes: int | None = None
    helix_angle: float | None = None
    corner_radius: float | None = None
    recommended_parameters: dict[str, float] | None = None
    usage_guidelines: str | None = None
    compatible_materials: list[str] | None = None
    manufacturer_id: UUID | None = None
    model_number: str | None = None
    image_url: str | None = None
