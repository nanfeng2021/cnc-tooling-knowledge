"""
Unit Tests for Domain Models.

Following TDD principles, these tests define the expected behavior
of domain models before implementation.

Test Categories:
- Unit Tests: Test individual classes in isolation
- Integration Tests: Test interactions between components
- Property Tests: Test invariants and properties

Run with: pytest tests/unit/domain/ -v
"""

import pytest
from uuid import uuid4
from datetime import datetime

from src.domain.models.cutter import (
    Cutter,
    CutterType,
    MaterialSpec,
    GeometryParams,
)


class TestCutterType:
    """Tests for CutterType value object."""
    
    def test_create_valid_cutter_type(self):
        """Should create a valid CutterType with required category."""
        cutter_type = CutterType(category="end_mill")
        
        assert cutter_type.category == "end_mill"
        assert cutter_type.subcategory is None
        assert cutter_type.coating is None
    
    def test_create_with_optional_fields(self):
        """Should create CutterType with subcategory and coating."""
        cutter_type = CutterType(
            category="end_mill",
            subcategory="square",
            coating="TiAlN",
        )
        
        assert cutter_type.category == "end_mill"
        assert cutter_type.subcategory == "square"
        assert cutter_type.coating == "TiAlN"
    
    def test_category_required(self):
        """Should raise error if category is missing."""
        with pytest.raises(ValueError, match="category is required"):
            CutterType(category="")
    
    def test_from_string_simple(self):
        """Should parse simple string format."""
        cutter_type = CutterType.from_string("end_mill")
        
        assert cutter_type.category == "end_mill"
        assert cutter_type.subcategory is None
        assert cutter_type.coating is None
    
    def test_from_string_with_subcategory(self):
        """Should parse string with subcategory."""
        cutter_type = CutterType.from_string("end_mill/square")
        
        assert cutter_type.category == "end_mill"
        assert cutter_type.subcategory == "square"
        assert cutter_type.coating is None
    
    def test_from_string_complete(self):
        """Should parse complete string format."""
        cutter_type = CutterType.from_string("end_mill/square/TiAlN")
        
        assert cutter_type.category == "end_mill"
        assert cutter_type.subcategory == "square"
        assert cutter_type.coating == "TiAlN"
    
    def test_is_frozen(self):
        """Should be immutable (frozen dataclass)."""
        cutter_type = CutterType(category="end_mill")
        
        with pytest.raises(Exception):  # FrozenInstanceError
            cutter_type.category = "drill"


class TestMaterialSpec:
    """Tests for MaterialSpec value object."""
    
    def test_create_minimal_spec(self):
        """Should create with only substrate."""
        material = MaterialSpec(substrate="carbide")
        
        assert material.substrate == "carbide"
        assert material.coating_type is None
        assert material.hardness_hrc is None
    
    def test_create_complete_spec(self):
        """Should create with all fields."""
        material = MaterialSpec(
            substrate="carbide",
            coating_type="TiAlN",
            hardness_hrc=62.0,
        )
        
        assert material.substrate == "carbide"
        assert material.coating_type == "TiAlN"
        assert material.hardness_hrc == 62.0
    
    def test_description_minimal(self):
        """Should generate correct description for minimal spec."""
        material = MaterialSpec(substrate="hss")
        
        assert material.description == "hss"
    
    def test_description_with_coating(self):
        """Should include coating in description."""
        material = MaterialSpec(substrate="carbide", coating_type="TiAlN")
        
        assert material.description == "carbide with TiAlN coating"
    
    def test_description_complete(self):
        """Should include all info in description."""
        material = MaterialSpec(
            substrate="carbide",
            coating_type="TiAlN",
            hardness_hrc=62.0,
        )
        
        assert material.description == "carbide with TiAlN coating (62.0 HRC)"


class TestGeometryParams:
    """Tests for GeometryParams value object."""
    
    def test_create_valid_params(self):
        """Should create valid geometry parameters."""
        geometry = GeometryParams(
            diameter=10.0,
            length=75.0,
            flute_length=30.0,
            number_of_flutes=4,
        )
        
        assert geometry.diameter == 10.0
        assert geometry.length == 75.0
        assert geometry.flute_length == 30.0
        assert geometry.number_of_flutes == 4
        assert geometry.helix_angle == 30.0  # default
        assert geometry.corner_radius == 0.0  # default
    
    def test_custom_helix_and_corner(self):
        """Should accept custom helix angle and corner radius."""
        geometry = GeometryParams(
            diameter=10.0,
            length=75.0,
            flute_length=30.0,
            number_of_flutes=4,
            helix_angle=45.0,
            corner_radius=0.5,
        )
        
        assert geometry.helix_angle == 45.0
        assert geometry.corner_radius == 0.5
    
    def test_diameter_must_be_positive(self):
        """Should reject non-positive diameter."""
        with pytest.raises(ValueError, match="Diameter must be positive"):
            GeometryParams(
                diameter=0,
                length=75.0,
                flute_length=30.0,
                number_of_flutes=4,
            )
    
    def test_length_must_be_positive(self):
        """Should reject non-positive length."""
        with pytest.raises(ValueError, match="Length must be positive"):
            GeometryParams(
                diameter=10.0,
                length=-5.0,
                flute_length=30.0,
                number_of_flutes=4,
            )
    
    def test_flutes_must_be_at_least_one(self):
        """Should reject less than 1 flute."""
        with pytest.raises(ValueError, match="Number of flutes must be at least 1"):
            GeometryParams(
                diameter=10.0,
                length=75.0,
                flute_length=30.0,
                number_of_flutes=0,
            )
    
    def test_aspect_ratio_calculation(self):
        """Should calculate correct aspect ratio."""
        geometry = GeometryParams(
            diameter=10.0,
            length=50.0,
            flute_length=20.0,
            number_of_flutes=4,
        )
        
        assert geometry.aspect_ratio == 5.0
    
    def test_is_frozen(self):
        """Should be immutable."""
        geometry = GeometryParams(
            diameter=10.0,
            length=75.0,
            flute_length=30.0,
            number_of_flutes=4,
        )
        
        with pytest.raises(Exception):
            geometry.diameter = 12.0


