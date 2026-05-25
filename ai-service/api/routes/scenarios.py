"""
Scenario Matching Routes

场景匹配API端点。
"""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.scenario_matching.application.queries.match_scenario import MatchScenarioQuery
from src.scenario_matching.domain.models.machining_scenario import MachiningScenario
from src.scenario_matching.domain.services.scenario_service import ScenarioMatchingService
from src.semantic_search.infrastructure.persistence.chroma_repo import ChromaVectorRepository

router = APIRouter()


class ScenarioMatchRequest(BaseModel):
    """场景匹配请求"""
    category: str = Field(..., description="加工类别（milling/turning等）")
    material_iso_code: str = Field(..., description="材料ISO代码（P/M/K/N/S/H）")
    subcategory: Optional[str] = Field(default=None, description="子类别")
    variant: Optional[str] = Field(default=None, description="变体")
    target_diameter: Optional[float] = Field(default=None, gt=0, description="目标直径mm")
    manufacturer_id: Optional[str] = Field(default=None, description="制造商ID")
    top_k: int = Field(default=10, ge=1, le=50, description="返回结果数量")
    min_score: float = Field(default=0.0, ge=0, le=1, description="最低匹配分数")


class ScoreBreakdown(BaseModel):
    """分数细分"""
    category: float = 0.0
    material: float = 0.0
    subcategory: float = 0.0
    variant: float = 0.0
    diameter: float = 0.0
    parameters: float = 0.0


class ScenarioMatchItem(BaseModel):
    """场景匹配结果项"""
    document_id: str
    score: float
    score_breakdown: ScoreBreakdown
    metadata: dict = {}


class ScenarioMatchResponse(BaseModel):
    """场景匹配响应"""
    items: list[ScenarioMatchItem]
    total: int


@router.post("", response_model=ScenarioMatchResponse)
async def match_scenario(request: ScenarioMatchRequest):
    """执行场景匹配"""
    try:
        repo = ChromaVectorRepository()
        service = ScenarioMatchingService(repo)

        scenario = MachiningScenario(
            category=request.category,
            material_iso_code=request.material_iso_code,
            subcategory=request.subcategory,
            variant=request.variant,
            target_diameter=request.target_diameter,
            manufacturer_id=request.manufacturer_id,
        )

        results = await service.find_matches(
            scenario=scenario,
            top_k=request.top_k,
            min_score=request.min_score,
        )

        return ScenarioMatchResponse(
            items=[
                ScenarioMatchItem(
                    document_id=r.document_id,
                    score=r.score,
                    score_breakdown=ScoreBreakdown(**r.score_breakdown),
                    metadata=r.metadata,
                )
                for r in results
            ],
            total=len(results),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/match", response_model=ScenarioMatchResponse)
async def match_scenario_alias(request: ScenarioMatchRequest):
    """执行场景匹配（别名端点，兼容前端调用）"""
    return await match_scenario(request)
