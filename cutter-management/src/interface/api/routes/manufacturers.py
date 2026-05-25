"""
Manufacturer Routes

制造商管理API端点。
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_manufacturers():
    """列出所有制造商"""
    # TODO: 实现制造商查询
    return {"items": [], "total": 0}


@router.get("/{manufacturer_id}")
async def get_manufacturer(manufacturer_id: str):
    """获取制造商详情"""
    # TODO: 实现制造商查询
    return {"id": manufacturer_id, "name": "TODO"}
