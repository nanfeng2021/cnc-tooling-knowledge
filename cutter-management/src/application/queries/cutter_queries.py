"""
Cutter Queries

CQRS查询对象。
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class GetCutterByIdQuery:
    """根据ID获取刀具"""
    cutter_id: str


@dataclass(frozen=True)
class ListCuttersQuery:
    """列出刀具（分页）"""
    limit: int = 20
    offset: int = 0


@dataclass(frozen=True)
class FilterCuttersQuery:
    """按条件过滤刀具"""
    category: str | None = None
    subcategory: str | None = None
    variant: str | None = None
    manufacturer_id: str | None = None
    limit: int = 20
    offset: int = 0
