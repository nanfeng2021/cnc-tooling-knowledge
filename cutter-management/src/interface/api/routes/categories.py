"""
Category Routes

分类管理API端点。
"""

from fastapi import APIRouter, Depends

from src.application.dto.category_dto import CategoryTreeDTO
from src.application.handlers.category_handler import CategoryQueryHandler
from src.interface.api.dependencies import get_category_query_handler

router = APIRouter()


@router.get("", response_model=list[CategoryTreeDTO])
async def list_categories(
    handler: CategoryQueryHandler = Depends(get_category_query_handler),
):
    """获取分类树结构

    返回完整的刀具分类树，包含三级结构:
    - category: 主分类（如车削、铣削、孔加工等）
    - subcategory: 子分类（如立铣刀、面铣刀等）
    - variant: 变体（如方肩、球头等）
    """
    return await handler.handle_get_category_tree()
