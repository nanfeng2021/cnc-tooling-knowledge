"""
Recommendation Routes

参数推荐API端点。
"""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.recommendation.application.queries.get_recommendations import GetRecommendationsQuery
from src.recommendation.domain.services.recommendation_service import RecommendationService
from src.semantic_search.infrastructure.persistence.chroma_repo import ChromaVectorRepository

router = APIRouter()


class RecommendationRequest(BaseModel):
    """推荐请求"""
    workpiece_material: str = Field(..., description="工件材料（ISO代码或名称）")
    operation_type: str = Field(..., description="加工类型（milling/turning等）")
    target_diameter: float | None = Field(default=None, gt=0, description="目标直径mm")
    max_results: int = Field(default=5, ge=1, le=20, description="最大结果数")


class ParameterRangeItem(BaseModel):
    """参数范围"""
    min_value: float
    max_value: float
    avg_value: float
    unit: str = ""


class RecommendationResponse(BaseModel):
    """推荐响应"""
    workpiece_material: str
    iso_code: str
    operation_type: str
    parameters: dict[str, ParameterRangeItem] = {}
    source_documents: list[dict] = []
    target_diameter: float | None = None
    candidate_count: int = 0


@router.post("", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """获取切削参数推荐"""
    try:
        repo = ChromaVectorRepository()
        service = RecommendationService(repo)

        result = await service.recommend(
            workpiece_material=request.workpiece_material,
            operation_type=request.operation_type,
            target_diameter=request.target_diameter,
            max_results=request.max_results,
        )

        return RecommendationResponse(
            workpiece_material=result.workpiece_material,
            iso_code=result.iso_code,
            operation_type=result.operation_type,
            parameters={
                k: ParameterRangeItem(
                    min_value=v.min_value,
                    max_value=v.max_value,
                    avg_value=v.avg_value,
                    unit=v.unit,
                )
                for k, v in result.parameters.items()
            },
            source_documents=result.source_documents,
            target_diameter=result.target_diameter,
            candidate_count=result.candidate_count,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/parameters", response_model=RecommendationResponse)
async def get_parameters_get(
    workpiece_material: str,
    operation_type: str,
    target_diameter: Optional[float] = None,
    max_results: int = 5,
):
    """获取切削参数推荐（GET方法，兼容前端调用）"""
    try:
        repo = ChromaVectorRepository()
        service = RecommendationService(repo)

        result = await service.recommend(
            workpiece_material=workpiece_material,
            operation_type=operation_type,
            target_diameter=target_diameter,
            max_results=max_results,
        )

        return RecommendationResponse(
            workpiece_material=result.workpiece_material,
            iso_code=result.iso_code,
            operation_type=result.operation_type,
            parameters={
                k: ParameterRangeItem(
                    min_value=v.min_value,
                    max_value=v.max_value,
                    avg_value=v.avg_value,
                    unit=v.unit,
                )
                for k, v in result.parameters.items()
            },
            source_documents=result.source_documents,
            target_diameter=result.target_diameter,
            candidate_count=result.candidate_count,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
