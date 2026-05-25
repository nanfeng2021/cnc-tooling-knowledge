"""
Health Check Routes

增强型健康检查，聚合后端依赖服务状态。
"""

from datetime import datetime
from typing import Any

import httpx
from fastapi import APIRouter, Request

from src.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """基础健康检查"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
    }


@router.get("/health/dependencies")
async def health_dependencies(request: Request):
    """聚合后端依赖服务健康状态"""
    dependencies: dict[str, Any] = {}
    overall_status = "healthy"

    # 检查cutter-management
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.CUTTER_SERVICE_URL}/health")
            if resp.status_code == 200:
                dependencies["cutter-management"] = {
                    "status": "healthy",
                    "url": settings.CUTTER_SERVICE_URL,
                }
            else:
                dependencies["cutter-management"] = {
                    "status": "unhealthy",
                    "url": settings.CUTTER_SERVICE_URL,
                    "error": f"HTTP {resp.status_code}",
                }
                overall_status = "degraded"
    except Exception as e:
        dependencies["cutter-management"] = {
            "status": "unreachable",
            "url": settings.CUTTER_SERVICE_URL,
            "error": str(e),
        }
        overall_status = "degraded"

    # 检查ai-service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.AI_SERVICE_URL}/health")
            if resp.status_code == 200:
                dependencies["ai-service"] = {
                    "status": "healthy",
                    "url": settings.AI_SERVICE_URL,
                }
            else:
                dependencies["ai-service"] = {
                    "status": "unhealthy",
                    "url": settings.AI_SERVICE_URL,
                    "error": f"HTTP {resp.status_code}",
                }
                overall_status = "degraded"
    except Exception as e:
        dependencies["ai-service"] = {
            "status": "unreachable",
            "url": settings.AI_SERVICE_URL,
            "error": str(e),
        }
        overall_status = "degraded"

    return {
        "status": overall_status,
        "service": "api-gateway",
        "dependencies": dependencies,
        "timestamp": datetime.utcnow().isoformat(),
    }
