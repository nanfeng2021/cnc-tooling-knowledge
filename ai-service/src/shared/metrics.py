"""
Prometheus 指标定义

为 AI Service 提供 HTTP 请求计数器和延迟直方图。
"""

from prometheus_client import Counter, Histogram, Info, Gauge

# 服务信息
SERVICE_INFO = Info("ai_service", "AI Service information")
SERVICE_INFO.info({
    "version": "1.0.0",
    "service": "ai-service",
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

# 向量搜索计数器
VECTOR_SEARCH_TOTAL = Counter(
    "vector_search_total",
    "Total number of vector searches",
    ["status"],
)

# 向量搜索延迟直方图
VECTOR_SEARCH_DURATION_SECONDS = Histogram(
    "vector_search_duration_seconds",
    "Vector search duration in seconds",
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# 嵌入生成延迟直方图
EMBEDDING_DURATION_SECONDS = Histogram(
    "embedding_duration_seconds",
    "Embedding generation duration in seconds",
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

# 向量存储文档数量
VECTOR_STORE_DOCUMENTS = Gauge(
    "vector_store_documents_total",
    "Total number of documents in vector store",
)

# 事件消费计数器
EVENTS_CONSUMED_TOTAL = Counter(
    "events_consumed_total",
    "Total number of domain events consumed",
    ["event_type", "status"],
)
