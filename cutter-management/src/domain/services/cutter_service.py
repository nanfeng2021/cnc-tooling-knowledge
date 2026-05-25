"""
Cutter Domain Service

封装不属于单个聚合根的业务逻辑。
"""

from uuid import UUID

from src.domain.models.cutter_aggregate import Cutter
from src.domain.repositories.cutter_repo import CutterRepository


class CutterDomainService:
    """刀具领域服务，处理跨聚合的业务规则"""

    def __init__(self, repository: CutterRepository) -> None:
        self._repository = repository

    async def validate_unique_name(self, name: str, exclude_id: UUID | None = None) -> bool:
        """验证刀具名称是否唯一"""
        all_cutters = await self._repository.get_all(limit=10000)
        for cutter in all_cutters:
            if cutter.name == name and cutter.id != exclude_id:
                return False
        return True

    async def get_compatible_cutters(self, material: str, limit: int = 10) -> list[Cutter]:
        """获取与指定材料兼容的刀具列表"""
        all_cutters = await self._repository.get_all(limit=10000)
        compatible = [
            c for c in all_cutters
            if material.lower() in [m.lower() for m in c.compatible_materials]
        ]
        return compatible[:limit]
