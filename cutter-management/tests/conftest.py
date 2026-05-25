"""
Cutter Management Service - Pytest Configuration

提供异步测试fixtures和测试工具。
"""

import asyncio
import sys
from pathlib import Path
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_cutter_repository() -> AsyncMock:
    """模拟刀具仓库"""
    repo = AsyncMock()
    repo.add = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_all = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    repo.count = AsyncMock()
    repo.get_filtered = AsyncMock()
    return repo


@pytest.fixture
def mock_manufacturer_repository() -> AsyncMock:
    """模拟制造商仓库"""
    repo = AsyncMock()
    repo.add = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_all = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def mock_event_publisher() -> AsyncMock:
    """模拟事件发布者"""
    publisher = AsyncMock()
    publisher.publish = AsyncMock()
    return publisher


@pytest.fixture
def sample_cutter_data() -> dict:
    """提供示例刀具数据"""
    return {
        "name": "CoroMill Plura 10mm End Mill",
        "category": "milling",
        "subcategory": "milling_end_mill",
        "variant": "square",
        "substrate": "carbide_K20",
        "coating_type": "TiAlN",
        "hardness_hrc": 92.0,
        "iso_class": "K20",
        "material_grade": "4325",
        "diameter": 10.0,
        "length": 75.0,
        "flute_length": 30.0,
        "number_of_flutes": 4,
        "helix_angle": 38.0,
        "corner_radius": 0.0,
        "recommended_parameters": {
            "vc_steel": 180.0,
            "vc_stainless": 120.0,
            "vc_cast_iron": 250.0,
            "vc_aluminum": 400.0,
            "fz_steel": 0.05,
            "fz_stainless": 0.04,
            "fz_cast_iron": 0.06,
            "fz_aluminum": 0.08,
            "ap_max": 18.0,
            "ae_max": 10.0,
        },
        "usage_guidelines": "Suitable for steel and cast iron roughing and finishing",
        "compatible_materials": ["P", "K"],
        "manufacturer_id": "mfr-sandvik",
        "model_number": "R216.34-10040-APKT 4325",
        "image_url": "/images/cutters/milling_end_mill_square.png",
    }


@pytest.fixture
def sample_create_cutter_request() -> dict:
    """提供创建刀具请求数据"""
    return {
        "name": "Test End Mill",
        "category": "milling",
        "subcategory": "milling_end_mill",
        "variant": "square",
        "substrate": "carbide",
        "coating_type": "TiAlN",
        "diameter": 10.0,
        "length": 75.0,
        "flute_length": 30.0,
        "number_of_flutes": 4,
        "compatible_materials": ["P", "K"],
    }
