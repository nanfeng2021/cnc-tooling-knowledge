"""
AI Service - FastAPI Application

AI智能服务入口，提供语义搜索、参数推荐、场景匹配功能。
集成 Prometheus 指标和结构化日志。
集成 OpenTelemetry 分布式追踪。
"""

import os
import time
from contextlib import asynccontextmanager
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from src.shared.logging import setup_logging, get_logger
from src.shared.telemetry import setup_telemetry, instrument_fastapi
from src.shared.metrics import (
    HTTP_REQUESTS_TOTAL,
    HTTP_REQUEST_DURATION_SECONDS,
    VECTOR_STORE_DOCUMENTS,
)
from api.routes import search, recommendations, scenarios, health, qa, similar, gcode

# 初始化 OpenTelemetry（必须在日志初始化之前）
setup_telemetry(service_name="ai-service", service_version="1.0.0")

# 初始化结构化日志
setup_logging(log_level=os.getenv("LOG_LEVEL", "INFO"), log_format=os.getenv("LOG_FORMAT", "json"))
logger = get_logger("ai_service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("ai_service.starting")

    # 预加载嵌入模型
    from src.shared.infrastructure.ml.embedding_model import get_embedding_model
    model = get_embedding_model()
    logger.info("ai_service.embedding_model_loaded", dimension=model.get_dimension())

    # 初始化ChromaDB
    from src.semantic_search.infrastructure.persistence.chroma_repo import ChromaVectorRepository
    repo = ChromaVectorRepository()
    count = await repo.count()
    VECTOR_STORE_DOCUMENTS.set(count)
    logger.info("ai_service.chromadb_ready", document_count=count)

    logger.info("ai_service.started")

    yield

    logger.info("ai_service.shutting_down")
    logger.info("ai_service.stopped")


app = FastAPI(
    title="CNC Tooling AI Service",
    description="AI智能服务，提供语义搜索、切削参数推荐、加工场景匹配",
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
app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])
app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["Recommendations"])
app.include_router(scenarios.router, prefix="/api/v1/scenarios", tags=["Scenarios"])
app.include_router(qa.router, prefix="/api/v1/qa", tags=["QA"])
app.include_router(similar.router, prefix="/api/v1/similar", tags=["Similar"])
app.include_router(gcode.router, prefix="/api/v1/gcode", tags=["GCode"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
