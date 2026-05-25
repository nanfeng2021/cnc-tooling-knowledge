"""
CNC API Gateway - FastAPI Application

统一API入口，路由到后端微服务。
集成JWT认证、限流中间件、Prometheus指标和增强型健康检查。
集成 OpenTelemetry 分布式追踪。
"""

import os
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app

from src.core.config import settings
from src.core.logging import setup_logging, get_logger
from src.core.telemetry import setup_telemetry, instrument_fastapi, instrument_httpx
from opentelemetry.trace import format_trace_id, format_span_id
from src.api.routes.health import router as health_router
from src.api.middleware.rate_limit import get_rate_limiter
from src.api.metrics import (
    HTTP_REQUESTS_TOTAL,
    HTTP_REQUEST_DURATION_SECONDS,
    PROXY_REQUESTS_TOTAL,
    PROXY_REQUEST_DURATION_SECONDS,
    RATE_LIMIT_HITS_TOTAL,
)

# 初始化 OpenTelemetry（必须在日志初始化之前）
setup_telemetry(service_name="cnc-api-gateway", service_version="2.0.0")

# 初始化结构化日志
setup_logging(log_level=settings.LOG_LEVEL, log_format=settings.LOG_FORMAT)
logger = get_logger("api_gateway")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("api_gateway.starting", host=settings.HOST, port=settings.PORT)

    # 埋点 httpx（FastAPI 埋点已在模块级别完成）
    instrument_httpx()

    # 创建HTTP客户端
    app.state.http_client = httpx.AsyncClient(
        timeout=30.0,
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
    )

    # 初始化限流器
    app.state.rate_limiter = get_rate_limiter()

    logger.info("api_gateway.started")

    yield

    # 关闭时清理
    logger.info("api_gateway.shutting_down")
    await app.state.http_client.aclose()
    await app.state.rate_limiter.close()
    logger.info("api_gateway.stopped")


app = FastAPI(
    title="CNC Tooling API Gateway",
    description="统一API入口，路由到后端微服务。集成JWT认证、限流中间件、Prometheus指标和增强型健康检查",
    version="2.0.0",
    lifespan=lifespan,
)

# OpenTelemetry FastAPI 埋点（必须在 app 创建后、middleware 添加前）
instrument_fastapi(app)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus /metrics 端点
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# 注册健康检查路由
app.include_router(health_router)


# 测试端点 - 验证 OpenTelemetry trace
@app.get("/test-trace")
async def test_trace():
    """测试 OpenTelemetry trace 是否正常工作"""
    from opentelemetry import trace

    tracer = trace.get_tracer("api-gateway")
    with tracer.start_as_current_span("test-operation") as span:
        span.set_attribute("test.key", "test-value")
        logger.info("test.trace", message="This is a test trace log")

        return {
            "status": "ok",
            "message": "Trace test completed",
            "trace_id": format_trace_id(trace.get_current_span().get_span_context().trace_id),
            "span_id": format_span_id(trace.get_current_span().get_span_context().span_id),
        }


