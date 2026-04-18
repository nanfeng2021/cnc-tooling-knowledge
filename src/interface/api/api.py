"""
FastAPI Web API for Tooling RAG Knowledge Base.

This module provides the REST API interface layer:
- Defines routes and endpoints
- Handles request/response validation
- Orchestrates application services

Following Clean Architecture principles:
- Interface layer depends on Application layer
- No business logic in controllers/routes
- Request/Response models separate from domain models

Design Patterns:
- Dependency Injection: Services injected into route handlers
- Controller Pattern: Routes organized by resource
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
import os

from src.application.handlers.cutter_handler import CutterCommandHandler, CutterQueryHandler
from src.application.commands.ingest_cutter import IngestCutterCommand
from src.application.queries.search_cutters import (
    SearchCuttersQuery,
    GetCutterByIdQuery,
    GetAllCuttersQuery,
    SearchByMaterialQuery,
)
from src.application.dto.cutter_dto import (
    CutterDTO,
    CutterSearchResultDTO,
    CutterListResponse,
    ErrorResponse,
)
from src.domain.repositories.cutter_repo import CutterNotFoundError, DuplicateCutterError


# ============================================================================
# LLM Service Imports
# ============================================================================

from typing import Any


# ============================================================================
# Dependency Injection Setup
# ============================================================================

def get_command_handler() -> CutterCommandHandler:
    """Dependency provider for command handler."""
    # In production, this would come from a container or factory
    from src.infrastructure.persistence.chroma_repo import ChromaCutterRepository
    
    repo = ChromaCutterRepository()
    return CutterCommandHandler(repository=repo)


def get_query_handler() -> CutterQueryHandler:
    """Dependency provider for query handler."""
    from src.infrastructure.persistence.chroma_repo import ChromaCutterRepository
    
    repo = ChromaCutterRepository()
    return CutterQueryHandler(repository=repo)


# ============================================================================
# Request/Response Models
# ============================================================================

class IngestCutterRequest(BaseModel):
    """Request model for ingesting a new cutter."""
    
    name: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., description="e.g., 'end_mill', 'drill'")
    subcategory: Optional[str] = None
    coating: Optional[str] = None
    substrate: str = "carbide"
    coating_type: Optional[str] = None
    hardness_hrc: Optional[float] = None
    diameter: float = Field(..., gt=0)
    length: float = Field(..., gt=0)
    flute_length: float = Field(..., gt=0)
    number_of_flutes: int = Field(..., ge=1)
    helix_angle: float = Field(default=30.0)
    corner_radius: float = Field(default=0.0, ge=0)
    recommended_parameters: dict = Field(default_factory=dict)
    usage_guidelines: List[str] = Field(default_factory=list)
    compatible_materials: List[str] = Field(default_factory=list)


class SearchRequest(BaseModel):
    """Request model for semantic search."""
    
    query: str = Field(..., min_length=1, description="Search query")
    top_k: int = Field(default=5, ge=1, le=50)
    filters: Optional[dict] = None


class ChatRequest(BaseModel):
    """Request model for LLM-powered Q&A."""
    
    question: str = Field(..., min_length=1, description="User's question")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of documents to retrieve")
    use_rag: bool = Field(default=True, description="Whether to use RAG context")


class ChatResponse(BaseModel):
    """Response model for Q&A."""
    
    question: str
    answer: str
    sources: List[Dict[str, Any]] = []
    model: str
    provider: str


class ToolRecommendationRequest(BaseModel):
    """Request model for tool recommendation."""
    
    workpiece_material: str = Field(..., description="Workpiece material")
    operation: str = Field(..., description="Machining operation")
    machine_type: str = Field(default="3-axis", description="Machine type")


class ToolRecommendationResponse(BaseModel):
    """Response model for tool recommendation."""
    
    material: str
    operation: str
    machine_type: str
    recommendation: str


# ============================================================================
# FastAPI Application
# ============================================================================

def create_app() -> FastAPI:
    """
    Factory function to create and configure the FastAPI application.
    
    Using a factory pattern allows for:
    - Easy testing with different configurations
    - Middleware customization per environment
    - Dependency injection setup
    """
    
    app = FastAPI(
        title="Tooling RAG Knowledge Base API",
        description="""
        ## Intelligent Cutter Knowledge Base
        
        This API provides:
        - **Cutter Management**: Create, read, update, delete cutter definitions
        - **Semantic Search**: Find cutters using natural language queries
        - **Material Matching**: Discover cutters suitable for specific materials
        - **Parameter Recommendations**: Get cutting parameters for operations
        
        ### Features
        - DDD Architecture
        - CQRS Pattern
        - Vector-based Semantic Search
        - RESTful Design
        """,
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure per environment
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register routes
    register_routes(app)
    
    return app


def register_routes(app: FastAPI) -> None:
    """Register all API routes."""
    
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "tooling-rag"}
    
    @app.post(
        "/cutters",
        response_model=CutterDTO,
        status_code=201,
        tags=["Cutters"],
        responses={400: {"model": ErrorResponse}},
    )
    async def ingest_cutter(
        request: IngestCutterRequest,
        handler: CutterCommandHandler = Depends(get_command_handler),
    ):
        """
        Ingest a new cutter into the knowledge base.
        
        - **name**: Unique cutter name
        - **category**: Main category (end_mill, drill, etc.)
        - **diameter**: Cutter diameter in mm
        - **compatible_materials**: List of workpiece materials
        """
        try:
            command = IngestCutterCommand(
                name=request.name,
                category=request.category,
                subcategory=request.subcategory,
                coating=request.coating,
                substrate=request.substrate,
                coating_type=request.coating_type,
                hardness_hrc=request.hardness_hrc,
                diameter=request.diameter,
                length=request.length,
                flute_length=request.flute_length,
                number_of_flutes=request.number_of_flutes,
                helix_angle=request.helix_angle,
                corner_radius=request.corner_radius,
                recommended_parameters=request.recommended_parameters,
                usage_guidelines=request.usage_guidelines,
                compatible_materials=request.compatible_materials,
            )
            
            result = handler.handle_ingest(command)
            return result
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except DuplicateCutterError as e:
            raise HTTPException(status_code=409, detail=str(e))
    
    @app.get(
        "/cutters",
        response_model=CutterListResponse,
        tags=["Cutters"],
    )
    async def get_all_cutters(
        limit: int = Query(default=100, ge=1, le=500),
        offset: int = Query(default=0, ge=0),
        handler: CutterQueryHandler = Depends(get_query_handler),
    ):
        """
        Retrieve all cutters with pagination.
        
        - **limit**: Maximum number of results
        - **offset**: Number of results to skip
        """
        query = GetAllCuttersQuery(limit=limit, offset=offset)
        items = handler.handle_get_all(query)
        
        return CutterListResponse(
            items=items,
            total=len(items),  # Should be total count from DB
            limit=limit,
            offset=offset,
        )
    
    @app.get(
        "/cutters/{cutter_id}",
        response_model=CutterDTO,
        tags=["Cutters"],
        responses={404: {"model": ErrorResponse}},
    )
    async def get_cutter_by_id(
        cutter_id: str,
        handler: CutterQueryHandler = Depends(get_query_handler),
    ):
        """Retrieve a specific cutter by ID."""
        query = GetCutterByIdQuery(cutter_id=cutter_id)
        result = handler.handle_get_by_id(query)
        
        if not result:
            raise HTTPException(status_code=404, detail="Cutter not found")
        
        return result
    
    @app.post(
        "/search",
        response_model=List[CutterSearchResultDTO],
        tags=["Search"],
    )
    async def search_cutters(
        request: SearchRequest,
        handler: CutterQueryHandler = Depends(get_query_handler),
    ):
        """
        Semantic search for cutters.
        
        Uses vector embeddings to find cutters matching the query meaning,
        not just keyword matching.
        
        Example queries:
        - "carbide end mill for steel"
        - "fine finishing tool for aluminum"
        - "10mm diameter 4-flute cutter"
        """
        query = SearchCuttersQuery(
            query_text=request.query,
            top_k=request.top_k,
            filters=request.filters,
        )
        
        results = handler.handle_search(query)
        return results
    
    @app.get(
        "/search/material/{material}",
        response_model=List[CutterDTO],
        tags=["Search"],
    )
    async def search_by_material(
        material: str,
        top_k: int = Query(default=10, ge=1, le=50),
        handler: CutterQueryHandler = Depends(get_query_handler),
    ):
        """
        Find cutters suitable for a specific workpiece material.
        
        - **material**: Workpiece material (e.g., "steel", "aluminum")
        - **top_k**: Maximum number of results
        """
        query = SearchByMaterialQuery(
            workpiece_material=material,
            top_k=top_k,
        )
        
        results = handler.handle_search_by_material(query)
        return results
    
    @app.post(
        "/chat",
        response_model=ChatResponse,
        tags=["LLM Q&A"],
    )
    async def chat(
        request: ChatRequest,
        query_handler: CutterQueryHandler = Depends(get_query_handler),
    ):
        """
        Intelligent Q&A with RAG context.
        
        Combines retrieved knowledge from vector store with LLM reasoning
        to provide accurate, context-aware answers about cutting tools.
        
        Example questions:
        - "What's the best tool for stainless steel finishing?"
        - "推荐加工铝合金的刀具"
        - "钛合金加工需要注意什么？"
        """
        from src.infrastructure.external.llm_service import create_llm_service
        
        # Retrieve relevant documents
        retrieved_docs = []
        if request.use_rag:
            search_query = SearchCuttersQuery(
                query_text=request.question,
                top_k=request.top_k,
            )
            results = query_handler.handle_search(search_query)
            retrieved_docs = [
                {
                    "cutter": result.cutter.to_dict() if hasattr(result.cutter, 'to_dict') else str(result.cutter),
                    "relevance_score": result.relevance_score,
                }
                for result in results
            ]
        
        # Get LLM response with RAG context
        try:
            llm = create_llm_service(
                provider=os.getenv("LLM_PROVIDER", "openai"),
                model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            )
            
            response = llm.ask(
                question=request.question,
                retrieved_docs=retrieved_docs,
            )
            
            return ChatResponse(
                question=response["question"],
                answer=response["answer"],
                sources=response["sources"],
                model=response["model"],
                provider=response["provider"],
            )
            
        except Exception as e:
            # Fallback without LLM
            return ChatResponse(
                question=request.question,
                answer=f"LLM service unavailable: {str(e)}. Please check your API key configuration.",
                sources=retrieved_docs[:3],
                model="fallback",
                provider="none",
            )
    
    @app.post(
        "/recommend/tool",
        response_model=ToolRecommendationResponse,
        tags=["LLM Q&A"],
    )
    async def recommend_tool(request: ToolRecommendationRequest):
        """
        Get AI-powered tool recommendation for specific machining operation.
        
        Provides detailed recommendations including:
        - Tool type and geometry
        - Material and coating
        - Cutting parameters
        - Key considerations
        """
        from src.infrastructure.external.llm_service import create_llm_service
        
        try:
            llm = create_llm_service(
                provider=os.getenv("LLM_PROVIDER", "openai"),
                model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            )
            
            result = llm.recommend_tool(
                workpiece_material=request.workpiece_material,
                operation=request.operation,
                machine_type=request.machine_type,
            )
            
            return ToolRecommendationResponse(**result)
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Recommendation service unavailable: {str(e)}",
            )
    
    @app.exception_handler(CutterNotFoundError)
    async def cutter_not_found_handler(request, exc):
        return HTTPException(status_code=404, detail=str(exc))
    
    @app.exception_handler(DuplicateCutterError)
    async def duplicate_cutter_handler(request, exc):
        return HTTPException(status_code=409, detail=str(exc))


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
