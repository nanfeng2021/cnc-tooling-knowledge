"""
Cutter API 集成测试

测试 FastAPI 端点的完整请求流程。
"""

import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient

from src.interface.api.app import app
from src.domain.models.cutter_aggregate import Cutter, CutterType, MaterialSpec, GeometryParams


@pytest.fixture
def client() -> TestClient:
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
def sample_cutter() -> Cutter:
    """创建示例刀具"""
    return Cutter.create(
        name="Test End Mill",
        cutter_type=CutterType(category="milling", subcategory="milling_end_mill", variant="square"),
        material=MaterialSpec(substrate="carbide_K20", coating_type="TiAlN"),
        geometry=GeometryParams(
            diameter=10.0,
            length=75.0,
            flute_length=30.0,
            number_of_flutes=4
        ),
        compatible_materials=["P", "K"]
    )


class TestCuttersAPI:
    """刀具 API 测试"""

    @patch("src.interface.api.routes.cutters.get_cutter_handler")
    def test_create_cutter(self, mock_get_handler, client):
        """测试创建刀具端点"""
        # 设置 mock
        mock_handler = AsyncMock()
        mock_handler.handle_create.return_value = {
            "id": str(uuid4()),
            "name": "New End Mill",
            "category": "milling",
            "subcategory": "milling_end_mill",
            "variant": "square",
            "substrate": "carbide",
            "coating_type": "TiAlN",
            "diameter": 10.0,
            "length": 75.0,
            "flute_length": 30.0,
            "number_of_flutes": 4,
            "compatible_materials": ["P", "K"],
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }
        mock_get_handler.return_value = mock_handler

        # 发送请求
        response = client.post(
            "/api/v1/cutters",
            json={
                "name": "New End Mill",
                "category": "milling",
                "subcategory": "milling_end_mill",
                "variant": "square",
                "substrate": "carbide",
                "coating_type": "TiAlN",
                "diameter": 10.0,
                "length": 75.0,
                "flute_length": 30.0,
                "number_of_flutes": 4,
                "compatible_materials": ["P", "K"]
            }
        )

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New End Mill"
        assert data["category"] == "milling"

    @patch("src.interface.api.routes.cutters.get_cutter_handler")
    def test_create_cutter_validation_error(self, mock_get_handler, client):
        """测试创建刀具时验证失败"""
        # 设置 mock
        mock_handler = AsyncMock()
        mock_handler.handle_create.side_effect = ValueError("Validation failed: Name is required")
        mock_get_handler.return_value = mock_handler

        # 发送请求
        response = client.post(
            "/api/v1/cutters",
            json={
                "name": "",  # 空名称
                "category": "milling",
                "substrate": "carbide",
                "diameter": 10.0,
                "length": 75.0,
                "flute_length": 30.0,
                "number_of_flutes": 4
            }
        )

        # 验证响应
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    @patch("src.interface.api.routes.cutters.get_cutter_query_handler")
    def test_get_cutter_by_id(self, mock_get_handler, client, sample_cutter):
        """测试根据ID获取刀具"""
        # 设置 mock
        mock_handler = AsyncMock()
        mock_handler.handle_get_by_id.return_value = {
            "id": str(sample_cutter.id),
            "name": sample_cutter.name,
            "category": sample_cutter.cutter_type.category,
            "subcategory": sample_cutter.cutter_type.subcategory,
            "variant": sample_cutter.cutter_type.variant,
            "substrate": sample_cutter.material.substrate,
            "coating_type": sample_cutter.material.coating_type,
            "diameter": sample_cutter.geometry.diameter,
            "length": sample_cutter.geometry.length,
            "flute_length": sample_cutter.geometry.flute_length,
            "number_of_flutes": sample_cutter.geometry.number_of_flutes,
            "compatible_materials": sample_cutter.compatible_materials,
            "created_at": sample_cutter.created_at.isoformat(),
            "updated_at": sample_cutter.updated_at.isoformat()
        }
        mock_get_handler.return_value = mock_handler

        # 发送请求
        response = client.get(f"/api/v1/cutters/{sample_cutter.id}")

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test End Mill"
        assert data["id"] == str(sample_cutter.id)

    @patch("src.interface.api.routes.cutters.get_cutter_query_handler")
    def test_get_cutter_not_found(self, mock_get_handler, client):
        """测试获取不存在的刀具"""
        # 设置 mock
        mock_handler = AsyncMock()
        mock_handler.handle_get_by_id.return_value = None
        mock_get_handler.return_value = mock_handler

        # 发送请求
        cutter_id = uuid4()
        response = client.get(f"/api/v1/cutters/{cutter_id}")

        # 验证响应
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    @patch("src.interface.api.routes.cutters.get_cutter_query_handler")
    def test_list_cutters(self, mock_get_handler, client, sample_cutter):
        """测试列出刀具"""
        # 设置 mock
        mock_handler = AsyncMock()
        mock_handler.handle_list.return_value = {
            "items": [
                {
                    "id": str(sample_cutter.id),
                    "name": sample_cutter.name,
                    "category": sample_cutter.cutter_type.category,
                    "subcategory": sample_cutter.cutter_type.subcategory,
                    "variant": sample_cutter.cutter_type.variant,
                    "substrate": sample_cutter.material.substrate,
                    "coating_type": sample_cutter.material.coating_type,
                    "diameter": sample_cutter.geometry.diameter,
                    "length": sample_cutter.geometry.length,
                    "flute_length": sample_cutter.geometry.flute_length,
                    "number_of_flutes": sample_cutter.geometry.number_of_flutes,
                    "compatible_materials": sample_cutter.compatible_materials,
                    "created_at": sample_cutter.created_at.isoformat(),
                    "updated_at": sample_cutter.updated_at.isoformat()
                }
            ],
            "total": 1,
            "limit": 10,
            "offset": 0
        }
        mock_get_handler.return_value = mock_handler

        # 发送请求
        response = client.get("/api/v1/cutters")

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 1
        assert data["total"] == 1

    @patch("src.interface.api.routes.cutters.get_cutter_handler")
    def test_update_cutter(self, mock_get_handler, client, sample_cutter):
        """测试更新刀具"""
        # 设置 mock
        mock_handler = AsyncMock()
        mock_handler.handle_update.return_value = {
            "id": str(sample_cutter.id),
            "name": "Updated End Mill",
            "category": sample_cutter.cutter_type.category,
            "subcategory": sample_cutter.cutter_type.subcategory,
            "variant": sample_cutter.cutter_type.variant,
            "substrate": sample_cutter.material.substrate,
            "coating_type": sample_cutter.material.coating_type,
            "diameter": sample_cutter.geometry.diameter,
            "length": sample_cutter.geometry.length,
            "flute_length": sample_cutter.geometry.flute_length,
            "number_of_flutes": sample_cutter.geometry.number_of_flutes,
            "compatible_materials": sample_cutter.compatible_materials,
            "created_at": sample_cutter.created_at.isoformat(),
            "updated_at": "2024-01-02T00:00:00"
        }
        mock_get_handler.return_value = mock_handler

        # 发送请求
        response = client.put(
            f"/api/v1/cutters/{sample_cutter.id}",
            json={"name": "Updated End Mill"}
        )

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated End Mill"

    @patch("src.interface.api.routes.cutters.get_cutter_handler")
    def test_delete_cutter(self, mock_get_handler, client, sample_cutter):
        """测试删除刀具"""
        # 设置 mock
        mock_handler = AsyncMock()
        mock_handler.handle_delete.return_value = True
        mock_get_handler.return_value = mock_handler

        # 发送请求
        response = client.delete(f"/api/v1/cutters/{sample_cutter.id}")

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @patch("src.interface.api.routes.cutters.get_cutter_handler")
    def test_delete_cutter_not_found(self, mock_get_handler, client):
        """测试删除不存在的刀具"""
        # 设置 mock
        mock_handler = AsyncMock()
        mock_handler.handle_delete.return_value = False
        mock_get_handler.return_value = mock_handler

        # 发送请求
        cutter_id = uuid4()
        response = client.delete(f"/api/v1/cutters/{cutter_id}")

        # 验证响应
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_health_check(self, client):
        """测试健康检查端点"""
        response = client.get("/health")

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "cutter-management"
