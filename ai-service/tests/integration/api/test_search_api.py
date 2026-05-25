"""
AI Service API 集成测试

测试 FastAPI 端点的完整请求流程。
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient

from api.app import app


@pytest.fixture
def client() -> TestClient:
    """创建测试客户端"""
    return TestClient(app)


class TestSearchAPI:
    """搜索 API 测试"""

    @patch("api.routes.search.get_search_service")
    def test_search_success(self, mock_get_service, client):
        """测试成功搜索"""
        # 设置 mock
        mock_service = AsyncMock()
        mock_service.search.return_value = [
            MagicMock(
                document_id=str(uuid4()),
                score=0.95,
                metadata={"name": "Test End Mill", "category": "milling"}
            ),
            MagicMock(
                document_id=str(uuid4()),
                score=0.85,
                metadata={"name": "Another End Mill", "category": "milling"}
            )
        ]
        mock_get_service.return_value = mock_service

        # 发送请求
        response = client.post(
            "/api/v1/search",
            json={
                "query": "10mm end mill for steel",
                "limit": 10
            }
        )

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 2
        assert data["results"][0]["score"] > data["results"][1]["score"]

    @patch("api.routes.search.get_search_service")
    def test_search_with_filters(self, mock_get_service, client):
        """测试带过滤条件的搜索"""
        # 设置 mock
        mock_service = AsyncMock()
        mock_service.search.return_value = [
            MagicMock(
                document_id=str(uuid4()),
                score=0.95,
                metadata={"name": "Test End Mill", "category": "milling"}
            )
        ]
        mock_get_service.return_value = mock_service

        # 发送请求
        response = client.post(
            "/api/v1/search",
            json={
                "query": "end mill",
                "limit": 10,
                "filters": {
                    "category": "milling",
                    "compatible_materials": ["P"]
                }
            }
        )

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1

    @patch("api.routes.search.get_search_service")
    def test_search_empty_results(self, mock_get_service, client):
        """测试搜索无结果"""
        # 设置 mock
        mock_service = AsyncMock()
        mock_service.search.return_value = []
        mock_get_service.return_value = mock_service

        # 发送请求
        response = client.post(
            "/api/v1/search",
            json={
                "query": "nonexistent tool",
                "limit": 10
            }
        )

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 0

    @patch("api.routes.search.get_search_service")
    def test_search_validation_error(self, mock_get_service, client):
        """测试搜索验证错误"""
        # 发送请求（缺少必填字段）
        response = client.post(
            "/api/v1/search",
            json={
                "limit": 10  # 缺少 query
            }
        )

        # 验证响应
        assert response.status_code == 422  # FastAPI 验证错误


class TestRecommendationsAPI:
    """推荐 API 测试"""

    @patch("api.routes.recommendations.get_recommendation_service")
    def test_recommendations_success(self, mock_get_service, client):
        """测试成功推荐"""
        # 设置 mock
        mock_service = AsyncMock()
        mock_service.recommend.return_value = MagicMock(
            material="steel",
            operation="milling",
            recommendations=[
                MagicMock(
                    parameter="vc_steel",
                    min_value=150.0,
                    max_value=250.0,
                    recommended=180.0
                ),
                MagicMock(
                    parameter="fz_steel",
                    min_value=0.03,
                    max_value=0.08,
                    recommended=0.05
                )
            ]
        )
        mock_get_service.return_value = mock_service

        # 发送请求
        response = client.post(
            "/api/v1/recommendations",
            json={
                "material": "steel",
                "operation": "milling",
                "tool_type": "end_mill",
                "diameter": 10.0
            }
        )

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["material"] == "steel"
        assert data["operation"] == "milling"
        assert len(data["recommendations"]) == 2

    @patch("api.routes.recommendations.get_recommendation_service")
    def test_recommendations_no_results(self, mock_get_service, client):
        """测试无推荐结果"""
        # 设置 mock
        mock_service = AsyncMock()
        mock_service.recommend.return_value = MagicMock(
            material="unknown",
            operation="milling",
            recommendations=[]
        )
        mock_get_service.return_value = mock_service

        # 发送请求
        response = client.post(
            "/api/v1/recommendations",
            json={
                "material": "unknown",
                "operation": "milling",
                "tool_type": "end_mill",
                "diameter": 10.0
            }
        )

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert len(data["recommendations"]) == 0


class TestScenariosAPI:
    """场景匹配 API 测试"""

    @patch("api.routes.scenarios.get_scenario_service")
    def test_scenarios_success(self, mock_get_service, client):
        """测试成功场景匹配"""
        # 设置 mock
        mock_service = AsyncMock()
        mock_service.find_matches.return_value = [
            MagicMock(
                scenario_id=str(uuid4()),
                score=0.95,
                metadata={
                    "name": "Steel Milling",
                    "category": "milling",
                    "material": "steel"
                }
            ),
            MagicMock(
                scenario_id=str(uuid4()),
                score=0.85,
                metadata={
                    "name": "General Milling",
                    "category": "milling",
                    "material": "general"
                }
            )
        ]
        mock_get_service.return_value = mock_service

        # 发送请求
        response = client.post(
            "/api/v1/scenarios",
            json={
                "category": "milling",
                "subcategory": "milling_end_mill",
                "material": "steel",
                "diameter": 10.0
            }
        )

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert len(data["matches"]) == 2
        assert data["matches"][0]["score"] > data["matches"][1]["score"]

    @patch("api.routes.scenarios.get_scenario_service")
    def test_scenarios_no_matches(self, mock_get_service, client):
        """测试无匹配场景"""
        # 设置 mock
        mock_service = AsyncMock()
        mock_service.find_matches.return_value = []
        mock_get_service.return_value = mock_service

        # 发送请求
        response = client.post(
            "/api/v1/scenarios",
            json={
                "category": "unknown",
                "subcategory": "unknown",
                "material": "unknown",
                "diameter": 10.0
            }
        )

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert len(data["matches"]) == 0


class TestHealthAPI:
    """健康检查 API 测试"""

    def test_health_endpoint(self, client):
        """测试健康检查端点"""
        response = client.get("/health")

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ai-service"

    @patch("api.routes.health.get_embedding_model")
    @patch("api.routes.health.ChromaVectorRepository")
    def test_health_dependencies_endpoint(self, mock_repo_class, mock_get_model, client):
        """测试依赖健康检查端点"""
        # 设置 mock
        mock_model = MagicMock()
        mock_model.get_dimension.return_value = 384
        mock_get_model.return_value = mock_model

        mock_repo = AsyncMock()
        mock_repo.count.return_value = 100
        mock_repo_class.return_value = mock_repo

        # 发送请求
        response = client.get("/health/dependencies")

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "dependencies" in data
        assert data["dependencies"]["embedding_model"]["status"] == "healthy"
        assert data["dependencies"]["chromadb"]["status"] == "healthy"

    def test_metrics_endpoint(self, client):
        """测试Prometheus指标端点"""
        response = client.get("/metrics")

        # 验证响应
        assert response.status_code == 200
        # Prometheus 指标应该是文本格式
        assert "http_requests_total" in response.text or "python_info" in response.text
