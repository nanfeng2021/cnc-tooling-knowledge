"""
Search Routes

语义搜索API端点。
"""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.semantic_search.application.queries.semantic_search import (
    SemanticSearchQuery,
    IndexDocumentCommand,
    DeleteDocumentCommand,
)
from src.semantic_search.domain.services.search_service import SemanticSearchService
from src.semantic_search.infrastructure.persistence.chroma_repo import ChromaVectorRepository

router = APIRouter()


class SearchRequest(BaseModel):
    """搜索请求"""
    query: str = Field(..., min_length=1, description="搜索查询文本")
    top_k: int = Field(default=10, ge=1, le=100, description="返回结果数量")
    similarity_threshold: float = Field(default=0.7, ge=0, le=1, description="相似度阈值")
    filters: Optional[dict[str, Any]] = Field(default=None, description="过滤条件")


class SearchResultItem(BaseModel):
    """搜索结果项"""
    document_id: str
    document_text: str
    similarity_score: float
    metadata: dict[str, Any] = {}


class SearchResponse(BaseModel):
    """搜索响应"""
    results: list[SearchResultItem]
    total: int


@router.post("", response_model=SearchResponse)
async def semantic_search(request: SearchRequest):
    """执行语义搜索"""
    try:
        repo = ChromaVectorRepository()
        service = SemanticSearchService(repo)

        query = SemanticSearchQuery(
            query_text=request.query,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            filters=request.filters,
        )

        results = await service.search(query)

        return SearchResponse(
            results=[
                SearchResultItem(
                    document_id=r.document_id,
                    document_text=r.document_text,
                    similarity_score=r.similarity_score,
                    metadata=r.metadata,
                )
                for r in results
            ],
            total=len(results),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=SearchResponse)
async def semantic_search_get(
    q: str,
    limit: int = 20,
    offset: int = 0,
    top_k: int = 10,
    similarity_threshold: float = 0.7,
    filters: Optional[str] = None,
):
    """执行语义搜索（GET方法，兼容前端调用）"""
    try:
        repo = ChromaVectorRepository()
        service = SemanticSearchService(repo)

        import json
        filter_dict = json.loads(filters) if filters else None

        query = SemanticSearchQuery(
            query_text=q,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            filters=filter_dict,
        )

        results = await service.search(query)

        # 应用offset和limit进行分页
        paginated = results[offset:offset + limit]

        return SearchResponse(
            results=[
                SearchResultItem(
                    document_id=r.document_id,
                    document_text=r.document_text,
                    similarity_score=r.similarity_score,
                    metadata=r.metadata,
                )
                for r in paginated
            ],
            total=len(results),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def search_health():
    """搜索服务健康检查"""
    repo = ChromaVectorRepository()
    count = await repo.count()
    return {"status": "healthy", "document_count": count}
