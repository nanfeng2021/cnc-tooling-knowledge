"""
Category Repository Interface

定义分类聚合根的持久化接口，遵循DDD Repository模式。
"""

from abc import ABC, abstractmethod


class CategoryRepository(ABC):
    """分类仓库接口"""

    @abstractmethod
    async def get_category_tree(self) -> list[dict]:
        """获取完整的分类树结构

        Returns:
            list[dict]: 分类树列表，每个元素包含:
                - category: 分类标识符
                - category_zh: 中文名称
                - category_en: 英文名称
                - icon: 图标名称
                - subcategories: 子分类列表
        """
        ...
