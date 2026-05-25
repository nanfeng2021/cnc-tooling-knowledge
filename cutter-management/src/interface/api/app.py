"""
Cutter Management Service - FastAPI Application

刀具管理微服务入口。
集成 Prometheus 指标和结构化日志。
集成 OpenTelemetry 分布式追踪。
"""

from dotenv import load_dotenv
load_dotenv()

import os
import time
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from src.core.logging import setup_logging, get_logger
from src.core.telemetry import setup_telemetry, instrument_fastapi
from src.interface.api.routes import cutters, manufacturers, health, categories
from src.interface.metrics import (
    HTTP_REQUESTS_TOTAL,
    HTTP_REQUEST_DURATION_SECONDS,
)

# 初始化 OpenTelemetry（必须在日志初始化之前）
setup_telemetry(service_name="cutter-management", service_version="1.0.0")

# 初始化结构化日志
setup_logging(log_level=os.getenv("LOG_LEVEL", "INFO"), log_format=os.getenv("LOG_FORMAT", "json"))
logger = get_logger("cutter_management")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    from src.infrastructure.persistence.database import init_db

    logger.info("cutter_management.starting")

    await init_db()
    logger.info("cutter_management.started")

    yield

    # 关闭时清理
    from src.infrastructure.persistence.database import close_db

    logger.info("cutter_management.shutting_down")
    await close_db()
    logger.info("cutter_management.stopped")


app = FastAPI(
    title="Cutter Management Service",
    description="刀具管理微服务，提供刀具CRUD、制造商管理等功能",
    version="1.0.0",
    lifespan=lifespan,
)

# OpenTelemetry FastAPI 埋点（必须在 app 创建后、middleware 添加前）
instrument_fastapi(app)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus /metrics 端点
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# 请求指标中间件
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Prometheus 请求指标中间件"""
    # 健康检查和指标端点直接跳过
    if request.url.path in ("/health", "/health/dependencies", "/metrics"):
        return await call_next(request)

    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time

    # 记录请求指标
    HTTP_REQUESTS_TOTAL.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code,
    ).inc()
    HTTP_REQUEST_DURATION_SECONDS.labels(
        method=request.method,
        endpoint=request.url.path,
    ).observe(duration)

    return response


# 注册路由
app.include_router(health.router, tags=["Health"])
app.include_router(cutters.router, prefix="/api/v1/cutters", tags=["Cutters"])
app.include_router(manufacturers.router, prefix="/api/v1/manufacturers", tags=["Manufacturers"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["Categories"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
