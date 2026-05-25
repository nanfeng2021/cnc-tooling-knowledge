"""
Semantic Search Domain Models Package

语义搜索子域的领域模型。
"""

from .search_query import SearchQuery, SearchResult, Document

__all__ = [
    "SearchQuery",
    "SearchResult",
    "Document",
]