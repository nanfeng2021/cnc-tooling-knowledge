"""
QA Routes

智能问答API端点。
基于语义搜索实现刀具知识问答。
"""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.semantic_search.application.queries.semantic_search import SemanticSearchQuery
from src.semantic_search.domain.services.search_service import SemanticSearchService
from src.semantic_search.infrastructure.persistence.chroma_repo import ChromaVectorRepository

router = APIRouter()


class QARequest(BaseModel):
    """问答请求"""
    question: str = Field(..., min_length=1, description="用户问题")
    top_k: int = Field(default=5, ge=1, le=20, description="返回相关刀具数量")


class QASource(BaseModel):
    """问答来源"""
    cutter_id: str
    cutter_name: str
    relevance_score: float
    category: str
    diameter: float
    summary: str


class QAResponse(BaseModel):
    """问答响应"""
    question: str
    answer: str
    sources: list[QASource]
    confidence: float


def generate_answer(question: str, sources: list[dict]) -> tuple[str, float]:
    """
    根据搜索结果生成答案。
    
    Args:
        question: 用户问题
        sources: 搜索结果列表
        
    Returns:
        (answer, confidence) 元组
    """
    if not sources:
        return "未找到相关的刀具信息。请尝试使用不同的关键词提问。", 0.0
    
    # 提取关键信息
    categories = set()
    materials = set()
    cutters_info = []
    
    for source in sources:
        metadata = source.get("metadata", {})
        category = metadata.get("category", "")
        if category:
            categories.add(category)
        
        substrate = metadata.get("substrate", "")
        if substrate:
            materials.add(substrate)
        
        cutters_info.append({
            "name": metadata.get("name", source.get("document_id", "")),
            "category": category,
            "diameter": metadata.get("diameter", 0),
            "substrate": substrate,
        })
    
    # 生成答案
    answer_parts = []
    
    if len(cutters_info) == 1:
        c = cutters_info[0]
        answer_parts.append(f"为您找到 1 款相关刀具：{c['name']}")
        if c['category']:
            answer_parts.append(f"类型：{c['category']}")
        if c['diameter']:
            answer_parts.append(f"直径：{c['diameter']}mm")
        if c['substrate']:
            answer_parts.append(f"基材：{c['substrate']}")
    else:
        answer_parts.append(f"为您找到 {len(cutters_info)} 款相关刀具。")
        
        if categories:
            category_names = {
                "turning": "车削",
                "milling": "铣削",
                "hole_making": "孔加工",
                "threading": "螺纹",
                "gear_cutting": "齿轮",
            }
            cat_labels = [category_names.get(c, c) for c in categories]
            answer_parts.append(f"涵盖类型：{'、'.join(cat_labels)}")
        
        if materials:
            answer_parts.append(f"基材包括：{'、'.join(materials)}")
    
    answer = "。".join(answer_parts) + "。"
    
    # 计算置信度
    avg_score = sum(s.get("similarity_score", 0) for s in sources) / len(sources)
    confidence = min(avg_score * 1.2, 1.0)  # 略微提升置信度
    
    return answer, confidence


@router.post("/ask", response_model=QAResponse)
async def ask_question(request: QARequest):
    """
    智能问答接口
    
    接收用户问题，通过语义搜索找到相关刀具，生成结构化答案。
    """
    try:
        repo = ChromaVectorRepository()
        service = SemanticSearchService(repo)
        
        # 执行语义搜索
        query = SemanticSearchQuery(
            query_text=request.question,
            top_k=request.top_k,
            similarity_threshold=0.3,  # QA场景使用较低阈值以获取更多结果
        )
        
        search_results = await service.search(query)
        
        # 转换搜索结果为 QA 来源
        sources = []
        for result in search_results:
            metadata = result.metadata or {}
            sources.append(QASource(
                cutter_id=result.document_id,
                cutter_name=metadata.get("name", result.document_id),
                relevance_score=round(result.similarity_score, 4),
                category=metadata.get("category", ""),
                diameter=float(metadata.get("diameter", 0)),
                summary=f"{metadata.get('category', '')} | {metadata.get('diameter', 0)}mm | {metadata.get('substrate', '')}",
            ))
        
        # 生成答案
        answer, confidence = generate_answer(
            request.question,
            [{"metadata": r.metadata, "similarity_score": r.similarity_score, "document_id": r.document_id} for r in search_results]
        )
        
        return QAResponse(
            question=request.question,
            answer=answer,
            sources=sources,
            confidence=round(confidence, 4),
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问答服务错误: {str(e)}")


@router.get("/health")
async def qa_health():
    """问答服务健康检查"""
    try:
        repo = ChromaVectorRepository()
        count = await repo.count()
        return {
            "status": "healthy",
            "document_count": count,
            "service": "qa",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "service": "qa",
        }
