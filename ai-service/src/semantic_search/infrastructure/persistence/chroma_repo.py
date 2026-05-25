"""
ChromaDB Vector Repository

实现VectorRepository接口，使用ChromaDB进行向量存储和检索。
复用原chroma_repo.py和ai-service/app.py的逻辑。
"""

import json
import os
from datetime import datetime
from typing import Any, Optional

import chromadb
from chromadb.config import Settings

from src.shared.infrastructure.ml.embedding_model import get_embedding_model
from src.semantic_search.domain.models.search_query import SearchResult
from src.semantic_search.domain.repositories.vector_repo import VectorRepository


class ChromaVectorRepository(VectorRepository):
    """ChromaDB向量仓库实现"""

    def __init__(
        self,
        persist_directory: str | None = None,
        collection_name: str | None = None,
    ) -> None:
        self._persist_dir = persist_directory or os.getenv("CHROMA_PERSIST_DIR", "/app/vector_store")
        self._collection_name = collection_name or os.getenv("CHROMA_COLLECTION", "cutter_knowledge")
        self._client = None
        self._collection = None
        self._embedding_model = get_embedding_model()

    def _ensure_initialized(self) -> None:
        """确保ChromaDB已初始化"""
        if self._client is not None:
            return

        self._client = chromadb.PersistentClient(
            path=self._persist_dir,
            settings=Settings(anonymized_telemetry=False, allow_reset=True),
        )
        self._collection = self._client.get_or_create_collection(
            name=self._collection_name,
            metadata={"description": "Cutter knowledge base"},
        )

    async def add(
        self,
        document_id: str,
        text: str,
        metadata: dict[str, Any],
    ) -> None:
        """添加文档"""
        import asyncio
        await asyncio.to_thread(self._add_sync, document_id, text, metadata)

    def _add_sync(self, document_id: str, text: str, metadata: dict[str, Any]) -> None:
        """同步添加文档"""
        self._ensure_initialized()
        embedding = self._embedding_model.generate(text)
        meta = self._flatten_metadata(metadata)
        meta["_data"] = json.dumps(metadata, ensure_ascii=False, default=str)

        self._collection.add(
            ids=[document_id],
            embeddings=[embedding],
            metadatas=[meta],
            documents=[text],
        )

    async def update(
        self,
        document_id: str,
        text: str,
        metadata: dict[str, Any],
    ) -> None:
        """更新文档"""
        import asyncio
        await asyncio.to_thread(self._update_sync, document_id, text, metadata)

    def _update_sync(self, document_id: str, text: str, metadata: dict[str, Any]) -> None:
        """同步更新文档"""
        self._ensure_initialized()
        embedding = self._embedding_model.generate(text)
        meta = self._flatten_metadata(metadata)
        meta["_data"] = json.dumps(metadata, ensure_ascii=False, default=str)

        self._collection.update(
            ids=[document_id],
            embeddings=[embedding],
            metadatas=[meta],
            documents=[text],
        )

    async def delete(self, document_id: str) -> bool:
        """删除文档"""
        import asyncio
        return await asyncio.to_thread(self._delete_sync, document_id)

    def _delete_sync(self, document_id: str) -> bool:
        """同步删除文档"""
        self._ensure_initialized()
        self._collection.delete(ids=[document_id])
        return True

    async def get(self, document_id: str) -> Optional[dict[str, Any]]:
        """获取文档详情"""
        import asyncio
        return await asyncio.to_thread(self._get_sync, document_id)

    def _get_sync(self, document_id: str) -> Optional[dict[str, Any]]:
        """同步获取文档"""
        self._ensure_initialized()
        result = self._collection.get(
            ids=[document_id],
            include=["metadatas", "documents"],
        )
        if not result["ids"]:
            return None
        return {
            "id": result["ids"][0],
            "metadata": result["metadatas"][0] if result["metadatas"] else None,
            "document": result["documents"][0] if result["documents"] else None,
        }

    async def search(
        self,
        query_text: str,
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
        similarity_threshold: float = 0.0,
    ) -> list[SearchResult]:
        """语义搜索"""
        import asyncio
        return await asyncio.to_thread(
            self._search_sync, query_text, top_k, filters, similarity_threshold
        )

    def _search_sync(
        self,
        query_text: str,
        top_k: int,
        filters: Optional[dict[str, Any]],
        similarity_threshold: float,
    ) -> list[SearchResult]:
        """同步搜索"""
        self._ensure_initialized()
        query_embedding = self._embedding_model.generate(query_text)

        where_filter = None
        if filters:
            where_filter = self._build_where_filter(filters)

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter,
            include=["metadatas", "distances", "documents"],
        )

        search_results = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i] if results["distances"] else 0.0
                similarity = 1.0 / (1.0 + distance)

                if similarity < similarity_threshold:
                    continue

                search_results.append(SearchResult(
                    document_id=doc_id,
                    document_text=results["documents"][0][i] if results["documents"] else "",
                    similarity_score=similarity,
                    metadata=results["metadatas"][0][i] if results["metadatas"] else {},
                ))

        return search_results

    async def count(self) -> int:
        """获取文档总数"""
        import asyncio
        return await asyncio.to_thread(self._count_sync)

    def _count_sync(self) -> int:
        """同步获取总数"""
        self._ensure_initialized()
        return self._collection.count()

    @staticmethod
    def _flatten_metadata(data: dict) -> dict:
        """展平嵌套字典为ChromaDB兼容格式"""
        flat: dict = {}
        for key, value in data.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    coerced = ChromaVectorRepository._coerce_value(sub_value)
                    if coerced is not None:
                        flat[f"{key}.{sub_key}"] = coerced
            else:
                coerced = ChromaVectorRepository._coerce_value(value)
                if coerced is not None:
                    flat[key] = coerced
        return flat

    @staticmethod
    def _coerce_value(value):
        """转换值为ChromaDB兼容类型"""
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, (list, dict)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)

    @staticmethod
    def _build_where_filter(filters: dict) -> dict:
        """构建ChromaDB where过滤条件"""
        where = {}
        for key, value in filters.items():
            if isinstance(value, (str, int, float)):
                where[key] = value
        return where if where else None
