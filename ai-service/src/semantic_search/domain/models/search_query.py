"""
Search Query Domain Models

语义搜索子域的核心领域模型。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4


@dataclass(frozen=True)
class SearchQuery:
    """值对象：搜索查询"""
    
    query_text: str
    top_k: int = 10
    similarity_threshold: float = 0.7
    filters: Optional[Dict[str, any]] = None
    
    def __post_init__(self) -> None:
        if not self.query_text:
            raise ValueError("Query text is required")
        if self.top_k < 1:
            raise ValueError("top_k must be at least 1")
        if not (0.0 <= self.similarity_threshold <= 1.0):
            raise ValueError("similarity_threshold must be between 0.0 and 1.0")


@dataclass
class SearchResult:
    """值对象：搜索结果"""
    
    document_id: str
    document_text: str
    similarity_score: float
    metadata: Dict[str, any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        if not (0.0 <= self.similarity_score <= 1.0):
            raise ValueError("similarity_score must be between 0.0 and 1.0")


@dataclass
class Document:
    """实体：文档"""
    
    id: str
    text: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def create(
        cls,
        text: str,
        document_id: Optional[str] = None,
        metadata: Optional[Dict[str, any]] = None,
    ) -> "Document":
        """创建新的文档实例"""
        return cls(
            id=document_id or str(uuid4()),
            text=text,
            metadata=metadata or {},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    
    def update_embedding(self, embedding: List[float]) -> None:
        """更新文档的嵌入向量"""
        self.embedding = embedding
        self.updated_at = datetime.utcnow()
    
    def update_text(self, text: str) -> None:
        """更新文档文本"""
        self.text = text
        self.updated_at = datetime.utcnow()
        # 嵌入需要重新生成
        self.embedding = None
    
    def update_metadata(self, metadata: Dict[str, any]) -> None:
        """更新文档元数据"""
        self.metadata.update(metadata)
        self.updated_at = datetime.utcnow()
    
    def to_vector_store_format(self) -> Dict[str, any]:
        """转换为向量存储格式"""
        return {
            "id": self.id,
            "embedding": self.embedding,
            "metadata": {
                **self.metadata,
                "_data": self.text,
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
            }
        }