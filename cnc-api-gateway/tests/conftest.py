"""
API Gateway - Pytest Configuration

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
def mock_http_client() -> AsyncMock:
    """模拟HTTP客户端"""
    client = AsyncMock()
    client.request = AsyncMock()
    return client


@pytest.fixture
def mock_rate_limiter() -> AsyncMock:
    """模拟限流器"""
    limiter = AsyncMock()
    limiter.is_allowed = AsyncMock(return_value=True)
    limiter.get_remaining = AsyncMock(return_value=59)
    limiter.close = AsyncMock()
    limiter._max_requests = 60
    limiter._window_seconds = 60
    return limiter


@pytest.fixture
def sample_jwt_payload() -> dict:
    """提供示例JWT payload"""
    return {
        "sub": "user123",
        "exp": 9999999999,  # 远未来时间
        "iat": 1000000000,
        "scope": "read write"
    }
