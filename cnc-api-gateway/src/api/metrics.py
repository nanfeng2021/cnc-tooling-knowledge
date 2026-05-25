"""
Prometheus 指标定义

为 API Gateway 提供 HTTP 请求计数器和延迟直方图。
"""

from prometheus_client import Counter, Histogram, Info

# 服务信息
SERVICE_INFO = Info("api_gateway", "API Gateway service information")
SERVICE_INFO.info({
    "version": "2.0.0",
    "service": "cnc-api-gateway",
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

# 代理请求计数器
PROXY_REQUESTS_TOTAL = Counter(
    "proxy_requests_total",
    "Total number of proxied requests",
    ["target_service", "status_code"],
)

# 代理请求延迟直方图
PROXY_REQUEST_DURATION_SECONDS = Histogram(
    "proxy_request_duration_seconds",
    "Proxied request duration in seconds",
    ["target_service"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# 限流计数器
RATE_LIMIT_HITS_TOTAL = Counter(
    "rate_limit_hits_total",
    "Total number of rate limit hits",
    ["client_id"],
)
