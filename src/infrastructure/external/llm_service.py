"""
LLM Service for intelligent Q&A.

Supports:
- OpenAI API (GPT-4, GPT-3.5-turbo)
- Local models (via Ollama, llama.cpp)
- Azure OpenAI

Usage:
    from src.infrastructure.external.llm_service import LLMService
    
    llm = LLMService(api_key="your-key", model="gpt-4")
    response = llm.chat("What is the best tool for steel machining?")
"""

import os
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat messages and get response."""
        pass
    
    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> str:
        """Send completion prompt and get response."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self._client = None
    
    @property
    def client(self):
        """Lazy load OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("Please install openai: pip install openai")
        return self._client
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat completion request."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 1024),
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI chat error: {e}")
            raise
    
    def complete(self, prompt: str, **kwargs) -> str:
        """Send completion request."""
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, **kwargs)


class OllamaProvider(LLMProvider):
    """Local Ollama provider for running models locally."""
    
    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self._client = None
    
    @property
    def client(self):
        """Lazy load Ollama client."""
        if self._client is None:
            try:
                from ollama import Client
                self._client = Client(host=self.base_url)
            except ImportError:
                raise ImportError("Please install ollama: pip install ollama")
        return self._client
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat completion request to local Ollama."""
        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": kwargs.get("temperature", 0.7),
                    "num_predict": kwargs.get("max_tokens", 1024),
                }
            )
            return response["message"]["content"]
        except Exception as e:
            logger.error(f"Ollama chat error: {e}")
            raise
    
    def complete(self, prompt: str, **kwargs) -> str:
        """Send completion request."""
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, **kwargs)


class LLMService:
    """
    Main LLM service with RAG integration.
    
    Provides intelligent Q&A by combining:
    - Retrieved context from vector store
    - LLM reasoning and generation
    """
    
    SYSTEM_PROMPT = """You are a CNC machining expert assistant specializing in cutting tools.
You help users with:
- Tool selection recommendations
- Cutting parameter guidance (speed, feed, depth of cut)
- Material-specific tool advice
- Troubleshooting machining issues

Always provide practical, actionable advice based on the context provided.
If you're unsure or lack sufficient information, say so clearly.

Context from knowledge base:
{context}

Answer concisely and professionally."""

    def __init__(
        self,
        provider: str = "openai",
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        base_url: Optional[str] = None,
    ):
        """
        Initialize LLM service.
        
        Args:
            provider: LLM provider ("openai", "ollama", "azure")
            api_key: API key for cloud providers
            model: Model name to use
            base_url: Custom base URL (for Ollama or custom endpoints)
        """
        self.provider_name = provider
        self.model = model
        self.provider = self._create_provider(provider, api_key, model, base_url)
    
    def _create_provider(
        self,
        provider: str,
        api_key: Optional[str],
        model: str,
        base_url: Optional[str],
    ) -> LLMProvider:
        """Create appropriate provider instance."""
        if provider == "openai":
            key = api_key or os.getenv("OPENAI_API_KEY")
            if not key:
                raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env var.")
            return OpenAIProvider(api_key=key, model=model)
        
        elif provider == "ollama":
            return OllamaProvider(model=model, base_url=base_url or "http://localhost:11434")
        
        else:
            raise ValueError(f"Unknown provider: {provider}. Supported: openai, ollama")
    
    def ask(
        self,
        question: str,
        context: Optional[str] = None,
        retrieved_docs: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Ask a question with optional RAG context.
        
        Args:
            question: User's question
            context: Pre-formatted context string
            retrieved_docs: Retrieved documents from vector store
            **kwargs: Additional parameters for LLM
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        # Build context from retrieved documents
        if retrieved_docs and not context:
            context = self._build_context(retrieved_docs)
        
        # Format system prompt with context
        system_prompt = self.SYSTEM_PROMPT.format(context=context or "No additional context provided.")
        
        # Create messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ]
        
        # Get LLM response
        answer = self.provider.chat(messages, **kwargs)
        
        # Build response
        response = {
            "question": question,
            "answer": answer,
            "sources": retrieved_docs[:3] if retrieved_docs else [],
            "model": self.model,
            "provider": self.provider_name,
        }
        
        return response
    
    def _build_context(self, docs: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved documents."""
        context_parts = []
        
        for i, doc in enumerate(docs, 1):
            cutter = doc.get("cutter", {})
            score = doc.get("relevance_score", 0)
            
            parts = [
                f"[Document {i}] (Relevance: {score:.2f})",
                f"Name: {cutter.get('name', 'Unknown')}",
                f"Type: {cutter.get('cutter_type', {}).get('category', 'N/A')}",
                f"Material: {cutter.get('material', {}).get('substrate', 'N/A')}",
                f"Geometry: Φ{cutter.get('geometry', {}).get('diameter', 'N/A')}mm",
            ]
            
            guidelines = cutter.get("usage_guidelines", [])
            if guidelines:
                parts.append("Guidelines:")
                for g in guidelines[:2]:
                    parts.append(f"  - {g}")
            
            context_parts.append("\n".join(parts))
        
        return "\n\n".join(context_parts)
    
    def recommend_tool(
        self,
        workpiece_material: str,
        operation: str,
        machine_type: str = "3-axis",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Get tool recommendation for specific machining operation.
        
        Args:
            workpiece_material: Workpiece material (e.g., "steel", "aluminum")
            operation: Machining operation (e.g., "roughing", "finishing")
            machine_type: Machine type (e.g., "2-axis lathe", "5-axis mill")
            **kwargs: Additional parameters
            
        Returns:
            Tool recommendation with reasoning
        """
        prompt = f"""Recommend the best cutting tool for this machining operation:

- Workpiece Material: {workpiece_material}
- Operation: {operation}
- Machine Type: {machine_type}

Provide:
1. Recommended tool type and geometry
2. Tool material and coating
3. Starting cutting parameters (Vc, fz)
4. Key considerations for this application"""

        response = self.provider.complete(prompt, **kwargs)
        
        return {
            "material": workpiece_material,
            "operation": operation,
            "machine_type": machine_type,
            "recommendation": response,
        }


# Factory function for easy instantiation
def create_llm_service(
    provider: str = "openai",
    model: str = "gpt-4o-mini",
    **kwargs,
) -> LLMService:
    """
    Create LLM service instance.
    
    Examples:
        # OpenAI
        llm = create_llm_service(provider="openai", model="gpt-4o-mini")
        
        # Ollama (local)
        llm = create_llm_service(provider="ollama", model="llama3.2")
    """
    return LLMService(provider=provider, model=model, **kwargs)
