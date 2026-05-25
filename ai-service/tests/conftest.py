"""
AI Service - Pytest Configuration

提供测试fixtures和测试工具。
"""

import sys
from pathlib import Path
from typing import Generator
from unittest.mock import AsyncMock, MagicMock

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """创建事件循环"""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_vector_repository() -> AsyncMock:
    """模拟向量仓库"""
    repo = AsyncMock()
    repo.add = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    repo.get = AsyncMock()
    repo.search = AsyncMock()
    repo.count = AsyncMock(return_value=0)
    return repo


@pytest.fixture
def mock_embedding_model() -> MagicMock:
    """模拟嵌入模型"""
    model = MagicMock()
    model.encode.return_value = [0.1, 0.2, 0.3]  # 返回固定向量
    model.get_dimension.return_value = 384
    return model


@pytest.fixture
def sample_search_query() -> dict:
    """提供示例搜索查询"""
    return {
        "query": "10mm end mill for steel",
        "limit": 10,
        "filters": {
            "category": "milling",
            "compatible_materials": ["P"]
        }
    }


@pytest.fixture
def sample_recommendation_query() -> dict:
    """提供示例推荐查询"""
    return {
        "material": "steel",
        "operation": "milling",
        "tool_type": "end_mill",
        "diameter": 10.0
    }


@pytest.fixture
def sample_scenario_query() -> dict:
    """提供示例场景匹配查询"""
    return {
        "category": "milling",
        "subcategory": "milling_end_mill",
        "material": "steel",
        "diameter": 10.0
    }
