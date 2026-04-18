"""
Domain Models for Tooling RAG Knowledge Base.

This module contains the core business entities following DDD principles:
- Aggregate Roots: Cutter (main entity with identity)
- Value Objects: Immutable objects defined by their attributes
- Entities: Objects with distinct identity
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass(frozen=True)
class CutterType:
    """Value Object: Cutter type classification."""
    
    category: str  # e.g., "end_mill", "drill", "reamer"
    subcategory: Optional[str] = None
    coating: Optional[str] = None
    
    def __post_init__(self) -> None:
        if not self.category:
            raise ValueError("Cutter category is required")
    
    @classmethod
    def from_string(cls, value: str) -> "CutterType":
        """Parse cutter type from string format: 'category/subcategory/coating'."""
        parts = value.split("/")
        return cls(
            category=parts[0],
            subcategory=parts[1] if len(parts) > 1 else None,
            coating=parts[2] if len(parts) > 2 else None,
        )


@dataclass(frozen=True)
class GeometryParams:
    """Value Object: Cutter geometric parameters."""
    
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
        """Calculate length-to-diameter ratio."""
        return self.length / self.diameter


@dataclass(frozen=True)
class MaterialSpec:
    """Value Object: Material specifications."""
    
    substrate: str  # e.g., "carbide", "hss"
    coating_type: Optional[str] = None
    hardness_hrc: Optional[float] = None
    
    @property
    def description(self) -> str:
        """Get human-readable material description."""
        base = self.substrate
        if self.coating_type:
            base += f" with {self.coating_type} coating"
        if self.hardness_hrc:
            base += f" ({self.hardness_hrc} HRC)"
        return base


@dataclass
class Cutter:
    """
    Aggregate Root: Represents a cutting tool in the knowledge base.
    
    This is the main entity that encapsulates all cutter-related data
    and business logic. Following DDD principles:
    - Has a unique identity (id)
    - Enforces invariants through validation
    - Contains other value objects
    """
    
    id: UUID
    name: str
    cutter_type: CutterType
    material: MaterialSpec
    geometry: GeometryParams
    recommended_parameters: dict[str, float]
    usage_guidelines: list[str]
    compatible_materials: list[str]
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    embedding_vector: Optional[list[float]] = None
    
    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Cutter name is required")
        if not self.recommended_parameters:
            raise ValueError("Recommended parameters are required")
    
    def update_usage_guideline(self, guideline: str, index: int) -> None:
        """Update a specific usage guideline (demonstrates entity mutability)."""
        if index < 0 or index >= len(self.usage_guidelines):
            raise IndexError("Guideline index out of range")
        self.usage_guidelines[index] = guideline
        self.updated_at = datetime.utcnow()
    
    def add_compatible_material(self, material: str) -> None:
        """Add a compatible workpiece material."""
        if material not in self.compatible_materials:
            self.compatible_materials.append(material)
            self.updated_at = datetime.utcnow()
    
    def is_suitable_for_material(self, material: str) -> bool:
        """Check if cutter is suitable for a given workpiece material."""
        return material.lower() in [m.lower() for m in self.compatible_materials]
    
    def get_cutting_speed(self, workpiece_material: str) -> Optional[float]:
        """Get recommended cutting speed (Vc) for a workpiece material."""
        key = f"vc_{workpiece_material.lower()}"
        return self.recommended_parameters.get(key)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": str(self.id),
            "name": self.name,
            "cutter_type": {
                "category": self.cutter_type.category,
                "subcategory": self.cutter_type.subcategory,
                "coating": self.cutter_type.coating,
            },
            "material": {
                "substrate": self.material.substrate,
                "coating_type": self.material.coating_type,
                "hardness_hrc": self.material.hardness_hrc,
            },
            "geometry": {
                "diameter": self.geometry.diameter,
                "length": self.geometry.length,
                "flute_length": self.geometry.flute_length,
                "number_of_flutes": self.geometry.number_of_flutes,
                "helix_angle": self.geometry.helix_angle,
                "corner_radius": self.geometry.corner_radius,
            },
            "recommended_parameters": self.recommended_parameters,
            "usage_guidelines": self.usage_guidelines,
            "compatible_materials": self.compatible_materials,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @classmethod
    def create(
        cls,
        name: str,
        cutter_type: CutterType,
        material: MaterialSpec,
        geometry: GeometryParams,
        recommended_parameters: dict[str, float],
        usage_guidelines: list[str],
        compatible_materials: list[str],
        cutter_id: Optional[UUID] = None,
    ) -> "Cutter":
        """Factory method to create a new Cutter instance."""
        return cls(
            id=cutter_id or uuid4(),
            name=name,
            cutter_type=cutter_type,
            material=material,
            geometry=geometry,
            recommended_parameters=recommended_parameters,
            usage_guidelines=usage_guidelines,
            compatible_materials=compatible_materials,
        )
