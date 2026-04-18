"""
Embedding Service for generating vector embeddings.

This module provides the infrastructure for text embedding generation:
- Uses sentence-transformers for high-quality embeddings
- Implements caching for performance
- Supports multiple embedding models via Strategy pattern

Design Patterns:
- Strategy Pattern: Different embedding models can be swapped
- Singleton Pattern: Single instance per model for efficiency
- Caching Pattern: Avoid redundant computations
"""

from typing import Optional
from functools import lru_cache
import numpy as np


class EmbeddingService:
    """
    Service for generating text embeddings.
    
    This class wraps the sentence-transformers library and provides:
    - Lazy loading of models (only loaded when first used)
    - LRU caching of embeddings for repeated texts
    - Consistent interface regardless of underlying model
    
    Thread Safety: The model loading is thread-safe due to lazy initialization
    with a module-level cache. Individual embedding generation should be
    synchronized if called concurrently from multiple threads.
    """
    
    _model_cache: dict[str, any] = {}
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: Optional[str] = None,
    ) -> None:
        """
        Initialize the embedding service.
        
        Args:
            model_name: Name of the sentence-transformers model
            device: Device for inference ('cpu', 'cuda', etc.)
                   If None, auto-detects best available device
        """
        self._model_name = model_name
        self._device = device or self._auto_detect_device()
        self._model = None
    
    @staticmethod
    def _auto_detect_device() -> str:
        """Auto-detect best available device for inference."""
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                return "mps"  # Apple Silicon
        except ImportError:
            pass
        return "cpu"
    
    def _load_model(self) -> None:
        """Lazy load the embedding model."""
        if self._model is not None:
            return
        
        # Check global cache first
        if self._model_name in EmbeddingService._model_cache:
            self._model = EmbeddingService._model_cache[self._model_name]
            return
        
        # Load model
        try:
            from sentence_transformers import SentenceTransformer
            
            self._model = SentenceTransformer(
                self._model_name,
                device=self._device,
            )
            
            # Cache for future instances
            EmbeddingService._model_cache[self._model_name] = self._model
            
        except ImportError as e:
            raise ImportError(
                "sentence-transformers is required. "
                "Install with: pip install sentence-transformers"
            ) from e
    
    @lru_cache(maxsize=1000)
    def generate(self, text: str) -> list[float]:
        """
        Generate embedding vector for a text string.
        
        Args:
            text: Input text to embed
            
        Returns:
            Embedding vector as list of floats
            
        Note:
            Results are cached using LRU cache for performance.
            Identical texts will return cached embeddings instantly.
        """
        self._load_model()
        
        # Generate embedding
        embedding = self._model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,  # L2 normalization for cosine similarity
        )
        
        # Convert numpy array to list for JSON serialization
        return embedding.tolist()
    
    def generate_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
            
        Note:
            Batch processing is more efficient than individual calls
            as the model can process multiple texts in parallel.
        """
        self._load_model()
        
        # Separate cached and non-cached texts
        embeddings = []
        uncached_texts = []
        uncached_indices = []
        
        for i, text in enumerate(texts):
            if text in self.generate.cache_info():
                # Use cached result
                embeddings.append(self.generate(text))
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)
                embeddings.append(None)  # Placeholder
        
        # Generate embeddings for uncached texts
        if uncached_texts:
            batch_embeddings = self._model.encode(
                uncached_texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=len(uncached_texts) > 10,
            )
            
            # Fill in the results
            for i, emb in enumerate(batch_embeddings):
                embeddings[uncached_indices[i]] = emb.tolist()
        
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embedding vectors.
        
        Returns:
            Dimension of the embedding space
        """
        self._load_model()
        return self._model.get_sentence_embedding_dimension()
    
    def get_model_info(self) -> dict:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model metadata
        """
        return {
            "model_name": self._model_name,
            "device": self._device,
            "dimension": self.get_embedding_dimension(),
            "cache_info": str(self.generate.cache_info()),
        }
