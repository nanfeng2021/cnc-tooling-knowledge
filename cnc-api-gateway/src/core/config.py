"""
API Gateway Configuration

配置管理模块，使用pydantic-settings进行配置验证。
"""

from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # JWT配置
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 后端服务配置
    CUTTER_SERVICE_URL: str = "http://cutter-management:8001"
    AI_SERVICE_URL: str = "http://ai-service:8002"
    
    # 限流配置
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10
    
    # Redis配置
    REDIS_URL: str = "redis://:redis123@111.228.18.127:6379/0"
    
    # CORS配置
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:80"]
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # 健康检查配置
    HEALTH_CHECK_INTERVAL: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


# 创建全局配置实例
settings = Settings()