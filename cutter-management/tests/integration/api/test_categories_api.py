"""
Categories API 集成测试

测试分类 API 端点的完整请求流程。
"""

import pytest
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from src.interface.api.app import app
from src.interface.api.dependencies import get_category_query_handler


@pytest.fixture
def client() -> TestClient:
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
def sample_categories_response():
    """示例分类响应数据"""
    return [
        {
            "category": "turning",
            "category_zh": "车削刀具",
            "category_en": "Turning",
            "icon": "RotateCcw",
            "id": "turning",
            "label_zh": "车削刀具",
            "subcategories": [
                {
                    "subcategory": "turning_external",
                    "subcategory_zh": "外圆车刀",
                    "subcategory_en": "External Turning",
                    "id": "turning_external",
                    "label_zh": "外圆车刀",
                    "variants": [
                        {
                            "variant": "roughing",
                            "variant_zh": "粗车外圆刀",
                            "variant_en": "Roughing",
                            "id": "roughing",
                            "label_zh": "粗车外圆刀"
                        }
                    ]
                }
            ]
        }
    ]


class TestCategoriesAPI:
    """分类 API 测试"""

    def test_list_categories_success(self, client, sample_categories_response):
        """测试获取分类列表成功"""
        # 设置 mock
        mock_handler = AsyncMock()
        mock_handler.handle_get_category_tree.return_value = sample_categories_response

        # 使用依赖覆盖
        app.dependency_overrides[get_category_query_handler] = lambda: mock_handler

        try:
            # 发送请求
            response = client.get("/api/v1/categories")

            # 验证响应
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]["category"] == "turning"
            assert data[0]["category_zh"] == "车削刀具"
        finally:
            # 清理依赖覆盖
            app.dependency_overrides.clear()

    def test_list_categories_empty(self, client):
        """测试获取空分类列表"""
        # 设置 mock
        mock_handler = AsyncMock()
        mock_handler.handle_get_category_tree.return_value = []

        # 使用依赖覆盖
        app.dependency_overrides[get_category_query_handler] = lambda: mock_handler

        try:
            # 发送请求
            response = client.get("/api/v1/categories")

            # 验证响应
            assert response.status_code == 200
            data = response.json()
            assert data == []
        finally:
            # 清理依赖覆盖
            app.dependency_overrides.clear()

    def test_list_categories_with_subcategories(self, client, sample_categories_response):
        """测试分类列表包含子分类"""
        # 设置 mock
        mock_handler = AsyncMock()
        mock_handler.handle_get_category_tree.return_value = sample_categories_response

        # 使用依赖覆盖
        app.dependency_overrides[get_category_query_handler] = lambda: mock_handler

        try:
            # 发送请求
            response = client.get("/api/v1/categories")

            # 验证响应
            assert response.status_code == 200
            data = response.json()
            category = data[0]
            assert "subcategories" in category
            assert len(category["subcategories"]) == 1
            subcategory = category["subcategories"][0]
            assert subcategory["subcategory"] == "turning_external"
            assert "variants" in subcategory
            assert len(subcategory["variants"]) == 1
        finally:
            # 清理依赖覆盖
            app.dependency_overrides.clear()

    def test_list_categories_has_required_fields(self, client, sample_categories_response):
        """测试分类响应包含必要字段"""
        # 设置 mock
        mock_handler = AsyncMock()
        mock_handler.handle_get_category_tree.return_value = sample_categories_response

        # 使用依赖覆盖
        app.dependency_overrides[get_category_query_handler] = lambda: mock_handler

        try:
            # 发送请求
            response = client.get("/api/v1/categories")

            # 验证响应
            assert response.status_code == 200
            data = response.json()
            category = data[0]

            # 必须包含的字段
            required_fields = ["category", "category_zh", "category_en", "icon", "subcategories", "id", "label_zh"]
            for field in required_fields:
                assert field in category, f"Missing field: {field}"
        finally:
            # 清理依赖覆盖
            app.dependency_overrides.clear()