class TestCutter:
    """Tests for Cutter aggregate root."""
    
    @pytest.fixture
    def valid_cutter_data(self):
        """Provide valid data for creating cutters."""
        return {
            "name": "10mm Carbide End Mill",
            "cutter_type": CutterType(category="end_mill", subcategory="square"),
            "material": MaterialSpec(substrate="carbide", coating_type="TiAlN"),
            "geometry": GeometryParams(
                diameter=10.0,
                length=75.0,
                flute_length=30.0,
                number_of_flutes=4,
            ),
            "recommended_parameters": {
                "vc_steel": 120.0,
                "vc_aluminum": 200.0,
                "fz_steel": 0.05,
            },
            "usage_guidelines": [
                "Use for steel and stainless steel",
                "Avoid interrupted cuts",
            ],
            "compatible_materials": ["steel", "stainless_steel", "cast_iron"],
        }
    
    def test_create_using_factory(self, valid_cutter_data):
        """Should create cutter using factory method."""
        cutter = Cutter.create(**valid_cutter_data)
        
        assert cutter.name == "10mm Carbide End Mill"
        assert cutter.cutter_type.category == "end_mill"
        assert cutter.material.substrate == "carbide"
        assert cutter.geometry.diameter == 10.0
        assert len(cutter.usage_guidelines) == 2
        assert len(cutter.compatible_materials) == 3
    
    def test_auto_generated_id(self, valid_cutter_data):
        """Should generate UUID automatically."""
        cutter = Cutter.create(**valid_cutter_data)
        
        assert cutter.id is not None
        assert isinstance(cutter.id, type(uuid4()))
    
    def test_custom_id(self, valid_cutter_data):
        """Should accept custom ID."""
        custom_id = uuid4()
        cutter = Cutter.create(**valid_cutter_data, cutter_id=custom_id)
        
        assert cutter.id == custom_id
    
    def test_name_required(self, valid_cutter_data):
        """Should require name."""
        valid_cutter_data["name"] = ""
        
        with pytest.raises(ValueError, match="name is required"):
            Cutter.create(**valid_cutter_data)
    
    def test_recommended_parameters_required(self, valid_cutter_data):
        """Should require recommended parameters."""
        valid_cutter_data["recommended_parameters"] = {}
        
        with pytest.raises(ValueError, match="parameters are required"):
            Cutter.create(**valid_cutter_data)
    
    def test_update_usage_guideline(self, valid_cutter_data):
        """Should update usage guideline and timestamp."""
        cutter = Cutter.create(**valid_cutter_data)
        old_updated_at = cutter.updated_at
        
        cutter.update_usage_guideline("New guideline", 0)
        
        assert cutter.usage_guidelines[0] == "New guideline"
        assert cutter.updated_at > old_updated_at
    
    def test_update_invalid_index(self, valid_cutter_data):
        """Should raise error for invalid guideline index."""
        cutter = Cutter.create(**valid_cutter_data)
        
        with pytest.raises(IndexError):
            cutter.update_usage_guideline("Invalid", 99)
    
    def test_add_compatible_material(self, valid_cutter_data):
        """Should add new compatible material."""
        cutter = Cutter.create(**valid_cutter_data)
        
        cutter.add_compatible_material("aluminum")
        
        assert "aluminum" in cutter.compatible_materials
    
    def test_add_duplicate_material(self, valid_cutter_data):
        """Should not add duplicate material."""
        cutter = Cutter.create(**valid_cutter_data)
        original_count = len(cutter.compatible_materials)
        
        cutter.add_compatible_material("steel")  # Already in list
        
        assert len(cutter.compatible_materials) == original_count
    
    def test_is_suitable_for_material_match(self, valid_cutter_data):
        """Should return True for compatible material."""
        cutter = Cutter.create(**valid_cutter_data)
        
        assert cutter.is_suitable_for_material("steel") is True
        assert cutter.is_suitable_for_material("STAINLESS_STEEL") is True  # case insensitive
    
    def test_is_suitable_for_material_no_match(self, valid_cutter_data):
        """Should return False for incompatible material."""
        cutter = Cutter.create(**valid_cutter_data)
        
        assert cutter.is_suitable_for_material("titanium") is False
    
    def test_get_cutting_speed(self, valid_cutter_data):
        """Should return cutting speed for material."""
        cutter = Cutter.create(**valid_cutter_data)
        
        speed = cutter.get_cutting_speed("steel")
        
        assert speed == 120.0
    
    def test_get_cutting_speed_not_available(self, valid_cutter_data):
        """Should return None if speed not specified."""
        cutter = Cutter.create(**valid_cutter_data)
        
        speed = cutter.get_cutting_speed("titanium")
        
        assert speed is None
    
    def test_to_dict_serialization(self, valid_cutter_data):
        """Should serialize to dictionary correctly."""
        cutter = Cutter.create(**valid_cutter_data)
        
        data = cutter.to_dict()
        
        assert data["id"] == str(cutter.id)
        assert data["name"] == cutter.name
        assert data["cutter_type"]["category"] == "end_mill"
        assert data["geometry"]["diameter"] == 10.0
        assert "created_at" in data
        assert "updated_at" in data
