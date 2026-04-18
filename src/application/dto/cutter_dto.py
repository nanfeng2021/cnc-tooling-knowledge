"""
Data Transfer Objects (DTOs) for the Application layer.

DTOs are used to transfer data between layers and across boundaries.
They are separate from domain models to:
- Prevent leaking domain logic to external layers
- Provide stable interfaces even when domain models change
- Enable different representations for different use cases

Following the DTO pattern with Pydantic for validation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class CutterTypeDTO(BaseModel):
    """DTO for cutter type information."""
    
    category: str = Field(..., description="Main category (e.g., 'end_mill')")
    subcategory: Optional[str] = Field(None, description="Sub-category")
    coating: Optional[str] = Field(None, description="Coating type")
    
    class Config:
        frozen = True  # Immutable DTO


class MaterialSpecDTO(BaseModel):
    """DTO for material specifications."""
    
    substrate: str = Field(..., description="Base material (e.g., 'carbide')")
    coating_type: Optional[str] = Field(None, description="Coating type")
    hardness_hrc: Optional[float] = Field(None, description="Hardness in HRC")
    
    class Config:
        frozen = True


class GeometryParamsDTO(BaseModel):
    """DTO for geometric parameters."""
    
    diameter: float = Field(..., gt=0, description="Diameter in mm")
    length: float = Field(..., gt=0, description="Length in mm")
    flute_length: float = Field(..., gt=0, description="Flute length in mm")
    number_of_flutes: int = Field(..., ge=1, description="Number of flutes")
    helix_angle: float = Field(30.0, description="Helix angle in degrees")
    corner_radius: float = Field(0.0, ge=0, description="Corner radius in mm")
    
    class Config:
        frozen = True
    
    @property
    def aspect_ratio(self) -> float:
        """Calculate length-to-diameter ratio."""
        return self.length / self.diameter


class CutterDTO(BaseModel):
    """
    Main DTO for Cutter aggregate.
    
    This DTO provides a stable interface for external layers
    (API, CLI, etc.) while hiding domain model complexity.
    """
    
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., min_length=1, description="Cutter name")
    cutter_type: CutterTypeDTO = Field(..., description="Cutter type classification")
    material: MaterialSpecDTO = Field(..., description="Material specifications")
    geometry: GeometryParamsDTO = Field(..., description="Geometric parameters")
    recommended_parameters: dict[str, float] = Field(
        default_factory=dict,
        description="Recommended cutting parameters",
    )
    usage_guidelines: list[str] = Field(
        default_factory=list,
        description="Usage guidelines and best practices",
    )
    compatible_materials: list[str] = Field(
        default_factory=list,
        description="Compatible workpiece materials",
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        frozen = True  # Immutable DTO
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }
    
    @classmethod
    def from_domain(cls, cutter: "Cutter") -> "CutterDTO":
        """
        Factory method to create DTO from domain model.
        
        This method encapsulates the transformation logic,
        keeping domain models independent of DTO concerns.
        
        Args:
            cutter: Domain model instance
            
        Returns:
            Corresponding DTO instance
        """
        return cls(
            id=str(cutter.id),
            name=cutter.name,
            cutter_type=CutterTypeDTO(
                category=cutter.cutter_type.category,
                subcategory=cutter.cutter_type.subcategory,
                coating=cutter.cutter_type.coating,
            ),
            material=MaterialSpecDTO(
                substrate=cutter.material.substrate,
                coating_type=cutter.material.coating_type,
                hardness_hrc=cutter.material.hardness_hrc,
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
        )


class CutterSearchResultDTO(BaseModel):
    """
    DTO for search results with relevance score.
    
    Used specifically for semantic search responses where
    we need to include the similarity score alongside the cutter data.
    """
    
    cutter: CutterDTO = Field(..., description="The matched cutter")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    
    class Config:
        frozen = True


class CutterListResponse(BaseModel):
    """Response wrapper for list operations."""
    
    items: list[CutterDTO]
    total: int
    limit: int
    offset: int


class ErrorResponse(BaseModel):
    """Standard error response format."""
    
    error: str
    message: str
    details: Optional[dict] = None
