"""
Category Repository Implementation

实现CategoryRepository接口，从静态JSON文件读取分类数据。
"""

import json
from pathlib import Path

from src.domain.repositories.category_repo import CategoryRepository


class JsonCategoryRepository(CategoryRepository):
    """基于JSON文件的分类仓库"""

    def __init__(self, data_path: str | None = None) -> None:
        if data_path is None:
            # 默认路径：项目根目录下的 data/categories.json
            self._data_path = Path(__file__).parent.parent.parent.parent.parent / "data" / "categories.json"
        else:
            self._data_path = Path(data_path)

    async def get_category_tree(self) -> list[dict]:
        """获取完整的分类树结构"""
        try:
            with open(self._data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []
