"""
Semantic Search Service 单元测试

测试语义搜索服务的业务逻辑。
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.semantic_search.domain.services.search_service import SemanticSearchService
from src.semantic_search.domain.models.search_query import SearchQuery, SearchResult, Document


class TestSemanticSearchService:
    """SemanticSearchService 测试"""

    @pytest.fixture
    def mock_vector_repo(self) -> AsyncMock:
        """模拟向量仓库"""
        repo = AsyncMock()
        repo.add = AsyncMock()
        repo.update = AsyncMock()
        repo.delete = AsyncMock()
        repo.get = AsyncMock()
        repo.search = AsyncMock()
        repo.count = AsyncMock(return_value=0)
        return repo

    @pytest.fixture
    def service(self, mock_vector_repo) -> SemanticSearchService:
        """创建搜索服务实例"""
        return SemanticSearchService(vector_repo=mock_vector_repo)

    @pytest.mark.asyncio
    async def test_search_success(self, service, mock_vector_repo):
        """测试成功搜索"""
        # 设置 mock 返回值
        mock_vector_repo.search.return_value = [
            SearchResult(
                document_id=str(uuid4()),
                document_text="10mm carbide end mill",
                similarity_score=0.95,
                metadata={"name": "Test End Mill", "category": "milling"}
            ),
            SearchResult(
                document_id=str(uuid4()),
                document_text="12mm carbide end mill",
                similarity_score=0.85,
                metadata={"name": "Another End Mill", "category": "milling"}
            )
        ]

        # 执行搜索
        query = SearchQuery(query_text="10mm end mill for steel", top_k=10)
        results = await service.search(query)

        # 验证结果
        assert len(results) == 2
        assert results[0].similarity_score > results[1].similarity_score
        mock_vector_repo.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_with_filters(self, service, mock_vector_repo):
        """测试带过滤条件的搜索"""
        # 设置 mock 返回值
        mock_vector_repo.search.return_value = [
            SearchResult(
                document_id=str(uuid4()),
                document_text="10mm carbide end mill",
                similarity_score=0.95,
                metadata={"name": "Test End Mill", "category": "milling"}
            )
        ]

        # 执行搜索
        query = SearchQuery(
            query_text="end mill",
            top_k=10,
            filters={"category": "milling", "compatible_materials": ["P"]}
        )
        results = await service.search(query)

        # 验证结果
        assert len(results) == 1
        mock_vector_repo.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_index_document(self, service, mock_vector_repo):
        """测试索引文档"""
        # 执行索引
        await service.index_document(
            document_id=str(uuid4()),
            text="10mm carbide end mill for steel",
            metadata={"name": "Test End Mill", "category": "milling"}
        )

        # 验证调用
        mock_vector_repo.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_document(self, service, mock_vector_repo):
        """测试更新文档"""
        document_id = str(uuid4())

        # 执行更新
        await service.update_document(
            document_id=document_id,
            text="Updated 10mm carbide end mill",
            metadata={"name": "Updated End Mill", "category": "milling"}
        )

        # 验证调用
        mock_vector_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_document(self, service, mock_vector_repo):
        """测试删除文档"""
        document_id = str(uuid4())

        # 执行删除
        await service.delete_document(document_id)

        # 验证调用
        mock_vector_repo.delete.assert_called_once_with(document_id)

    @pytest.mark.asyncio
    async def test_get_document(self, service, mock_vector_repo):
        """测试获取文档"""
        document_id = str(uuid4())
        expected_doc = {
            "id": document_id,
            "text": "Test content",
            "metadata": {"name": "Test"}
        }

        # 设置 mock 返回值
        mock_vector_repo.get.return_value = expected_doc

        # 执行获取
        result = await service.get_document(document_id)

        # 验证结果
        assert result == expected_doc
        mock_vector_repo.get.assert_called_once_with(document_id)

    @pytest.mark.asyncio
    async def test_get_document_not_found(self, service, mock_vector_repo):
        """测试获取不存在的文档"""
        document_id = str(uuid4())

        # 设置 mock 返回值
        mock_vector_repo.get.return_value = None

        # 执行获取
        result = await service.get_document(document_id)

        # 验证结果
        assert result is None
        mock_vector_repo.get.assert_called_once_with(document_id)
