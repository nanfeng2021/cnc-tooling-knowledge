"""
Cutter Routes

刀具CRUD API端点。
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from src.application.commands.create_cutter import CreateCutterCommand
from src.application.commands.update_cutter import UpdateCutterCommand
from src.application.commands.delete_cutter import DeleteCutterCommand
from src.application.dto.cutter_dto import CutterDTO, CutterListResponse
from src.application.handlers.cutter_handler import CutterCommandHandler, CutterQueryHandler
from src.application.queries.cutter_queries import FilterCuttersQuery, GetCutterByIdQuery
from src.domain.repositories.cutter_repo import CutterNotFoundError, DuplicateCutterError
from src.interface.api.dependencies import get_command_handler, get_query_handler

router = APIRouter()


class CreateCutterRequest(BaseModel):
    """创建刀具请求"""
    name: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., description="ISO major category")
    subcategory: str = ""
    variant: str | None = None
    substrate: str = "carbide"
    coating_type: str | None = None
    hardness_hrc: float | None = None
    iso_class: str | None = None
    material_grade: str | None = None
    diameter: float = Field(..., gt=0)
    length: float = Field(..., gt=0)
    flute_length: float = Field(default=0.0, ge=0)
    number_of_flutes: int = Field(default=4, ge=1)
    helix_angle: float = 30.0
    corner_radius: float = Field(default=0.0, ge=0)
    recommended_parameters: dict[str, float] = Field(default_factory=dict)
    usage_guidelines: str = ""
    compatible_materials: list[str] = Field(default_factory=list)
    manufacturer_id: str | None = None
    model_number: str | None = None
    image_url: str | None = None


class UpdateCutterRequest(BaseModel):
    """更新刀具请求"""
    name: str | None = None
    model_number: str | None = None
    image_url: str | None = None
    usage_guidelines: str | None = None
    recommended_parameters: dict[str, float] | None = None
    compatible_materials: list[str] | None = None


@router.post("", response_model=CutterDTO, status_code=201)
async def create_cutter(
    request: CreateCutterRequest,
    handler: CutterCommandHandler = Depends(get_command_handler),
):
    """创建新刀具"""
    try:
        manufacturer_id = None
        if request.manufacturer_id:
            try:
                manufacturer_id = UUID(request.manufacturer_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid manufacturer_id")

        command = CreateCutterCommand(
            name=request.name,
            category=request.category,
            subcategory=request.subcategory,
            variant=request.variant,
            substrate=request.substrate,
            coating_type=request.coating_type,
            hardness_hrc=request.hardness_hrc,
            iso_class=request.iso_class,
            material_grade=request.material_grade,
            diameter=request.diameter,
            length=request.length,
            flute_length=request.flute_length,
            number_of_flutes=request.number_of_flutes,
            helix_angle=request.helix_angle,
            corner_radius=request.corner_radius,
            recommended_parameters=request.recommended_parameters,
            usage_guidelines=request.usage_guidelines,
            compatible_materials=request.compatible_materials,
            manufacturer_id=manufacturer_id,
            model_number=request.model_number,
            image_url=request.image_url,
        )
        return await handler.handle_create(command)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DuplicateCutterError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("", response_model=CutterListResponse)
async def list_cutters(
    category: str | None = Query(None),
    subcategory: str | None = Query(None),
    variant: str | None = Query(None),
    manufacturer_id: str | None = Query(None),
    limit: int = Query(20, ge=1, le=500),
    offset: int = Query(0, ge=0),
    handler: CutterQueryHandler = Depends(get_query_handler),
):
    """列出刀具（支持过滤和分页）"""
    query = FilterCuttersQuery(
        category=category,
        subcategory=subcategory,
        variant=variant,
        manufacturer_id=manufacturer_id,
        limit=limit,
        offset=offset,
    )
    return await handler.handle_filter(query)


@router.get("/{cutter_id}", response_model=CutterDTO)
async def get_cutter(
    cutter_id: str,
    handler: CutterQueryHandler = Depends(get_query_handler),
):
    """获取单个刀具详情"""
    result = await handler.handle_get_by_id(GetCutterByIdQuery(cutter_id=cutter_id))
    if not result:
        raise HTTPException(status_code=404, detail="Cutter not found")
    return result


@router.put("/{cutter_id}", response_model=CutterDTO)
async def update_cutter(
    cutter_id: str,
    request: UpdateCutterRequest,
    handler: CutterCommandHandler = Depends(get_command_handler),
):
    """更新刀具"""
    try:
        command = UpdateCutterCommand(
            cutter_id=UUID(cutter_id),
            name=request.name,
            model_number=request.model_number,
            image_url=request.image_url,
            usage_guidelines=request.usage_guidelines,
            recommended_parameters=request.recommended_parameters,
            compatible_materials=request.compatible_materials,
        )
        return await handler.handle_update(command)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except CutterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{cutter_id}", status_code=204)
async def delete_cutter(
    cutter_id: str,
    handler: CutterCommandHandler = Depends(get_command_handler),
):
    """删除刀具"""
    try:
        command = DeleteCutterCommand(cutter_id=UUID(cutter_id))
        result = await handler.handle_delete(command)
        if not result:
            raise HTTPException(status_code=404, detail="Cutter not found")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid cutter_id")
