"""
Cutter Pydantic Schemas

API请求和响应的Pydantic模型。
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CutterTypeSchema(BaseModel):
    """刀具类型Schema"""
    category: str
    subcategory: str = ""
    variant: Optional[str] = None


class MaterialSpecSchema(BaseModel):
    """材料规格Schema"""
    substrate: str
    coating_type: Optional[str] = None
    hardness_hrc: Optional[float] = None
    iso_class: Optional[str] = None
    material_grade: Optional[str] = None


class GeometryParamsSchema(BaseModel):
    """几何参数Schema"""
    diameter: float
    length: float
    flute_length: float = 0.0
    number_of_flutes: int = 4
    helix_angle: float = 30.0
    corner_radius: float = 0.0


class CutterCreateSchema(BaseModel):
    """创建刀具请求Schema"""
    name: str = Field(..., min_length=1, max_length=200)
    category: str
    subcategory: str = ""
    variant: Optional[str] = None
    substrate: str = "carbide"
    coating_type: Optional[str] = None
    hardness_hrc: Optional[float] = None
    iso_class: Optional[str] = None
    material_grade: Optional[str] = None
    diameter: float = Field(..., gt=0)
    length: float = Field(..., gt=0)
    flute_length: float = 0.0
    number_of_flutes: int = 4
    helix_angle: float = 30.0
    corner_radius: float = 0.0
    recommended_parameters: dict[str, float] = {}
    usage_guidelines: str = ""
    compatible_materials: list[str] = []
    manufacturer_id: Optional[str] = None
    model_number: Optional[str] = None
    image_url: Optional[str] = None


class CutterUpdateSchema(BaseModel):
    """更新刀具请求Schema"""
    name: Optional[str] = None
    model_number: Optional[str] = None
    image_url: Optional[str] = None
    usage_guidelines: Optional[str] = None
    recommended_parameters: Optional[dict[str, float]] = None
    compatible_materials: Optional[list[str]] = None


class CutterResponseSchema(BaseModel):
    """刀具响应Schema"""
    id: str
    name: str
    cutter_type: CutterTypeSchema
    material: MaterialSpecSchema
    geometry: GeometryParamsSchema
    recommended_parameters: dict[str, float] = {}
    usage_guidelines: str = ""
    compatible_materials: list[str] = []
    created_at: datetime
    updated_at: datetime
    manufacturer_id: Optional[str] = None
    model_number: Optional[str] = None
    image_url: Optional[str] = None
