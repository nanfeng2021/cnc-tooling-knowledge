"""
Repository interfaces for the Domain layer.

Following DDD principles, repositories are defined in the domain layer
as interfaces. Implementations live in the Infrastructure layer.
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from src.domain.models.cutter import Cutter


class CutterRepository(ABC):
    """
    Repository interface for Cutter aggregate.
    
    This interface defines the contract for persistence operations.
    The actual implementation (ChromaDB, SQL, etc.) is in Infrastructure.
    
    Following the Repository pattern:
    - Provides collection-like interface for aggregates
    - Abstracts persistence logic from domain logic
    - Enables easy testing with mock implementations
    """
    
    @abstractmethod
    def add(self, cutter: Cutter) -> None:
        """
        Add a new cutter to the repository.
        
        Args:
            cutter: The Cutter aggregate to persist
            
        Raises:
            DuplicateCutterError: If a cutter with the same ID already exists
        """
        pass
    
    @abstractmethod
    def get_by_id(self, cutter_id: UUID) -> Optional[Cutter]:
        """
        Retrieve a cutter by its unique ID.
        
        Args:
            cutter_id: The unique identifier of the cutter
            
        Returns:
            The Cutter if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_all(self) -> list[Cutter]:
        """
        Retrieve all cutters from the repository.
        
        Returns:
            List of all Cutter aggregates
        """
        pass
    
    @abstractmethod
    def search_by_query(
        self, 
        query: str, 
        top_k: int = 5,
        filters: Optional[dict] = None,
    ) -> list[tuple[Cutter, float]]:
        """
        Search for cutters using semantic similarity.
        
        Args:
            query: Natural language search query
            top_k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of (Cutter, similarity_score) tuples sorted by relevance
        """
        pass
    
    @abstractmethod
    def search_by_material(
        self, 
        workpiece_material: str,
        top_k: int = 10,
    ) -> list[Cutter]:
        """
        Find cutters suitable for a specific workpiece material.
        
        Args:
            workpiece_material: The material to machine
            top_k: Maximum number of results
            
        Returns:
            List of compatible Cutters
        """
        pass
    
    @abstractmethod
    def update(self, cutter: Cutter) -> None:
        """
        Update an existing cutter.
        
        Args:
            cutter: The Cutter with updated data
            
        Raises:
            CutterNotFoundError: If the cutter doesn't exist
        """
        pass
    
    @abstractmethod
    def delete(self, cutter_id: UUID) -> bool:
        """
        Delete a cutter by ID.
        
        Args:
            cutter_id: The unique identifier of the cutter to delete
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def count(self) -> int:
        """
        Get the total number of cutters in the repository.
        
        Returns:
            Count of cutters
        """
        pass


class RepositoryError(Exception):
    """Base exception for repository errors."""
    pass


class DuplicateCutterError(RepositoryError):
    """Raised when trying to add a cutter that already exists."""
    pass


class CutterNotFoundError(RepositoryError):
    """Raised when a cutter is not found."""
    pass
