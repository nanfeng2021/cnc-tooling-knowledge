"""
Cutter Aggregate Root

刀具聚合根，包含刀具的所有业务逻辑。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4


@dataclass(frozen=True)
class CutterType:
    """值对象：刀具类型
    
    三级分类体系：类别 -> 子类别 -> 变体
    - category: ISO主要类别（turning, milling, hole_making, threading, gear_cutting）
    - subcategory: 刀具形式（milling_end_mill, hole_drill, turning_external等）
    - variant: 功能变体（square, ball_nose, twist, spiral_flute等）
    """
    
    category: str  # e.g., "milling", "turning", "hole_making"
    subcategory: str = ""  # e.g., "milling_end_mill", "hole_drill"
    variant: Optional[str] = None  # e.g., "square", "ball_nose", "twist"
    
    def __post_init__(self) -> None:
        if not self.category:
            raise ValueError("Cutter category is required")
    
    @classmethod
    def from_string(cls, value: str) -> "CutterType":
        """从字符串格式解析刀具类型：'category/subcategory/variant'"""
        parts = value.split("/")
        return cls(
            category=parts[0],
            subcategory=parts[1] if len(parts) > 1 else "",
            variant=parts[2] if len(parts) > 2 else None,
        )
    
    def to_string(self) -> str:
        """转换为字符串格式"""
        parts = [self.category]
        if self.subcategory:
            parts.append(self.subcategory)
        if self.variant:
            parts.append(self.variant)
        return "/".join(parts)


@dataclass(frozen=True)
class MaterialSpec:
    """值对象：材料规格"""
    
    substrate: str  # e.g., "carbide_K20", "hss", "cbn"
    coating_type: Optional[str] = None  # e.g., "TiAlN", "PVD_TiAlN", "AlCrN"
    hardness_hrc: Optional[float] = None
    iso_class: Optional[str] = None  # ISO 513 class: "P25", "M20", "K10"
    material_grade: Optional[str] = None  # Manufacturer grade: "4325", "KCP10"
    
    @property
    def description(self) -> str:
        """获取人类可读的材料描述"""
        base = self.substrate
        if self.coating_type:
            base += f" with {self.coating_type} coating"
        if self.hardness_hrc:
            base += f" ({self.hardness_hrc} HRC)"
        return base


@dataclass(frozen=True)
class GeometryParams:
    """值对象：几何参数"""
    
    diameter: float  # mm
    length: float  # mm
    flute_length: float  # mm
    number_of_flutes: int
    helix_angle: float = 30.0  # degrees
    corner_radius: float = 0.0  # mm
    
    def __post_init__(self) -> None:
        if self.diameter <= 0:
            raise ValueError("Diameter must be positive")
        if self.length <= 0:
            raise ValueError("Length must be positive")
        if self.number_of_flutes < 1:
            raise ValueError("Number of flutes must be at least 1")
    
    @property
    def aspect_ratio(self) -> float:
        """计算长径比"""
        return self.length / self.diameter


@dataclass
class Cutter:
    """
    聚合根：表示知识库中的刀具。
    
    这是主要的实体，封装了所有刀具相关的数据和业务逻辑。
    遵循DDD原则：
    - 具有唯一标识（id）
    - 通过验证强制执行不变量
    - 包含其他值对象
    """
    
    id: UUID
    name: str
    cutter_type: CutterType
    material: MaterialSpec
    geometry: GeometryParams
    manufacturer_id: Optional[UUID] = None
    model_number: Optional[str] = None
    image_url: Optional[str] = None
    recommended_parameters: Dict[str, float] = field(default_factory=dict)
    usage_guidelines: str = ""
    compatible_materials: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Cutter name is required")
    
    @classmethod
    def create(
        cls,
        name: str,
        cutter_type: CutterType,
        material: MaterialSpec,
        geometry: GeometryParams,
        manufacturer_id: Optional[UUID] = None,
        model_number: Optional[str] = None,
        image_url: Optional[str] = None,
        recommended_parameters: Optional[Dict[str, float]] = None,
        usage_guidelines: str = "",
        compatible_materials: Optional[List[str]] = None,
        cutter_id: Optional[UUID] = None,
    ) -> "Cutter":
        """创建新的刀具实例"""
        return cls(
            id=cutter_id or uuid4(),
            name=name,
            cutter_type=cutter_type,
            material=material,
            geometry=geometry,
            manufacturer_id=manufacturer_id,
            model_number=model_number,
            image_url=image_url,
            recommended_parameters=recommended_parameters or {},
            usage_guidelines=usage_guidelines,
            compatible_materials=compatible_materials or [],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    
    def update_parameters(self, params: Dict[str, float]) -> None:
        """更新切削参数 - 业务规则验证"""
        self._validate_parameters(params)
        self.recommended_parameters.update(params)
        self.updated_at = datetime.utcnow()
    
    def _validate_parameters(self, params: Dict[str, float]) -> None:
        """验证切削参数"""
        for key, value in params.items():
            if value < 0:
                raise ValueError(f"Parameter {key} must be non-negative")
    
    def add_compatible_material(self, material: str) -> None:
        """添加兼容材料 - 业务规则验证"""
        if not self._is_valid_material(material):
            raise ValueError(f"Invalid material: {material}")
        if material not in self.compatible_materials:
            self.compatible_materials.append(material)
            self.updated_at = datetime.utcnow()
    
    def _is_valid_material(self, material: str) -> bool:
        """验证材料是否有效"""
        valid_materials = [
            "steel", "stainless_steel", "aluminum", "cast_iron",
            "titanium", "nickel_alloy", "copper", "brass",
            "plastic", "composite", "wood"
        ]
        return material.lower() in valid_materials
    
    def update_info(
        self,
        name: Optional[str] = None,
        model_number: Optional[str] = None,
        image_url: Optional[str] = None,
        usage_guidelines: Optional[str] = None,
    ) -> None:
        """更新刀具基本信息"""
        if name is not None:
            self.name = name
        if model_number is not None:
            self.model_number = model_number
        if image_url is not None:
            self.image_url = image_url
        if usage_guidelines is not None:
            self.usage_guidelines = usage_guidelines
        self.updated_at = datetime.utcnow()
    
    def to_document(self) -> str:
        """转换为文档格式（用于嵌入生成）"""
        parts = [
            f"Name: {self.name}",
            f"Type: {self.cutter_type.to_string()}",
            f"Material: {self.material.description}",
            f"Diameter: {self.geometry.diameter}mm",
            f"Length: {self.geometry.length}mm",
            f"Flutes: {self.geometry.number_of_flutes}",
        ]
        
        if self.compatible_materials:
            parts.append(f"Compatible materials: {', '.join(self.compatible_materials)}")
        
        if self.recommended_parameters:
            params = ", ".join(f"{k}: {v}" for k, v in self.recommended_parameters.items())
            parts.append(f"Recommended parameters: {params}")
        
        if self.usage_guidelines:
            parts.append(f"Usage: {self.usage_guidelines}")
        
        return "\n".join(parts)
    
    def to_metadata(self) -> Dict[str, any]:
        """转换为元数据格式（用于向量存储）"""
        return {
            "id": str(self.id),
            "name": self.name,
            "category": self.cutter_type.category,
            "subcategory": self.cutter_type.subcategory,
            "variant": self.cutter_type.variant,
            "substrate": self.material.substrate,
            "coating_type": self.material.coating_type,
            "diameter": self.geometry.diameter,
            "length": self.geometry.length,
            "number_of_flutes": self.geometry.number_of_flutes,
            "manufacturer_id": str(self.manufacturer_id) if self.manufacturer_id else None,
            "model_number": self.model_number,
            "compatible_materials": self.compatible_materials,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }