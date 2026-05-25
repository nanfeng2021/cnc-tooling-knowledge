"""
Health Check Routes

健康检查端点。
"""

from datetime import datetime

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查"""
    from src.shared.infrastructure.ml.embedding_model import get_embedding_model
    from src.semantic_search.infrastructure.persistence.chroma_repo import ChromaVectorRepository

    model = get_embedding_model()
    repo = ChromaVectorRepository()
    count = await repo.count()

    return {
        "status": "healthy",
        "service": "ai-service",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "model_info": {
            "name": model._model_name,
            "dimension": model.get_dimension(),
        },
        "vector_store": {
            "document_count": count,
        },
    }


@router.get("/health/dependencies")
async def health_dependencies():
    """依赖服务健康检查"""
    from src.semantic_search.infrastructure.persistence.chroma_repo import ChromaVectorRepository

    repo = ChromaVectorRepository()

    # 检查ChromaDB
    chroma_status = "unknown"
    try:
        count = await repo.count()
        chroma_status = f"healthy ({count} documents)"
    except Exception as e:
        chroma_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy",
        "service": "ai-service",
        "dependencies": {
            "chromadb": chroma_status,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }
