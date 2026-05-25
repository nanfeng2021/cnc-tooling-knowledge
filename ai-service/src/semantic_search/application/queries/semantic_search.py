"""
Semantic Search Queries

语义搜索查询对象。
"""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class SemanticSearchQuery:
    """语义搜索查询"""

    query_text: str
    top_k: int = 10
    similarity_threshold: float = 0.7
    filters: Optional[dict[str, Any]] = None


@dataclass(frozen=True)
class IndexDocumentCommand:
    """索引文档命令"""

    document_id: str
    text: str
    metadata: Optional[dict[str, Any]] = None


@dataclass(frozen=True)
class UpdateDocumentCommand:
    """更新文档命令"""

    document_id: str
    text: str
    metadata: Optional[dict[str, Any]] = None


@dataclass(frozen=True)
class DeleteDocumentCommand:
    """删除文档命令"""

    document_id: str
