"""
Cutter DTOs

数据传输对象，用于应用层和接口层之间传递数据。
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CutterTypeDTO(BaseModel):
    """刀具类型DTO"""
    category: str
    subcategory: str = ""
    variant: Optional[str] = None

    class Config:
        frozen = True


class MaterialSpecDTO(BaseModel):
    """材料规格DTO"""
    substrate: str
    coating_type: Optional[str] = None
    hardness_hrc: Optional[float] = None
    iso_class: Optional[str] = None
    material_grade: Optional[str] = None

    class Config:
        frozen = True


class GeometryParamsDTO(BaseModel):
    """几何参数DTO"""
    diameter: float
    length: float
    flute_length: float = 0.0
    number_of_flutes: int = 4
    helix_angle: float = 30.0
    corner_radius: float = 0.0

    class Config:
        frozen = True


class CutterDTO(BaseModel):
    """刀具主DTO"""
    id: str
    name: str
    cutter_type: CutterTypeDTO
    material: MaterialSpecDTO
    geometry: GeometryParamsDTO
    recommended_parameters: dict[str, float] = Field(default_factory=dict)
    usage_guidelines: str = ""
    compatible_materials: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    manufacturer_id: Optional[str] = None
    model_number: Optional[str] = None
    image_url: Optional[str] = None

    class Config:
        frozen = True

    @classmethod
    def from_domain(cls, cutter) -> "CutterDTO":
        """从领域模型创建DTO"""
        return cls(
            id=str(cutter.id),
            name=cutter.name,
            cutter_type=CutterTypeDTO(
                category=cutter.cutter_type.category,
                subcategory=cutter.cutter_type.subcategory,
                variant=cutter.cutter_type.variant,
            ),
            material=MaterialSpecDTO(
                substrate=cutter.material.substrate,
                coating_type=cutter.material.coating_type,
                hardness_hrc=cutter.material.hardness_hrc,
                iso_class=cutter.material.iso_class,
                material_grade=cutter.material.material_grade,
            ),
            geometry=GeometryParamsDTO(
                diameter=cutter.geometry.diameter,
                length=cutter.geometry.length,
                flute_length=cutter.geometry.flute_length,
                number_of_flutes=cutter.geometry.number_of_flutes,
                helix_angle=cutter.geometry.helix_angle,
                corner_radius=cutter.geometry.corner_radius,
            ),
            recommended_parameters=cutter.recommended_parameters,
            usage_guidelines=cutter.usage_guidelines,
            compatible_materials=cutter.compatible_materials,
            created_at=cutter.created_at,
            updated_at=cutter.updated_at,
            manufacturer_id=str(cutter.manufacturer_id) if cutter.manufacturer_id else None,
            model_number=cutter.model_number,
            image_url=cutter.image_url,
        )


class CutterListResponse(BaseModel):
    """刀具列表响应"""
    items: list[CutterDTO]
    total: int
    limit: int
    offset: int


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    message: str