# 请求指标中间件（应用于所有请求）
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Prometheus 请求指标和限流中间件"""
    # 健康检查和指标端点不限流
    if request.url.path in ("/health", "/health/dependencies", "/metrics", "/docs", "/openapi.json"):
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

    # 限流检查
    limiter = app.state.rate_limiter
    client_id = request.client.host if request.client else "unknown"

    if not await limiter.is_allowed(client_id):
        remaining = await limiter.get_remaining(client_id)
        RATE_LIMIT_HITS_TOTAL.labels(client_id=client_id).inc()

        logger.warning(
            "rate_limit.exceeded",
            client_id=client_id,
            path=request.url.path,
        )

        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"},
            headers={
                "X-RateLimit-Limit": str(limiter._max_requests),
                "X-RateLimit-Remaining": str(remaining),
                "Retry-After": str(limiter._window_seconds),
            },
        )

    # 记录请求开始时间
    start_time = time.time()

    # 处理请求
    response = await call_next(request)

    # 计算请求耗时
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

    # 添加限流头信息
    remaining = await limiter.get_remaining(client_id)
    response.headers["X-RateLimit-Limit"] = str(limiter._max_requests)
    response.headers["X-RateLimit-Remaining"] = str(remaining)

    return response


# 代理路由 - 刀具管理服务
@app.api_route(
    "/api/v1/cutters/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE"],
    tags=["Cutters"]
)
async def proxy_cutters(request: Request, path: str):
    """代理请求到刀具管理服务"""
    return await proxy_request(
        request,
        f"{settings.CUTTER_SERVICE_URL}/api/v1/cutters/{path}"
    )


@app.api_route(
    "/api/v1/cutters",
    methods=["GET", "POST"],
    tags=["Cutters"]
)
async def proxy_cutters_root(request: Request):
    """代理请求到刀具管理服务（根路径）"""
    return await proxy_request(
        request,
        f"{settings.CUTTER_SERVICE_URL}/api/v1/cutters"
    )


# 代理路由 - 制造商管理服务
@app.api_route(
    "/api/v1/manufacturers/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE"],
    tags=["Manufacturers"]
)
async def proxy_manufacturers(request: Request, path: str):
    """代理请求到刀具管理服务"""
    return await proxy_request(
        request,
        f"{settings.CUTTER_SERVICE_URL}/api/v1/manufacturers/{path}"
    )


@app.api_route(
    "/api/v1/manufacturers",
    methods=["GET", "POST"],
    tags=["Manufacturers"]
)
async def proxy_manufacturers_root(request: Request):
    """代理请求到刀具管理服务（根路径）"""
    return await proxy_request(
        request,
        f"{settings.CUTTER_SERVICE_URL}/api/v1/manufacturers"
    )


# 代理路由 - 分类管理服务
@app.api_route(
    "/api/v1/categories/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE"],
    tags=["Categories"]
)
async def proxy_categories(request: Request, path: str):
    """代理请求到刀具管理服务"""
    return await proxy_request(
        request,
        f"{settings.CUTTER_SERVICE_URL}/api/v1/categories/{path}"
    )


@app.api_route(
    "/api/v1/categories",
    methods=["GET", "POST"],
    tags=["Categories"]
)
async def proxy_categories_root(request: Request):
    """代理请求到刀具管理服务（根路径）"""
    return await proxy_request(
        request,
        f"{settings.CUTTER_SERVICE_URL}/api/v1/categories"
    )


# 代理路由 - AI智能服务
@app.api_route(
    "/api/v1/search/{path:path}",
    methods=["GET", "POST"],
    tags=["Search"]
)
async def proxy_search(request: Request, path: str):
    """代理请求到AI智能服务"""
    return await proxy_request(
        request,
        f"{settings.AI_SERVICE_URL}/api/v1/search/{path}"
    )


@app.api_route(
    "/api/v1/search",
    methods=["GET", "POST"],
    tags=["Search"]
)
async def proxy_search_root(request: Request):
    """代理请求到AI智能服务（根路径）"""
    return await proxy_request(
        request,
        f"{settings.AI_SERVICE_URL}/api/v1/search"
    )


@app.api_route(
    "/api/v1/recommendations/{path:path}",
    methods=["GET", "POST"],
    tags=["Recommendations"]
)
async def proxy_recommendations(request: Request, path: str):
    """代理请求到AI智能服务"""
    return await proxy_request(
        request,
        f"{settings.AI_SERVICE_URL}/api/v1/recommendations/{path}"
    )


@app.api_route(
    "/api/v1/recommendations",
    methods=["GET", "POST"],
    tags=["Recommendations"]
)
async def proxy_recommendations_root(request: Request):
    """代理请求到AI智能服务（根路径）"""
    return await proxy_request(
        request,
        f"{settings.AI_SERVICE_URL}/api/v1/recommendations"
    )


@app.api_route(
    "/api/v1/scenarios/{path:path}",
    methods=["GET", "POST"],
    tags=["Scenarios"]
)
async def proxy_scenarios(request: Request, path: str):
    """代理请求到AI智能服务"""
    return await proxy_request(
        request,
        f"{settings.AI_SERVICE_URL}/api/v1/scenarios/{path}"
    )


@app.api_route(
    "/api/v1/scenarios",
    methods=["GET", "POST"],
    tags=["Scenarios"]
)
async def proxy_scenarios_root(request: Request):
    """代理请求到AI智能服务（根路径）"""
    return await proxy_request(
        request,
        f"{settings.AI_SERVICE_URL}/api/v1/scenarios"
    )


# 代理路由 - 智能问答服务
@app.api_route(
    "/api/v1/qa/{path:path}",
    methods=["GET", "POST"],
    tags=["QA"]
)
async def proxy_qa(request: Request, path: str):
    """代理请求到AI智能服务"""
    return await proxy_request(
        request,
        f"{settings.AI_SERVICE_URL}/api/v1/qa/{path}"
    )


@app.api_route(
    "/api/v1/qa",
    methods=["GET", "POST"],
    tags=["QA"]
)
async def proxy_qa_root(request: Request):
    """代理请求到AI智能服务（根路径）"""
    return await proxy_request(
        request,
        f"{settings.AI_SERVICE_URL}/api/v1/qa"
    )


# 代理路由 - 相似刀具服务
@app.api_route(
    "/api/v1/similar/{path:path}",
    methods=["GET", "POST"],
    tags=["Similar"]
)
async def proxy_similar(request: Request, path: str):
    """代理请求到AI智能服务"""
    return await proxy_request(
        request,
        f"{settings.AI_SERVICE_URL}/api/v1/similar/{path}"
    )


@app.api_route(
    "/api/v1/similar",
    methods=["GET", "POST"],
    tags=["Similar"]
)
async def proxy_similar_root(request: Request):
    """代理请求到AI智能服务（根路径）"""
    return await proxy_request(
        request,
        f"{settings.AI_SERVICE_URL}/api/v1/similar"
    )


# 代理路由 - G代码生成服务
@app.api_route(
    "/api/v1/gcode/{path:path}",
    methods=["GET", "POST"],
    tags=["GCode"]
)
async def proxy_gcode(request: Request, path: str):
    """代理请求到AI智能服务"""
    return await proxy_request(
        request,
        f"{settings.AI_SERVICE_URL}/api/v1/gcode/{path}"
    )


@app.api_route(
    "/api/v1/gcode",
    methods=["GET", "POST"],
    tags=["GCode"]
)
async def proxy_gcode_root(request: Request):
    """代理请求到AI智能服务（根路径）"""
    return await proxy_request(
        request,
        f"{settings.AI_SERVICE_URL}/api/v1/gcode"
    )


async def proxy_request(request: Request, target_url: str) -> JSONResponse:
    """通用请求代理函数"""
    # 提取目标服务名称
    target_service = "cutter-management" if "cutter-management" in target_url else "ai-service"

    logger.debug(
        "proxy.request",
        method=request.method,
        target_url=target_url,
        target_service=target_service,
    )

    start_time = time.time()

    try:
        # 获取请求体
        body = await request.body()

        # 构建请求头
        headers = dict(request.headers)
        # 移除不需要转发的头
        headers.pop("host", None)
        headers.pop("content-length", None)

        # 发送请求到目标服务
        response = await request.app.state.http_client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=body,
            params=dict(request.query_params)
        )

        # 计算耗时
        duration = time.time() - start_time

        # 记录代理请求指标
        PROXY_REQUESTS_TOTAL.labels(
            target_service=target_service,
            status_code=response.status_code,
        ).inc()
        PROXY_REQUEST_DURATION_SECONDS.labels(
            target_service=target_service,
        ).observe(duration)

        logger.debug(
            "proxy.response",
            method=request.method,
            target_url=target_url,
            status_code=response.status_code,
            duration=duration,
        )

        # 返回响应
        return JSONResponse(
            status_code=response.status_code,
            content=response.json(),
            headers=dict(response.headers)
        )

    except httpx.TimeoutException:
        duration = time.time() - start_time
        PROXY_REQUESTS_TOTAL.labels(
            target_service=target_service,
            status_code=504,
        ).inc()
        PROXY_REQUEST_DURATION_SECONDS.labels(
            target_service=target_service,
        ).observe(duration)

        logger.error(
            "proxy.timeout",
            method=request.method,
            target_url=target_url,
            duration=duration,
        )
        raise HTTPException(status_code=504, detail="Gateway Timeout")

    except httpx.ConnectError:
        duration = time.time() - start_time
        PROXY_REQUESTS_TOTAL.labels(
            target_service=target_service,
            status_code=502,
        ).inc()
        PROXY_REQUEST_DURATION_SECONDS.labels(
            target_service=target_service,
        ).observe(duration)

        logger.error(
            "proxy.connect_error",
            method=request.method,
            target_url=target_url,
            duration=duration,
        )
        raise HTTPException(status_code=502, detail="Bad Gateway")

    except Exception as e:
        duration = time.time() - start_time
        PROXY_REQUESTS_TOTAL.labels(
            target_service=target_service,
            status_code=500,
        ).inc()
        PROXY_REQUEST_DURATION_SECONDS.labels(
            target_service=target_service,
        ).observe(duration)

        logger.error(
            "proxy.error",
            method=request.method,
            target_url=target_url,
            error=str(e),
            duration=duration,
        )
        raise HTTPException(status_code=500, detail=str(e))