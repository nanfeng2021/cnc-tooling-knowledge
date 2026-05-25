"""
Health Check Routes

健康检查端点。
"""

from datetime import datetime

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "cutter-management",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
    }


@router.get("/health/dependencies")
async def health_dependencies():
    """依赖服务健康检查"""
    from src.infrastructure.persistence.database import engine

    # 检查数据库连接
    db_status = "unknown"
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "service": "cutter-management",
        "dependencies": {
            "database": db_status,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }
