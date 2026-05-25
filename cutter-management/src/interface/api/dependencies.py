"""
API Dependencies

FastAPI依赖注入配置。
"""

from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.handlers.cutter_handler import CutterCommandHandler, CutterQueryHandler
from src.application.handlers.category_handler import CategoryQueryHandler
from src.infrastructure.persistence.database import get_db_session
from src.infrastructure.persistence.postgres_repo import PostgresCutterRepository
from src.infrastructure.persistence.category_repo import JsonCategoryRepository


async def get_cutter_repository(session: AsyncSession = Depends(get_db_session)):
    """获取刀具仓库实例"""
    return PostgresCutterRepository(session)


async def get_command_handler(
    repo=Depends(get_cutter_repository),
    event_publisher=None,
) -> CutterCommandHandler:
    """获取命令处理器"""
    return CutterCommandHandler(repository=repo, event_publisher=event_publisher)


async def get_query_handler(
    repo=Depends(get_cutter_repository),
) -> CutterQueryHandler:
    """获取查询处理器"""
    return CutterQueryHandler(repository=repo)


async def get_category_query_handler() -> CategoryQueryHandler:
    """获取分类查询处理器"""
    repo = JsonCategoryRepository()
    return CategoryQueryHandler(repository=repo)


# 简化版依赖（不依赖数据库session，用于开发/测试）
def get_command_handler_simple() -> CutterCommandHandler:
    """简化的命令处理器依赖"""
    from src.infrastructure.persistence.database import async_session_factory

    # 这里简化处理，实际应使用依赖注入
    return None


def get_query_handler_simple() -> CutterQueryHandler:
    """简化的查询处理器依赖"""
    return None
