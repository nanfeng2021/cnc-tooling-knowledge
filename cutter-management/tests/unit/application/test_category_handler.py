"""
Category Query Handler 单元测试

测试分类查询处理器的业务逻辑。
"""

import pytest
from unittest.mock import AsyncMock

from src.application.handlers.category_handler import CategoryQueryHandler
from src.application.dto.category_dto import CategoryTreeDTO, SubcategoryDTO, VariantDTO


class TestCategoryQueryHandler:
    """CategoryQueryHandler 测试"""

    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        """模拟分类仓库"""
        repo = AsyncMock()
        return repo

    @pytest.fixture
    def handler(self, mock_repository) -> CategoryQueryHandler:
        """创建查询处理器实例"""
        return CategoryQueryHandler(repository=mock_repository)

    @pytest.fixture
    def sample_category_tree(self):
        """示例分类树数据"""
        return [
            {
                "category": "turning",
                "category_zh": "车削刀具",
                "category_en": "Turning",
                "icon": "RotateCcw",
                "subcategories": [
                    {
                        "subcategory": "turning_external",
                        "subcategory_zh": "外圆车刀",
                        "subcategory_en": "External Turning",
                        "variants": [
                            {"variant": "roughing", "variant_zh": "粗车外圆刀", "variant_en": "Roughing"},
                            {"variant": "finishing", "variant_zh": "精车外圆刀", "variant_en": "Finishing"},
                        ]
                    }
                ]
            }
        ]

    @pytest.mark.asyncio
    async def test_get_category_tree_returns_normalized_data(self, handler, mock_repository, sample_category_tree):
        """测试获取分类树返回标准化数据"""
        mock_repository.get_category_tree.return_value = sample_category_tree

        result = await handler.handle_get_category_tree()

        assert len(result) == 1
        assert result[0].category == "turning"
        assert result[0].category_zh == "车削刀具"
        assert result[0].id == "turning"
        assert result[0].label_zh == "车削刀具"
        assert len(result[0].subcategories) == 1
        assert result[0].subcategories[0].id == "turning_external"
        assert result[0].subcategories[0].label_zh == "外圆车刀"
        assert len(result[0].subcategories[0].variants) == 2
        assert result[0].subcategories[0].variants[0].id == "roughing"

    @pytest.mark.asyncio
    async def test_get_category_tree_returns_empty_list(self, handler, mock_repository):
        """测试获取空分类树"""
        mock_repository.get_category_tree.return_value = []

        result = await handler.handle_get_category_tree()

        assert result == []
        mock_repository.get_category_tree.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_category_tree_calls_repository(self, handler, mock_repository, sample_category_tree):
        """测试查询处理器正确调用仓库"""
        mock_repository.get_category_tree.return_value = sample_category_tree

        await handler.handle_get_category_tree()

        mock_repository.get_category_tree.assert_called_once()
