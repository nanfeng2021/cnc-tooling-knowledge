"""
Recommendation Service 单元测试

测试推荐服务的业务逻辑。
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.recommendation.domain.services.recommendation_service import RecommendationService
from src.recommendation.domain.models.recommendation import ParameterRange, RecommendationResult


class TestRecommendationService:
    """RecommendationService 测试"""

    @pytest.fixture
    def mock_vector_repo(self) -> AsyncMock:
        """模拟向量仓库"""
        repo = AsyncMock()
        repo.search = AsyncMock()
        return repo

    @pytest.fixture
    def service(self, mock_vector_repo) -> RecommendationService:
        """创建推荐服务实例"""
        return RecommendationService(vector_repo=mock_vector_repo)

    @pytest.mark.asyncio
    async def test_recommend_for_steel_milling(self, service, mock_vector_repo):
        """测试为钢材料铣削推荐参数"""
        # 设置 mock 返回值
        mock_vector_repo.search.return_value = [
            MagicMock(
                document_id="doc-1",
                similarity_score=0.95,
                metadata={
                    "name": "End Mill 10mm",
                    "category": "milling",
                    "recommended_parameters": {
                        "vc_steel": 180.0,
                        "fz_steel": 0.05,
                        "ap_max": 18.0,
                        "ae_max": 10.0
                    }
                }
            ),
            MagicMock(
                document_id="doc-2",
                similarity_score=0.90,
                metadata={
                    "name": "End Mill 12mm",
                    "category": "milling",
                    "recommended_parameters": {
                        "vc_steel": 200.0,
                        "fz_steel": 0.06,
                        "ap_max": 20.0,
                        "ae_max": 12.0
                    }
                }
            )
        ]

        # 执行推荐
        result = await service.recommend(
            workpiece_material="steel",
            operation_type="milling",
            target_diameter=10.0
        )

        # 验证结果
        assert isinstance(result, RecommendationResult)
        assert result.workpiece_material == "steel"
        assert result.operation_type == "milling"
        assert len(result.parameters) > 0

    @pytest.mark.asyncio
    async def test_recommend_for_aluminum(self, service, mock_vector_repo):
        """测试为铝合金推荐参数"""
        # 设置 mock 返回值
        mock_vector_repo.search.return_value = [
            MagicMock(
                document_id="doc-1",
                similarity_score=0.95,
                metadata={
                    "name": "End Mill 10mm",
                    "category": "milling",
                    "recommended_parameters": {
                        "vc_aluminum": 400.0,
                        "fz_aluminum": 0.08,
                        "ap_max": 15.0,
                        "ae_max": 8.0
                    }
                }
            )
        ]

        # 执行推荐
        result = await service.recommend(
            workpiece_material="aluminum",
            operation_type="milling",
            target_diameter=10.0
        )

        # 验证结果
        assert isinstance(result, RecommendationResult)
        assert result.workpiece_material == "aluminum"
        assert len(result.parameters) > 0

    @pytest.mark.asyncio
    async def test_recommend_with_no_results(self, service, mock_vector_repo):
        """测试没有推荐结果的情况"""
        # 设置 mock 返回空列表
        mock_vector_repo.search.return_value = []

        # 执行推荐 - 使用有效材料但无搜索结果
        result = await service.recommend(
            workpiece_material="steel",
            operation_type="milling",
            target_diameter=10.0
        )

        # 验证结果
        assert isinstance(result, RecommendationResult)
        assert len(result.parameters) == 0

    @pytest.mark.asyncio
    async def test_recommend_aggregates_parameters(self, service, mock_vector_repo):
        """测试参数聚合逻辑"""
        # 设置 mock 返回多个结果
        mock_vector_repo.search.return_value = [
            MagicMock(
                document_id="doc-1",
                similarity_score=0.95,
                metadata={
                    "name": "End Mill 1",
                    "recommended_parameters": {
                        "vc_steel": 180.0,
                        "fz_steel": 0.05,
                        "ap_max": 15.0,
                        "ae_max": 8.0
                    }
                }
            ),
            MagicMock(
                document_id="doc-2",
                similarity_score=0.90,
                metadata={
                    "name": "End Mill 2",
                    "recommended_parameters": {
                        "vc_steel": 200.0,
                        "fz_steel": 0.06,
                        "ap_max": 18.0,
                        "ae_max": 10.0
                    }
                }
            ),
            MagicMock(
                document_id="doc-3",
                similarity_score=0.85,
                metadata={
                    "name": "End Mill 3",
                    "recommended_parameters": {
                        "vc_steel": 220.0,
                        "fz_steel": 0.07,
                        "ap_max": 20.0,
                        "ae_max": 12.0
                    }
                }
            )
        ]

        # 执行推荐
        result = await service.recommend(
            workpiece_material="steel",
            operation_type="milling",
            target_diameter=10.0
        )

        # 验证参数聚合
        assert len(result.parameters) > 0
        # 应该包含聚合后的参数范围
        assert "vc_steel" in result.parameters
        assert "fz_steel" in result.parameters
        for key, param_range in result.parameters.items():
            assert isinstance(param_range, ParameterRange)
            assert param_range.min_value <= param_range.max_value

    @pytest.mark.asyncio
    async def test_recommend_includes_parameter_ranges(self, service, mock_vector_repo):
        """测试推荐结果包含参数范围"""
        # 设置 mock 返回值
        mock_vector_repo.search.return_value = [
            MagicMock(
                document_id="doc-1",
                similarity_score=0.95,
                metadata={
                    "name": "End Mill 10mm",
                    "recommended_parameters": {
                        "vc_steel": 180.0,
                        "fz_steel": 0.05,
                        "ap_max": 18.0,
                        "ae_max": 10.0
                    }
                }
            )
        ]

        # 执行推荐
        result = await service.recommend(
            workpiece_material="steel",
            operation_type="milling",
            target_diameter=10.0
        )

        # 验证参数范围
        assert len(result.parameters) > 0
        for key, param_range in result.parameters.items():
            assert isinstance(param_range, ParameterRange)
            assert param_range.min_value <= param_range.max_value
