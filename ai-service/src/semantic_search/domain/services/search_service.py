"""
Semantic Search Domain Service

语义搜索领域服务，封装搜索业务逻辑。
"""

from dataclasses import dataclass
from typing import Any, Optional

from src.semantic_search.domain.models.search_query import SearchQuery, SearchResult


@dataclass
class SemanticSearchService:
    """语义搜索服务"""

    def __init__(self, vector_repo) -> None:
        self._vector_repo = vector_repo

    async def search(self, query: SearchQuery) -> list[SearchResult]:
        """执行语义搜索"""
        return await self._vector_repo.search(
            query_text=query.query_text,
            top_k=query.top_k,
            filters=query.filters,
            similarity_threshold=query.similarity_threshold,
        )

    async def index_document(
        self,
        document_id: str,
        text: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """索引文档"""
        await self._vector_repo.add(
            document_id=document_id,
            text=text,
            metadata=metadata or {},
        )

    async def update_document(
        self,
        document_id: str,
        text: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """更新文档"""
        await self._vector_repo.update(
            document_id=document_id,
            text=text,
            metadata=metadata or {},
        )

    async def delete_document(self, document_id: str) -> bool:
        """删除文档"""
        return await self._vector_repo.delete(document_id)

    async def get_document(self, document_id: str) -> Optional[dict[str, Any]]:
        """获取文档详情"""
        return await self._vector_repo.get(document_id)
