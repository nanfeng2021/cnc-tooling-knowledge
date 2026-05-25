# CNC API Gateway Service

CNC刀具知识库系统的API网关服务，提供统一的API入口、路由、认证和限流功能。

## 功能特性

- **统一入口**：所有API请求通过网关路由到后端服务
- **请求路由**：根据路径将请求转发到相应的微服务
- **认证授权**：JWT Token验证和权限控制
- **限流熔断**：防止服务过载，保证系统稳定性
- **API文档聚合**：统一的Swagger文档入口
- **CORS处理**：跨域资源共享配置
- **健康检查**：服务健康状态监控
- **日志记录**：结构化日志和请求追踪

## 架构

```
┌─────────────────┐         HTTP/REST          ┌─────────────────┐
│   客户端         │ ◄──────────────────────────► │   API网关服务    │
│   (浏览器/App)  │                              │   (本服务)       │
└─────────────────┘                              └─────────────────┘
                                                        │
        ┌───────────────────────────────────────────────┼───────────────────────────────────────────────┐
        │                                               │                                               │
        ▼                                               ▼                                               ▼
┌──────────────────┐                          ┌──────────────────┐                          ┌──────────────────┐
│   刀具管理服务    │                          │   AI智能服务      │                          │   其他服务        │
│   (cutter-mgmt)  │                          │   (ai-service)   │                          │   (未来扩展)      │
└──────────────────┘                          └──────────────────┘                          └──────────────────┘
```

## API路由

### 刀具管理相关
- `GET /api/v1/cutters` - 获取刀具列表
- `POST /api/v1/cutters` - 创建刀具
- `GET /api/v1/cutters/{id}` - 获取刀具详情
- `PUT /api/v1/cutters/{id}` - 更新刀具
- `DELETE /api/v1/cutters/{id}` - 删除刀具

### 智能搜索相关
- `POST /api/v1/search` - 语义搜索
- `GET /api/v1/search/material/{material}` - 按材料搜索

### 推荐服务相关
- `GET /api/v1/recommendations/parameters` - 获取切削参数推荐

### 场景匹配相关
- `POST /api/v1/scenarios/match` - 场景匹配

### 系统相关
- `GET /health` - 健康检查
- `GET /docs` - API文档
- `GET /redoc` - ReDoc文档

## 快速开始

### 1. 安装依赖

```bash
cd cnc-api-gateway
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置后端服务地址和JWT密钥
```

### 3. 启动服务

```bash
# 开发模式
uvicorn src.api.app:app --reload --port 8000

# 生产模式
python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

### 4. 使用Docker

```bash
# 构建镜像
docker build -t cnc-api-gateway .

# 运行容器
docker run -p 8000:8000 --env-file .env cnc-api-gateway

# 使用Docker Compose
docker-compose up -d
```

## 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `HOST` | `0.0.0.0` | 服务监听地址 |
| `PORT` | `8000` | 服务端口 |
| `DEBUG` | `false` | 调试模式 |
| `JWT_SECRET_KEY` | - | JWT密钥（必须配置） |
| `JWT_ALGORITHM` | `HS256` | JWT算法 |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token过期时间（分钟） |
| `CUTTER_SERVICE_URL` | `http://cutter-management:8001` | 刀具管理服务地址 |
| `AI_SERVICE_URL` | `http://ai-service:8002` | AI智能服务地址 |
| `RATE_LIMIT_PER_MINUTE` | `60` | 每分钟请求限制 |
| `RATE_LIMIT_BURST` | `10` | 突发请求限制 |
| `REDIS_URL` | `redis://redis:6379/0` | Redis连接地址 |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | 允许的跨域来源 |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `LOG_FORMAT` | `json` | 日志格式 |

### 认证配置

1. **JWT密钥**：在生产环境中必须设置强密钥
2. **Token过期时间**：根据安全需求调整
3. **CORS配置**：根据前端域名配置

## 开发指南

### 项目结构

```
cnc-api-gateway/
├── src/
│   ├── api/
│   │   ├── app.py              # FastAPI应用
│   │   ├── routes/
│   │   │   ├── proxy.py        # 代理路由
│   │   │   └── health.py       # 健康检查
│   │   └── middleware/
│   │       ├── auth.py         # 认证中间件
│   │       ├── rate_limit.py   # 限流中间件
│   │       └── cors.py         # CORS中间件
│   ├── core/
│   │   ├── config.py           # 配置管理
│   │   └── security.py         # 安全工具
│   └── __init__.py
├── tests/
│   ├── test_proxy.py
│   └── test_middleware.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
├── README.md
└── .env.example
```

### 添加新路由

1. 在 `src/api/routes/` 创建新的路由模块
2. 在 `src/api/app.py` 中注册路由
3. 更新配置文件中的路由映射

### 自定义中间件

1. 在 `src/api/middleware/` 创建新的中间件
2. 在 `src/api/app.py` 中添加中间件

## 测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/ -v

# 运行集成测试
pytest tests/integration/ -v

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```

## 监控

### 健康检查

```bash
curl http://localhost:8000/health
```

### 指标监控

服务暴露Prometheus指标：
- `http_requests_total` - HTTP请求总数
- `http_request_duration_seconds` - 请求持续时间
- `rate_limit_hits_total` - 限流命中次数

### 日志

结构化日志格式：
```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "level": "info",
  "message": "Request processed",
  "request_id": "abc123",
  "method": "GET",
  "path": "/api/v1/cutters",
  "status_code": 200,
  "duration_ms": 150
}
```

## 部署

### Docker部署

```bash
# 构建镜像
docker build -t cnc-api-gateway:latest .

# 运行容器
docker run -d \
  --name cnc-api-gateway \
  -p 8000:8000 \
  --env-file .env \
  cnc-api-gateway:latest
```

### Kubernetes部署

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cnc-api-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cnc-api-gateway
  template:
    metadata:
      labels:
        app: cnc-api-gateway
    spec:
      containers:
      - name: cnc-api-gateway
        image: cnc-api-gateway:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: api-gateway-config
        - secretRef:
            name: api-gateway-secrets
```

## 故障排除

### 常见问题

1. **无法连接到后端服务**
   - 检查 `CUTTER_SERVICE_URL` 和 `AI_SERVICE_URL` 配置
   - 确保后端服务已启动
   - 检查网络连接

2. **JWT验证失败**
   - 检查 `JWT_SECRET_KEY` 配置
   - 确保Token格式正确
   - 检查Token是否过期

3. **限流过于频繁**
   - 调整 `RATE_LIMIT_PER_MINUTE` 和 `RATE_LIMIT_BURST`
   - 检查Redis连接

### 调试模式

```bash
# 启用调试模式
export DEBUG=true
export LOG_LEVEL=DEBUG

# 启动服务
uvicorn src.api.app:app --reload --port 8000
```

## 性能优化

### 连接池

- HTTP客户端使用连接池
- Redis连接池配置
- 数据库连接池

### 缓存

- Redis缓存热点数据
- 本地缓存频繁访问的数据

### 异步处理

- 使用异步HTTP客户端
- 异步数据库操作
- 异步消息队列

## 安全建议

1. **生产环境必须使用HTTPS**
2. **定期更换JWT密钥**
3. **限制CORS来源**
4. **启用请求速率限制**
5. **记录所有安全相关日志**
6. **定期更新依赖包**

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License