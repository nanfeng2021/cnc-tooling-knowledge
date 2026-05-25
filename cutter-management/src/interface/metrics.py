"""
Prometheus 指标定义

为 Cutter Management Service 提供 HTTP 请求计数器和延迟直方图。
"""

from prometheus_client import Counter, Histogram, Info

# 服务信息
SERVICE_INFO = Info("cutter_management", "Cutter Management service information")
SERVICE_INFO.info({
    "version": "1.0.0",
    "service": "cutter-management",
})

# HTTP 请求计数器
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"],
)

# HTTP 请求延迟直方图
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# 数据库操作计数器
DB_OPERATIONS_TOTAL = Counter(
    "db_operations_total",
    "Total number of database operations",
    ["operation", "model"],
)

# 数据库操作延迟直方图
DB_OPERATION_DURATION_SECONDS = Histogram(
    "db_operation_duration_seconds",
    "Database operation duration in seconds",
    ["operation", "model"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
)

# 事件发布计数器
EVENTS_PUBLISHED_TOTAL = Counter(
    "events_published_total",
    "Total number of domain events published",
    ["event_type"],
)
