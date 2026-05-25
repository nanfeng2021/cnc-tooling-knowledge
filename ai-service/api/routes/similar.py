"""
Similar Tool Routes

相似刀具查找API端点。
"""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.semantic_search.infrastructure.persistence.chroma_repo import ChromaVectorRepository

router = APIRouter()


class SimilarRequest(BaseModel):
    """相似刀具请求"""
    cutter_id: str = Field(..., description="刀具ID")
    top_k: int = Field(default=5, ge=1, le=20, description="返回结果数量")


class SimilarToolItem(BaseModel):
    """相似刀具结果项"""
    cutter_id: str
    cutter_name: str
    similarity_score: float
    category: Optional[str] = None
    diameter: Optional[float] = None
    substrate: Optional[str] = None


class SimilarToolResponse(BaseModel):
    """相似刀具响应"""
    source_cutter_id: str
    source_cutter_name: str
    similar_cutters: list[SimilarToolItem]
    count: int


@router.post("/find", response_model=SimilarToolResponse)
async def find_similar(request: SimilarRequest):
    """查找相似刀具"""
    try:
        repo = ChromaVectorRepository()

        # 首先获取源刀具信息
        source_doc = await repo.get_by_id(request.cutter_id)
        if not source_doc:
            raise HTTPException(status_code=404, detail=f"Cutter not found: {request.cutter_id}")

        # 使用语义搜索查找相似刀具
        from src.semantic_search.application.queries.semantic_search import SemanticSearchQuery
        from src.semantic_search.domain.services.search_service import SemanticSearchService

        service = SemanticSearchService(repo)

        # 使用源刀具的文本作为查询
        query_text = source_doc.document_text
        query = SemanticSearchQuery(
            query_text=query_text,
            top_k=request.top_k + 1,  # 多查一个，因为结果可能包含源刀具本身
            similarity_threshold=0.3,
        )

        results = await service.search(query)

        # 过滤掉源刀具本身
        similar_items = []
        for r in results:
            if r.document_id != request.cutter_id:
                metadata = r.metadata or {}
                similar_items.append(
                    SimilarToolItem(
                        cutter_id=r.document_id,
                        cutter_name=metadata.get("name", r.document_id),
                        similarity_score=r.similarity_score,
                        category=metadata.get("category"),
                        diameter=metadata.get("diameter"),
                        substrate=metadata.get("substrate"),
                    )
                )
                if len(similar_items) >= request.top_k:
                    break

        source_metadata = source_doc.metadata or {}
        return SimilarToolResponse(
            source_cutter_id=request.cutter_id,
            source_cutter_name=source_metadata.get("name", request.cutter_id),
            similar_cutters=similar_items,
            count=len(similar_items),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
