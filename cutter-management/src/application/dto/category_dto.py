"""
Category DTO

分类数据传输对象，用于API响应。
"""

from pydantic import BaseModel


class VariantDTO(BaseModel):
    """变体DTO"""
    variant: str
    variant_zh: str
    variant_en: str
    id: str
    label_zh: str


class SubcategoryDTO(BaseModel):
    """子分类DTO"""
    subcategory: str
    subcategory_zh: str
    subcategory_en: str
    id: str
    label_zh: str
    variants: list[VariantDTO]


class CategoryTreeDTO(BaseModel):
    """分类树DTO"""
    category: str
    category_zh: str
    category_en: str
    icon: str
    id: str
    label_zh: str
    subcategories: list[SubcategoryDTO]
