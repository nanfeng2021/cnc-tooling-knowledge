"""
Vector Repository Interface

向量仓库接口，定义向量存储和检索的抽象。
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from src.semantic_search.domain.models.search_query import SearchResult


class VectorRepository(ABC):
    """向量仓库接口"""

    @abstractmethod
    async def add(
        self,
        document_id: str,
        text: str,
        metadata: dict[str, Any],
    ) -> None:
        """添加文档到向量库"""
        ...

    @abstractmethod
    async def update(
        self,
        document_id: str,
        text: str,
        metadata: dict[str, Any],
    ) -> None:
        """更新文档"""
        ...

    @abstractmethod
    async def delete(self, document_id: str) -> bool:
        """删除文档"""
        ...

    @abstractmethod
    async def get(self, document_id: str) -> Optional[dict[str, Any]]:
        """获取文档详情"""
        ...

    @abstractmethod
    async def search(
        self,
        query_text: str,
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
        similarity_threshold: float = 0.0,
    ) -> list[SearchResult]:
        """语义搜索"""
        ...

    @abstractmethod
    async def count(self) -> int:
        """获取文档总数"""
        ...
