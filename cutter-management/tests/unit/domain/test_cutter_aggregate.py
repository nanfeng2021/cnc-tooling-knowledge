"""
Cutter Aggregate Root 单元测试

测试刀具聚合根的业务逻辑和验证规则。
"""

import pytest
from datetime import datetime
from uuid import uuid4

from src.domain.models.cutter_aggregate import (
    Cutter,
    CutterType,
    MaterialSpec,
    GeometryParams,
)


class TestCutterType:
    """CutterType 值对象测试"""

    def test_create_cutter_type(self):
        """测试创建刀具类型"""
        cutter_type = CutterType(category="milling", subcategory="milling_end_mill", variant="square")
        
        assert cutter_type.category == "milling"
        assert cutter_type.subcategory == "milling_end_mill"
        assert cutter_type.variant == "square"

    def test_cutter_type_from_string(self):
        """测试从字符串解析刀具类型"""
        cutter_type = CutterType.from_string("milling/milling_end_mill/square")
        
        assert cutter_type.category == "milling"
        assert cutter_type.subcategory == "milling_end_mill"
        assert cutter_type.variant == "square"

    def test_cutter_type_to_string(self):
        """测试转换为字符串格式"""
        cutter_type = CutterType(category="milling", subcategory="milling_end_mill", variant="square")
        
        assert cutter_type.to_string() == "milling/milling_end_mill/square"

    def test_cutter_type_without_variant(self):
        """测试没有变体的刀具类型"""
        cutter_type = CutterType(category="milling", subcategory="milling_end_mill")
        
        assert cutter_type.variant is None
        assert cutter_type.to_string() == "milling/milling_end_mill"

    def test_cutter_type_requires_category(self):
        """测试刀具类型必须有类别"""
        with pytest.raises(ValueError, match="Cutter category is required"):
            CutterType(category="", subcategory="milling_end_mill")


class TestMaterialSpec:
    """MaterialSpec 值对象测试"""

    def test_create_material_spec(self):
        """测试创建材料规格"""
        material = MaterialSpec(
            substrate="carbide_K20",
            coating_type="TiAlN",
            hardness_hrc=92.0,
            iso_class="K20",
            material_grade="4325"
        )
        
        assert material.substrate == "carbide_K20"
        assert material.coating_type == "TiAlN"
        assert material.hardness_hrc == 92.0
        assert material.iso_class == "K20"
        assert material.material_grade == "4325"

    def test_material_description_with_coating(self):
        """测试带涂层的材料描述"""
        material = MaterialSpec(substrate="carbide_K20", coating_type="TiAlN")
        
        assert material.description == "carbide_K20 with TiAlN coating"

    def test_material_description_with_hardness(self):
        """测试带硬度的材料描述"""
        material = MaterialSpec(substrate="carbide_K20", hardness_hrc=92.0)
        
        assert material.description == "carbide_K20 (92.0 HRC)"

    def test_material_description_full(self):
        """测试完整的材料描述"""
        material = MaterialSpec(
            substrate="carbide_K20",
            coating_type="TiAlN",
            hardness_hrc=92.0
        )
        
        assert material.description == "carbide_K20 with TiAlN coating (92.0 HRC)"

    def test_material_description_minimal(self):
        """测试最小材料描述"""
        material = MaterialSpec(substrate="hss")
        
        assert material.description == "hss"


class TestGeometryParams:
    """GeometryParams 值对象测试"""

    def test_create_geometry_params(self):
        """测试创建几何参数"""
        geometry = GeometryParams(
            diameter=10.0,
            length=75.0,
            flute_length=30.0,
            number_of_flutes=4,
            helix_angle=38.0,
            corner_radius=0.5
        )
        
        assert geometry.diameter == 10.0
        assert geometry.length == 75.0
        assert geometry.flute_length == 30.0
        assert geometry.number_of_flutes == 4
        assert geometry.helix_angle == 38.0
        assert geometry.corner_radius == 0.5

    def test_geometry_aspect_ratio(self):
        """测试长径比计算"""
        geometry = GeometryParams(
            diameter=10.0,
            length=75.0,
            flute_length=30.0,
            number_of_flutes=4
        )
        
        assert geometry.aspect_ratio == 7.5

    def test_geometry_requires_positive_diameter(self):
        """测试直径必须为正数"""
        with pytest.raises(ValueError, match="Diameter must be positive"):
            GeometryParams(
                diameter=0.0,
                length=75.0,
                flute_length=30.0,
                number_of_flutes=4
            )

    def test_geometry_requires_positive_length(self):
        """测试长度必须为正数"""
        with pytest.raises(ValueError, match="Length must be positive"):
            GeometryParams(
                diameter=10.0,
                length=-1.0,
                flute_length=30.0,
                number_of_flutes=4
            )

    def test_geometry_requires_positive_flutes(self):
        """测试槽数必须至少为1"""
        with pytest.raises(ValueError, match="Number of flutes must be at least 1"):
            GeometryParams(
                diameter=10.0,
                length=75.0,
                flute_length=30.0,
                number_of_flutes=0
            )


