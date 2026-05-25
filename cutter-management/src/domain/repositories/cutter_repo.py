"""
Cutter Repository Interface

定义刀具聚合根的持久化接口，遵循DDD Repository模式。
"""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.models.cutter_aggregate import Cutter


class CutterRepository(ABC):
    """刀具仓库接口"""

    @abstractmethod
    async def add(self, cutter: Cutter) -> None:
        """添加新刀具"""
        ...

    @abstractmethod
    async def get_by_id(self, cutter_id: UUID) -> Cutter | None:
        """根据ID获取刀具"""
        ...

    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> list[Cutter]:
        """获取所有刀具（分页）"""
        ...

    @abstractmethod
    async def update(self, cutter: Cutter) -> None:
        """更新刀具"""
        ...

    @abstractmethod
    async def delete(self, cutter_id: UUID) -> bool:
        """删除刀具，返回是否成功"""
        ...

    @abstractmethod
    async def count(self) -> int:
        """获取刀具总数"""
        ...

    @abstractmethod
    async def get_filtered(
        self,
        category: str | None = None,
        subcategory: str | None = None,
        variant: str | None = None,
        manufacturer_id: UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Cutter], int]:
        """按条件过滤刀具，返回(items, total)"""
        ...


class Manufacturer:
    """制造商聚合根（简化版）"""

    def __init__(self, id: UUID, name: str, country: str = "", website: str = "") -> None:
        self.id = id
        self.name = name
        self.country = country
        self.website = website


class ManufacturerRepository(ABC):
    """制造商仓库接口"""

    @abstractmethod
    async def add(self, manufacturer: Manufacturer) -> None:
        ...

    @abstractmethod
    async def get_by_id(self, manufacturer_id: UUID) -> Manufacturer | None:
        ...

    @abstractmethod
    async def get_all(self) -> list[Manufacturer]:
        ...


class CutterNotFoundError(Exception):
    """刀具未找到异常"""
    pass


class DuplicateCutterError(Exception):
    """刀具重复异常"""
    pass
