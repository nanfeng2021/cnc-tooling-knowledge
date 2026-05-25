"""
Category Aggregate

分类聚合根。
支持树形结构：category -> subcategory -> variant
"""

from uuid import UUID, uuid4
from dataclasses import dataclass, field


@dataclass
class Variant:
    """变体值对象"""
    variant: str
    variant_zh: str
    variant_en: str
    description: str = ""

    @property
    def id(self) -> str:
        return self.variant

    @property
    def label_zh(self) -> str:
        return self.variant_zh


@dataclass
class Subcategory:
    """子分类值对象"""
    subcategory: str
    subcategory_zh: str
    subcategory_en: str
    variants: list[Variant] = field(default_factory=list)

    @property
    def id(self) -> str:
        return self.subcategory

    @property
    def label_zh(self) -> str:
        return self.subcategory_zh


class Category:
    """分类聚合根"""

    def __init__(
        self,
        name: str,
        name_zh: str = "",
        name_en: str = "",
        icon: str = "",
        parent_id: UUID | None = None,
        level: int = 1,
        id: UUID | None = None,
    ) -> None:
        self.id = id or uuid4()
        self.name = name
        self.name_zh = name_zh
        self.name_en = name_en
        self.icon = icon
        self.parent_id = parent_id
        self.level = level
        self._subcategories: list[Subcategory] = []

    def __repr__(self) -> str:
        return f"Category(id={self.id}, name={self.name!r}, level={self.level})"

    @property
    def category(self) -> str:
        """返回分类标识符（用于前端兼容）"""
        return self.name

    @property
    def category_zh(self) -> str:
        """返回中文名称（用于前端兼容）"""
        return self.name_zh

    @property
    def category_en(self) -> str:
        """返回英文名称（用于前端兼容）"""
        return self.name_en

    def add_subcategory(self, subcategory: Subcategory) -> None:
        """添加子分类"""
        self._subcategories.append(subcategory)

    @property
    def subcategories(self) -> list[Subcategory]:
        """获取子分类列表"""
        return self._subcategories

    def to_tree_dict(self) -> dict:
        """转换为树形字典结构（用于API响应）"""
        return {
            "category": self.name,
            "category_zh": self.name_zh,
            "category_en": self.name_en,
            "icon": self.icon,
            "id": self.name,
            "label_zh": self.name_zh,
            "subcategories": [
                {
                    "subcategory": sub.subcategory,
                    "subcategory_zh": sub.subcategory_zh,
                    "subcategory_en": sub.subcategory_en,
                    "id": sub.subcategory,
                    "label_zh": sub.subcategory_zh,
                    "variants": [
                        {
                            "variant": v.variant,
                            "variant_zh": v.variant_zh,
                            "variant_en": v.variant_en,
                            "id": v.variant,
                            "label_zh": v.variant_zh,
                        }
                        for v in sub.variants
                    ]
                }
                for sub in self._subcategories
            ]
        }
