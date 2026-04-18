"""
ChromaDB implementation of the CutterRepository.

This module provides the infrastructure layer for persistence:
- Implements the Repository interface defined in Domain layer
- Uses ChromaDB for vector storage and semantic search
- Handles embedding generation and similarity matching

Design Patterns:
- Repository Pattern: Concrete implementation of domain interface
- Dependency Injection: Embedding service injected via constructor
"""

import chromadb
from chromadb.config import Settings
from typing import Optional
from uuid import UUID
import numpy as np

from src.domain.models.cutter import Cutter
from src.domain.repositories.cutter_repo import (
    CutterRepository,
    DuplicateCutterError,
    CutterNotFoundError,
)
from src.infrastructure.persistence.embeddings import EmbeddingService


class ChromaCutterRepository(CutterRepository):
    """
    ChromaDB-based repository implementation.
    
    This class provides:
    - Persistent vector storage for cutter documents
    - Semantic search via cosine similarity
    - Metadata filtering capabilities
    
    Thread Safety: ChromaDB client is thread-safe for reads,
    but writes should be synchronized externally if needed.
    """
    
    def __init__(
        self,
        persist_directory: str = "./vector_store",
        collection_name: str = "cutter_knowledge",
        embedding_service: Optional[EmbeddingService] = None,
    ) -> None:
        """
        Initialize the ChromaDB repository.
        
        Args:
            persist_directory: Directory for persistent storage
            collection_name: Name of the ChromaDB collection
            embedding_service: Service for generating embeddings
        """
        # Initialize ChromaDB client with persistence
        self._client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )
        
        # Get or create collection
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Cutter knowledge base"},
        )
        
        # Initialize embedding service
        self._embedding_service = embedding_service or EmbeddingService()
        
        # In-memory cache for quick lookups by ID
        self._cache: dict[str, Cutter] = {}
        
        # Load existing data into cache
        self._load_cache()
    
    def _load_cache(self) -> None:
        """Load all existing cutters into memory cache."""
        all_data = self._collection.get(include=["metadatas", "documents"])
        
        for i, doc_id in enumerate(all_data["ids"]):
            metadata = all_data["metadatas"][i]
            # Reconstruct Cutter from metadata (simplified for now)
            # In production, you'd store full JSON in metadata or a separate DB
            pass
    
    def add(self, cutter: Cutter) -> None:
        """
        Add a cutter to the repository.
        
        Args:
            cutter: The Cutter aggregate to persist
            
        Raises:
            DuplicateCutterError: If cutter ID already exists
        """
        cutter_id_str = str(cutter.id)
        
        # Check for duplicates
        if cutter_id_str in self._cache:
            raise DuplicateCutterError(f"Cutter {cutter_id_str} already exists")
        
        # Generate embedding from cutter text representation
        document_text = self._cutter_to_document(cutter)
        embedding = self._embedding_service.generate(document_text)
        
        # Add to ChromaDB
        self._collection.add(
            ids=[cutter_id_str],
            embeddings=[embedding],
            metadatas=[cutter.to_dict()],
            documents=[document_text],
        )
        
        # Update cache
        self._cache[cutter_id_str] = cutter
    
    def get_by_id(self, cutter_id: UUID) -> Optional[Cutter]:
        """Retrieve a cutter by ID."""
        cutter_id_str = str(cutter_id)
        return self._cache.get(cutter_id_str)
    
    def get_all(self) -> list[Cutter]:
        """Get all cutters from cache."""
        return list(self._cache.values())
    
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
            top_k: Number of results
            filters: Metadata filters (e.g., {"category": "end_mill"})
            
        Returns:
            List of (Cutter, score) tuples sorted by relevance
        """
        # Generate query embedding
        query_embedding = self._embedding_service.generate(query)
        
        # Build where filter for ChromaDB
        where_filter = None
        if filters:
            where_filter = self._build_where_filter(filters)
        
        # Query ChromaDB
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter,
            include=["metadatas", "distances"],
        )
        
        # Process results
        cutters_with_scores = []
        if results["ids"] and results["ids"][0]:
            for i, cutter_id_str in enumerate(results["ids"][0]):
                cutter = self._cache.get(cutter_id_str)
                if cutter:
                    # Convert distance to similarity score (ChromaDB returns L2 distance)
                    distance = results["distances"][0][i] if results["distances"] else 0.0
                    similarity = 1.0 / (1.0 + distance)  # Convert to 0-1 similarity
                    cutters_with_scores.append((cutter, similarity))
        
        return cutters_with_scores
    
    def search_by_material(
        self,
        workpiece_material: str,
        top_k: int = 10,
    ) -> list[Cutter]:
        """
        Find cutters suitable for a workpiece material.
        
        This uses metadata filtering rather than semantic search,
        as material compatibility is a structured property.
        """
        # Filter cutters that are compatible with the material
        compatible = [
            cutter for cutter in self._cache.values()
            if cutter.is_suitable_for_material(workpiece_material)
        ]
        
        # Sort by some criteria (e.g., most recently updated)
        compatible.sort(key=lambda c: c.updated_at, reverse=True)
        
        return compatible[:top_k]
    
    def update(self, cutter: Cutter) -> None:
        """
        Update an existing cutter.
        
        Args:
            cutter: The Cutter with updated data
            
        Raises:
            CutterNotFoundError: If cutter doesn't exist
        """
        cutter_id_str = str(cutter.id)
        
        if cutter_id_str not in self._cache:
            raise CutterNotFoundError(f"Cutter {cutter_id_str} not found")
        
        # Generate new embedding
        document_text = self._cutter_to_document(cutter)
        embedding = self._embedding_service.generate(document_text)
        
        # Update in ChromaDB
        self._collection.update(
            ids=[cutter_id_str],
            embeddings=[embedding],
            metadatas=[cutter.to_dict()],
            documents=[document_text],
        )
        
        # Update cache
        self._cache[cutter_id_str] = cutter
    
    def delete(self, cutter_id: UUID) -> bool:
        """Delete a cutter by ID."""
        cutter_id_str = str(cutter_id)
        
        if cutter_id_str not in self._cache:
            return False
        
        # Delete from ChromaDB
        self._collection.delete(ids=[cutter_id_str])
        
        # Remove from cache
        del self._cache[cutter_id_str]
        
        return True
    
    def count(self) -> int:
        """Get total number of cutters."""
        return len(self._cache)
    
    def _cutter_to_document(self, cutter: Cutter) -> str:
        """
        Convert a Cutter to a text document for embedding.
        
        This method creates a rich text representation that captures
        all searchable aspects of the cutter for semantic search.
        """
        parts = [
            f"Cutter: {cutter.name}",
            f"Type: {cutter.cutter_type.category}",
        ]
        
        if cutter.cutter_type.subcategory:
            parts.append(f"Subtype: {cutter.cutter_type.subcategory}")
        
        if cutter.cutter_type.coating:
            parts.append(f"Coating: {cutter.cutter_type.coating}")
        
        parts.append(f"Material: {cutter.material.substrate}")
        
        if cutter.material.hardness_hrc:
            parts.append(f"Hardness: {cutter.material.hardness_hrc} HRC")
        
        parts.append(
            f"Geometry: {cutter.geometry.diameter}mm diameter, "
            f"{cutter.geometry.length}mm length, "
            f"{cutter.geometry.number_of_flutes} flutes"
        )
        
        if cutter.usage_guidelines:
            parts.append("Usage: " + " ".join(cutter.usage_guidelines))
        
        if cutter.compatible_materials:
            parts.append("Compatible materials: " + ", ".join(cutter.compatible_materials))
        
        return ". ".join(parts)
    
    def _build_where_filter(self, filters: dict) -> dict:
        """
        Build ChromaDB where filter from application filters.
        
        Supports basic equality filters. For complex filters,
        extend this method with $and, $or operators.
        """
        # Simple flat filter conversion
        where = {}
        for key, value in filters.items():
            if isinstance(value, str):
                where[key] = value
            elif isinstance(value, (int, float)):
                where[key] = value
        
        return where if where else None
