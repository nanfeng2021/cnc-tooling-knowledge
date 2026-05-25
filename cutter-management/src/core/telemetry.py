"""
OpenTelemetry 配置模块

为 Cutter Management Service 提供分布式追踪能力。
"""

import os
import logging

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.trace import format_trace_id, format_span_id

logger = logging.getLogger(__name__)


def setup_telemetry(service_name: str, service_version: str = "1.0.0") -> None:
    """
    配置 OpenTelemetry SDK

    Args:
        service_name: 服务名称
        service_version: 服务版本
    """
    # 创建 Resource 标识服务
    resource = Resource.create({
        SERVICE_NAME: service_name,
        SERVICE_VERSION: service_version,
        "deployment.environment": os.getenv("ENVIRONMENT", "development"),
    })

    # 创建 TracerProvider
    provider = TracerProvider(resource=resource)

    # 添加导出器
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otlp_endpoint:
        # 生产环境：导出到 OTLP Collector
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
        logger.info(f"OTel: 导出到 OTLP Collector at {otlp_endpoint}")
    else:
        # 开发环境：导出到控制台
        exporter = ConsoleSpanExporter()
        logger.info("OTel: 导出到控制台 (开发模式)")

    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)

    # 设置全局 TracerProvider
    trace.set_tracer_provider(provider)

    logger.info(f"OTel: 初始化完成 for {service_name}")


def instrument_fastapi(app) -> None:
    """
    自动埋点 FastAPI 应用

    Args:
        app: FastAPI 实例
    """
    FastAPIInstrumentor.instrument_app(app)
    logger.info("OTel: FastAPI 已埋点")


def instrument_sqlalchemy(engine) -> None:
    """
    自动埋点 SQLAlchemy 引擎

    Args:
        engine: SQLAlchemy 引擎实例
    """
    SQLAlchemyInstrumentor().instrument(engine=engine)
    logger.info("OTel: SQLAlchemy 已埋点")


def get_trace_context() -> dict:
    """
    获取当前 trace 上下文，用于注入到日志

    Returns:
        包含 trace_id 和 span_id 的字典
    """
    span = trace.get_current_span()
    if span and span.is_recording():
        ctx = span.get_span_context()
        return {
            "trace_id": format_trace_id(ctx.trace_id),
            "span_id": format_span_id(ctx.span_id),
        }
    return {}


def add_trace_id_processor(logger, method_name, event_dict):
    """
    structlog 处理器：自动添加 trace_id 到日志

    用法：
        structlog.configure(
            processors=[
                add_trace_id_processor,
                ...
            ]
        )
    """
    trace_ctx = get_trace_context()
    if trace_ctx:
        event_dict.update(trace_ctx)
    return event_dict
