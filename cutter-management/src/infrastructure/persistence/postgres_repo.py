"""
PostgreSQL Repository Implementation

实现CutterRepository接口，使用SQLAlchemy异步ORM。
"""

from uuid import UUID

from sqlalchemy import func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.cutter_aggregate import Cutter
from src.domain.repositories.cutter_repo import (
    CutterNotFoundError,
    CutterRepository,
    DuplicateCutterError,
)
from src.infrastructure.persistence.models import CutterModel


class PostgresCutterRepository(CutterRepository):
    """PostgreSQL异步刀具仓库"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, cutter: Cutter) -> None:
        """添加新刀具"""
        # 检查是否已存在
        existing = await self._session.get(CutterModel, cutter.id)
        if existing:
            raise DuplicateCutterError(f"Cutter {cutter.id} already exists")

        model = CutterModel.from_domain(cutter)
        self._session.add(model)
        await self._session.flush()

    async def get_by_id(self, cutter_id: UUID) -> Cutter | None:
        """根据ID获取刀具"""
        model = await self._session.get(CutterModel, cutter_id)
        if not model:
            return None
        return model.to_domain()

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[Cutter]:
        """获取所有刀具"""
        stmt = (
            select(CutterModel)
            .order_by(CutterModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [m.to_domain() for m in models]

    async def update(self, cutter: Cutter) -> None:
        """更新刀具"""
        model = await self._session.get(CutterModel, cutter.id)
        if not model:
            raise CutterNotFoundError(f"Cutter {cutter.id} not found")

        # 更新字段
        model.name = cutter.name
        model.model_number = cutter.model_number
        model.image_url = cutter.image_url
        model.category = cutter.cutter_type.category
        model.subcategory = cutter.cutter_type.subcategory
        model.variant = cutter.cutter_type.variant
        model.substrate = cutter.material.substrate
        model.coating_type = cutter.material.coating_type
        model.hardness_hrc = cutter.material.hardness_hrc
        model.iso_class = cutter.material.iso_class
        model.material_grade = cutter.material.material_grade
        model.diameter = cutter.geometry.diameter
        model.length = cutter.geometry.length
        model.flute_length = cutter.geometry.flute_length
        model.number_of_flutes = cutter.geometry.number_of_flutes
        model.helix_angle = cutter.geometry.helix_angle
        model.corner_radius = cutter.geometry.corner_radius
        model.recommended_parameters = cutter.recommended_parameters
        model.usage_guidelines = cutter.usage_guidelines
        model.compatible_materials = cutter.compatible_materials
        model.manufacturer_id = cutter.manufacturer_id

        await self._session.flush()

    async def delete(self, cutter_id: UUID) -> bool:
        """删除刀具"""
        model = await self._session.get(CutterModel, cutter_id)
        if not model:
            return False

        await self._session.delete(model)
        await self._session.flush()
        return True

    async def count(self) -> int:
        """获取刀具总数"""
        stmt = select(func.count()).select_from(CutterModel)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def get_filtered(
        self,
        category: str | None = None,
        subcategory: str | None = None,
        variant: str | None = None,
        manufacturer_id: UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Cutter], int]:
        """按条件过滤刀具"""
        # 构建基础查询
        base_query = select(CutterModel)

        # 应用过滤条件
        if category:
            base_query = base_query.where(CutterModel.category == category)
        if subcategory:
            base_query = base_query.where(CutterModel.subcategory == subcategory)
        if variant:
            base_query = base_query.where(CutterModel.variant == variant)
        if manufacturer_id:
            base_query = base_query.where(CutterModel.manufacturer_id == manufacturer_id)

        # 获取总数
        count_stmt = select(func.count()).select_from(base_query.subquery())
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        # 获取分页数据
        stmt = (
            base_query
            .order_by(CutterModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [m.to_domain() for m in models], total
