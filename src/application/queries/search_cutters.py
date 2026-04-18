"""
Application Layer Queries following CQRS pattern.

Queries represent read operations that don't change state.
Each query is a dataclass with search/filter parameters.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class SearchCuttersQuery:
    """
    Query to search for cutters using semantic similarity.
    
    Following CQRS principles:
    - Immutable (frozen=True)
    - Contains all parameters needed for the query
    - Named as nouns (Search, Get, Find)
    """
    
    query_text: str
    top_k: int = 5
    filters: Optional[dict] = None
    
    def __post_init__(self) -> None:
        if not self.query_text or len(self.query_text.strip()) == 0:
            raise ValueError("Query text is required")
        if self.top_k < 1:
            raise ValueError("top_k must be at least 1")


@dataclass(frozen=True)
class GetCutterByIdQuery:
    """Query to retrieve a single cutter by ID."""
    
    cutter_id: str


@dataclass(frozen=True)
class GetAllCuttersQuery:
    """Query to retrieve all cutters."""
    
    limit: int = 100
    offset: int = 0


@dataclass(frozen=True)
class SearchByMaterialQuery:
    """Query to find cutters suitable for a specific material."""
    
    workpiece_material: str
    top_k: int = 10


@dataclass(frozen=True)
class GetCuttingParametersQuery:
    """
    Query to get recommended cutting parameters.
    
    This query demonstrates domain-specific business logic:
    finding the best cutter and its parameters for a given operation.
    """
    
    workpiece_material: str
    operation_type: str  # e.g., "roughing", "finishing"
    target_diameter: Optional[float] = None
    max_results: int = 3
