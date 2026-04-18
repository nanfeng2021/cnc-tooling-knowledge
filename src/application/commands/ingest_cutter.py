"""
Application Layer Commands following CQRS pattern.

Commands represent write operations that change state.
Each command is a dataclass with all required parameters.
"""

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class IngestCutterCommand:
    """
    Command to ingest a new cutter into the knowledge base.
    
    Following CQRS principles:
    - Immutable (frozen=True)
    - Contains all data needed for the operation
    - Named as imperative verbs (Ingest, Create, Update)
    """
    
    name: str
    category: str
    subcategory: Optional[str] = None
    coating: Optional[str] = None
    substrate: str = "carbide"
    coating_type: Optional[str] = None
    hardness_hrc: Optional[float] = None
    diameter: float = 0.0
    length: float = 0.0
    flute_length: float = 0.0
    number_of_flutes: int = 4
    helix_angle: float = 30.0
    corner_radius: float = 0.0
    recommended_parameters: dict = field(default_factory=dict)
    usage_guidelines: list[str] = field(default_factory=list)
    compatible_materials: list[str] = field(default_factory=list)
    cutter_id: Optional[UUID] = None
    
    def validate(self) -> list[str]:
        """
        Validate command data before execution.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        if not self.name or len(self.name.strip()) == 0:
            errors.append("Name is required")
        
        if self.diameter <= 0:
            errors.append("Diameter must be positive")
        
        if self.length <= 0:
            errors.append("Length must be positive")
        
        if self.number_of_flutes < 1:
            errors.append("Number of flutes must be at least 1")
        
        return errors


@dataclass(frozen=True)
class UpdateCutterCommand:
    """Command to update an existing cutter."""
    
    cutter_id: UUID
    name: Optional[str] = None
    usage_guidelines: Optional[list[str]] = None
    compatible_materials: Optional[list[str]] = None
    recommended_parameters: Optional[dict] = None


@dataclass(frozen=True)
class DeleteCutterCommand:
    """Command to delete a cutter."""
    
    cutter_id: UUID
