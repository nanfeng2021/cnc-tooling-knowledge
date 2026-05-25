"""
SQLAlchemy ORM Models

将领域模型映射到数据库表。
遵循DDD原则：ORM模型在Infrastructure层，与领域模型分离。
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """SQLAlchemy声明式基类"""
    pass


class ManufacturerModel(Base):
    """制造商表"""

    __tablename__ = "manufacturers"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False, unique=True)
    country = Column(String(100), default="")
    website = Column(String(500), default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    cutters = relationship("CutterModel", back_populates="manufacturer")


class CategoryModel(Base):
    """分类表"""

    __tablename__ = "categories"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    parent_id = Column(PG_UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    level = Column(Integer, default=1)  # 1=category, 2=subcategory, 3=variant
    description = Column(Text, default="")

    # 关系
    children = relationship("CategoryModel", backref="parent", remote_side=[id])


class CutterModel(Base):
    """刀具表"""

    __tablename__ = "cutters"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    model_number = Column(String(100), nullable=True)
    image_url = Column(String(500), nullable=True)

    # 分类信息
    category = Column(String(50), nullable=False)
    subcategory = Column(String(100), default="")
    variant = Column(String(100), nullable=True)

    # 材料规格
    substrate = Column(String(50), nullable=False)
    coating_type = Column(String(100), nullable=True)
    hardness_hrc = Column(Float, nullable=True)
    iso_class = Column(String(20), nullable=True)
    material_grade = Column(String(50), nullable=True)

    # 几何参数
    diameter = Column(Float, nullable=False)
    length = Column(Float, nullable=False)
    flute_length = Column(Float, default=0.0)
    number_of_flutes = Column(Integer, default=4)
    helix_angle = Column(Float, default=30.0)
    corner_radius = Column(Float, default=0.0)

    # 业务数据
    recommended_parameters = Column(JSONB, default=dict)
    usage_guidelines = Column(Text, default="")
    compatible_materials = Column(ARRAY(String), default=list)

    # 关联
    manufacturer_id = Column(PG_UUID(as_uuid=True), ForeignKey("manufacturers.id"), nullable=True)
    manufacturer = relationship("ManufacturerModel", back_populates="cutters")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_domain(self):
        """转换为领域模型"""
        from src.domain.models.cutter_aggregate import (
            Cutter,
            CutterType,
            GeometryParams,
            MaterialSpec,
        )

        return Cutter(
            id=self.id,
            name=self.name,
            cutter_type=CutterType(
                category=self.category,
                subcategory=self.subcategory,
                variant=self.variant,
            ),
            material=MaterialSpec(
                substrate=self.substrate,
                coating_type=self.coating_type,
                hardness_hrc=self.hardness_hrc,
                iso_class=self.iso_class,
                material_grade=self.material_grade,
            ),
            geometry=GeometryParams(
                diameter=self.diameter,
                length=self.length,
                flute_length=self.flute_length,
                number_of_flutes=self.number_of_flutes,
                helix_angle=self.helix_angle,
                corner_radius=self.corner_radius,
            ),
            manufacturer_id=self.manufacturer_id,
            model_number=self.model_number,
            image_url=self.image_url,
            recommended_parameters=self.recommended_parameters or {},
            usage_guidelines=self.usage_guidelines or "",
            compatible_materials=self.compatible_materials or [],
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, cutter) -> "CutterModel":
        """从领域模型创建"""
        return cls(
            id=cutter.id,
            name=cutter.name,
            model_number=cutter.model_number,
            image_url=cutter.image_url,
            category=cutter.cutter_type.category,
            subcategory=cutter.cutter_type.subcategory,
            variant=cutter.cutter_type.variant,
            substrate=cutter.material.substrate,
            coating_type=cutter.material.coating_type,
            hardness_hrc=cutter.material.hardness_hrc,
            iso_class=cutter.material.iso_class,
            material_grade=cutter.material.material_grade,
            diameter=cutter.geometry.diameter,
            length=cutter.geometry.length,
            flute_length=cutter.geometry.flute_length,
            number_of_flutes=cutter.geometry.number_of_flutes,
            helix_angle=cutter.geometry.helix_angle,
            corner_radius=cutter.geometry.corner_radius,
            recommended_parameters=cutter.recommended_parameters,
            usage_guidelines=cutter.usage_guidelines,
            compatible_materials=cutter.compatible_materials,
            manufacturer_id=cutter.manufacturer_id,
            created_at=cutter.created_at,
            updated_at=cutter.updated_at,
        )
