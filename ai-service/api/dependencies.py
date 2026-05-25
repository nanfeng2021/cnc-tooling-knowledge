"""
API Dependencies

FastAPI依赖注入配置。
"""

from src.semantic_search.infrastructure.persistence.chroma_repo import ChromaVectorRepository


def get_vector_repo() -> ChromaVectorRepository:
    """获取向量仓库实例"""
    return ChromaVectorRepository()
