"""
Redis Sliding Window Rate Limiter

Redis滑动窗口限流中间件，基于客户端IP进行限流。
"""

import time
from typing import Optional

import redis.asyncio as redis
from fastapi import HTTPException, Request, status

from src.core.config import settings


class RateLimiter:
    """Redis滑动窗口限流器"""

    def __init__(
        self,
        redis_url: str | None = None,
        max_requests: int | None = None,
        window_seconds: int = 60,
    ) -> None:
        self._redis_url = redis_url or settings.REDIS_URL
        self._max_requests = max_requests or settings.RATE_LIMIT_PER_MINUTE
        self._window_seconds = window_seconds
        self._redis_client: Optional[redis.Redis] = None

    async def _get_redis(self) -> redis.Redis:
        """获取Redis连接"""
        if self._redis_client is None:
            self._redis_client = redis.from_url(self._redis_url, decode_responses=True)
        return self._redis_client

    async def is_allowed(self, client_id: str) -> bool:
        """检查请求是否允许"""
        r = await self._get_redis()
        key = f"rate_limit:{client_id}"

        now = time.time()
        window_start = now - self._window_seconds

        # 使用滑动窗口算法
        pipe = r.pipeline()
        # 移除窗口外的记录
        pipe.zremrangebyscore(key, 0, window_start)
        # 添加当前请求
        pipe.zadd(key, {str(now): now})
        # 获取窗口内的请求数
        pipe.zcard(key)
        # 设置key过期时间
        pipe.expire(key, self._window_seconds)
        results = await pipe.execute()

        request_count = results[2]  # zcard的结果

        if request_count > self._max_requests:
            # 超出限制，移除刚添加的记录
            await r.zrem(key, str(now))
            return False

        return True

    async def get_remaining(self, client_id: str) -> int:
        """获取剩余请求数"""
        r = await self._get_redis()
        key = f"rate_limit:{client_id}"
        now = time.time()
        window_start = now - self._window_seconds

        # 清理过期记录
        await r.zremrangebyscore(key, 0, window_start)
        count = await r.zcard(key)

        return max(0, self._max_requests - count)

    async def close(self) -> None:
        """关闭Redis连接"""
        if self._redis_client:
            await self._redis_client.close()


# 全局限流器实例
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """获取限流器实例"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


async def check_rate_limit(request: Request) -> None:
    """FastAPI依赖：检查请求限流"""
    limiter = get_rate_limiter()

    # 获取客户端标识（IP或用户ID）
    client_id = request.client.host if request.client else "unknown"
    # 如果有认证信息，使用用户ID
    if hasattr(request.state, "user_id"):
        client_id = f"user:{request.state.user_id}"

    if not await limiter.is_allowed(client_id):
        remaining = await limiter.get_remaining(client_id)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={
                "X-RateLimit-Limit": str(limiter._max_requests),
                "X-RateLimit-Remaining": str(remaining),
                "Retry-After": str(limiter._window_seconds),
            },
        )


async def rate_limit_middleware(request: Request, call_next):
    """限流中间件"""
    limiter = get_rate_limiter()

    client_id = request.client.host if request.client else "unknown"
    if not await limiter.is_allowed(client_id):
        remaining = await limiter.get_remaining(client_id)
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={
                "X-RateLimit-Limit": str(limiter._max_requests),
                "X-RateLimit-Remaining": str(remaining),
            },
        )

    response = await call_next(request)
    remaining = await limiter.get_remaining(client_id)
    response.headers["X-RateLimit-Limit"] = str(limiter._max_requests)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    return response
