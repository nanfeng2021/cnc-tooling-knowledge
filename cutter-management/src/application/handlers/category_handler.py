"""
Category Query Handler

分类查询处理器。
"""

from src.application.dto.category_dto import CategoryTreeDTO, SubcategoryDTO, VariantDTO
from src.domain.repositories.category_repo import CategoryRepository


class CategoryQueryHandler:
    """分类查询处理器"""

    def __init__(self, repository: CategoryRepository) -> None:
        self._repository = repository

    async def handle_get_category_tree(self) -> list[CategoryTreeDTO]:
        """获取分类树"""
        tree_data = await self._repository.get_category_tree()

        result = []
        for cat in tree_data:
            subcategories = []
            for sub in cat.get("subcategories", []):
                variants = []
                for v in sub.get("variants", []):
                    variants.append(VariantDTO(
                        variant=v["variant"],
                        variant_zh=v["variant_zh"],
                        variant_en=v["variant_en"],
                        id=v["variant"],
                        label_zh=v["variant_zh"],
                    ))
                subcategories.append(SubcategoryDTO(
                    subcategory=sub["subcategory"],
                    subcategory_zh=sub["subcategory_zh"],
                    subcategory_en=sub["subcategory_en"],
                    id=sub["subcategory"],
                    label_zh=sub["subcategory_zh"],
                    variants=variants,
                ))
            result.append(CategoryTreeDTO(
                category=cat["category"],
                category_zh=cat["category_zh"],
                category_en=cat["category_en"],
                icon=cat["icon"],
                id=cat["category"],
                label_zh=cat["category_zh"],
                subcategories=subcategories,
            ))

        return result