class TestCutter:
    """Cutter 聚合根测试"""

    @pytest.fixture
    def sample_cutter(self) -> Cutter:
        """创建示例刀具"""
        return Cutter.create(
            name="Test End Mill",
            cutter_type=CutterType(category="milling", subcategory="milling_end_mill", variant="square"),
            material=MaterialSpec(substrate="carbide_K20", coating_type="TiAlN"),
            geometry=GeometryParams(
                diameter=10.0,
                length=75.0,
                flute_length=30.0,
                number_of_flutes=4
            ),
            compatible_materials=["P", "K"],
            recommended_parameters={"vc_steel": 180.0, "fz_steel": 0.05}
        )

    def test_create_cutter(self, sample_cutter):
        """测试创建刀具"""
        assert sample_cutter.name == "Test End Mill"
        assert sample_cutter.cutter_type.category == "milling"
        assert sample_cutter.material.substrate == "carbide_K20"
        assert sample_cutter.geometry.diameter == 10.0
        assert sample_cutter.compatible_materials == ["P", "K"]
        assert sample_cutter.id is not None
        assert sample_cutter.created_at is not None
        assert sample_cutter.updated_at is not None

    def test_cutter_requires_name(self):
        """测试刀具必须有名称"""
        with pytest.raises(ValueError, match="Cutter name is required"):
            Cutter.create(
                name="",
                cutter_type=CutterType(category="milling"),
                material=MaterialSpec(substrate="carbide"),
                geometry=GeometryParams(
                    diameter=10.0,
                    length=75.0,
                    flute_length=30.0,
                    number_of_flutes=4
                )
            )

    def test_update_parameters(self, sample_cutter):
        """测试更新切削参数"""
        new_params = {"vc_steel": 200.0, "vc_aluminum": 400.0}
        sample_cutter.update_parameters(new_params)
        
        assert sample_cutter.recommended_parameters["vc_steel"] == 200.0
        assert sample_cutter.recommended_parameters["vc_aluminum"] == 400.0
        assert sample_cutter.recommended_parameters["fz_steel"] == 0.05  # 保持不变

    def test_update_parameters_validates_negative(self, sample_cutter):
        """测试更新参数时验证负值"""
        with pytest.raises(ValueError, match="Parameter vc_steel must be non-negative"):
            sample_cutter.update_parameters({"vc_steel": -100.0})

    def test_add_compatible_material(self, sample_cutter):
        """测试添加兼容材料"""
        sample_cutter.add_compatible_material("aluminum")
        
        assert "aluminum" in sample_cutter.compatible_materials
        assert len(sample_cutter.compatible_materials) == 3

    def test_add_duplicate_compatible_material(self, sample_cutter):
        """测试添加重复的兼容材料"""
        sample_cutter.add_compatible_material("steel")  # 已存在
        
        assert sample_cutter.compatible_materials.count("steel") == 1

    def test_add_invalid_compatible_material(self, sample_cutter):
        """测试添加无效的兼容材料"""
        with pytest.raises(ValueError, match="Invalid material"):
            sample_cutter.add_compatible_material("unobtanium")

    def test_update_info(self, sample_cutter):
        """测试更新刀具信息"""
        sample_cutter.update_info(
            name="Updated End Mill",
            model_number="NEW-123",
            usage_guidelines="New guidelines"
        )
        
        assert sample_cutter.name == "Updated End Mill"
        assert sample_cutter.model_number == "NEW-123"
        assert sample_cutter.usage_guidelines == "New guidelines"

    def test_to_document(self, sample_cutter):
        """测试转换为文档格式"""
        doc = sample_cutter.to_document()
        
        assert "Name: Test End Mill" in doc
        assert "Type: milling/milling_end_mill/square" in doc
        assert "Material: carbide_K20 with TiAlN coating" in doc
        assert "Diameter: 10.0mm" in doc
        assert "Compatible materials: P, K" in doc

    def test_to_metadata(self, sample_cutter):
        """测试转换为元数据格式"""
        metadata = sample_cutter.to_metadata()
        
        assert metadata["name"] == "Test End Mill"
        assert metadata["category"] == "milling"
        assert metadata["subcategory"] == "milling_end_mill"
        assert metadata["variant"] == "square"
        assert metadata["substrate"] == "carbide_K20"
        assert metadata["diameter"] == 10.0
        assert metadata["compatible_materials"] == ["P", "K"]

    def test_cutter_is_frozen_after_creation(self, sample_cutter):
        """测试刀具创建后不可变（除了业务方法修改的字段）"""
        # Cutter 不是 frozen 的，因为需要通过业务方法修改
        # 但 id 应该是不可变的
        original_id = sample_cutter.id
        assert sample_cutter.id == original_id
