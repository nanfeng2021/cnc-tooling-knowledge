# Cutter Management Service

CNC刀具知识库系统的刀具管理服务，负责刀具的生命周期管理、制造商信息管理和分类体系管理。

## 功能特性

- **刀具生命周期管理**：刀具的创建、读取、更新、删除（CRUD）操作
- **制造商信息管理**：制造商的增删改查和关联管理
- **分类体系管理**：三级分类体系（类别/子类别/变体）
- **领域事件发布**：刀具变更事件的发布和通知
- **数据验证**：完整的业务规则验证
- **数据库迁移**：Alembic数据库版本管理
- **缓存支持**：Redis缓存热点数据
- **健康检查**：服务健康状态监控

## 架构

本服务遵循DDD（领域驱动设计）架构：

```
┌─────────────────────────────────────────────────────────────┐
│                     Interface Layer                          │
│                   (FastAPI REST API)                         │
├─────────────────────────────────────────────────────────────┤
│                    Application Layer                         │
│              (Commands, Queries, Handlers)                   │
├─────────────────────────────────────────────────────────────┤
│                       Domain Layer                           │
│         (Aggregates, Entities, Value Objects)                │
├─────────────────────────────────────────────────────────────┤
│                   Infrastructure Layer                       │
│            (PostgreSQL, RabbitMQ, Redis)                     │
└─────────────────────────────────────────────────────────────┘
```

### 领域模型

#### 聚合根
- **Cutter**：刀具聚合根，包含刀具的所有业务逻辑
- **Manufacturer**：制造商聚合根
- **Category**：分类聚合根

#### 值对象
- **CutterType**：刀具类型（类别/子类别/变体）
- **MaterialSpec**：材料规格
- **GeometryParams**：几何参数
- **CuttingParameters**：切削参数

#### 领域事件
- **CutterCreatedEvent**：刀具创建事件
- **CutterUpdatedEvent**：刀具更新事件
- **CutterDeletedEvent**：刀具删除事件

## API端点

### 刀具管理
- `GET /api/v1/cutters` - 获取刀具列表
- `POST /api/v1/cutters` - 创建刀具
- `GET /api/v1/cutters/{id}` - 获取刀具详情
- `PUT /api/v1/cutters/{id}` - 更新刀具
- `DELETE /api/v1/cutters/{id}` - 删除刀具
- `GET /api/v1/cutters/search` - 搜索刀具

### 制造商管理
- `GET /api/v1/manufacturers` - 获取制造商列表
- `POST /api/v1/manufacturers` - 创建制造商
- `GET /api/v1/manufacturers/{id}` - 获取制造商详情
- `PUT /api/v1/manufacturers/{id}` - 更新制造商
- `DELETE /api/v1/manufacturers/{id}` - 删除制造商

### 分类管理
- `GET /api/v1/categories` - 获取分类树
- `POST /api/v1/categories` - 创建分类
- `GET /api/v1/categories/{id}` - 获取分类详情
- `PUT /api/v1/categories/{id}` - 更新分类
- `DELETE /api/v1/categories/{id}` - 删除分类

### 系统
- `GET /health` - 健康检查
- `GET /docs` - API文档
- `GET /redoc` - ReDoc文档

## 快速开始

### 1. 安装依赖

```bash
cd cutter-management
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库和RabbitMQ连接信息
```

### 3. 数据库迁移

```bash
# 创建数据库迁移
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

### 4. 启动服务

```bash
# 开发模式
uvicorn src.interface.api.app:app --reload --port 8001

# 生产模式
python -m uvicorn src.interface.api.app:app --host 0.0.0.0 --port 8001
```

### 5. 使用Docker

```bash
# 构建镜像
docker build -t cnc-cutter-management .

# 运行容器
docker run -p 8001:8001 --env-file .env cnc-cutter-management

# 使用Docker Compose
docker-compose up -d
```

## 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `HOST` | `0.0.0.0` | 服务监听地址 |
| `PORT` | `8001` | 服务端口 |
| `DEBUG` | `false` | 调试模式 |
| `DATABASE_URL` | - | PostgreSQL连接地址（必须配置） |
| `DATABASE_POOL_SIZE` | `20` | 数据库连接池大小 |
| `DATABASE_MAX_OVERFLOW` | `10` | 连接池最大溢出连接数 |
| `RABBITMQ_URL` | `amqp://rabbitmq:5672` | RabbitMQ连接地址 |
| `RABBITMQ_EXCHANGE` | `cnc_events` | RabbitMQ交换机名称 |
| `RABBITMQ_QUEUE` | `cutter_events` | RabbitMQ队列名称 |
| `REDIS_URL` | `redis://redis:6379/1` | Redis连接地址 |
| `JWT_SECRET_KEY` | - | JWT密钥（必须配置） |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `LOG_FORMAT` | `json` | 日志格式 |
| `EVENT_PUBLISH_ENABLED` | `true` | 是否启用事件发布 |

### 数据库配置

1. **PostgreSQL**：主要数据存储
2. **连接池**：配置合适的连接池大小
3. **迁移**：使用Alembic管理数据库版本

### 消息队列配置

1. **RabbitMQ**：事件发布和订阅
2. **交换机**：事件路由
3. **队列**：事件消费

## 开发指南

### 项目结构

```
cutter-management/
├── src/
│   ├── domain/                    # 领域层
│   │   ├── models/               # 领域模型
│   │   ├── events/               # 领域事件
│   │   ├── repositories/         # 仓库接口
│   │   └── services/             # 领域服务
│   ├── application/              # 应用层
│   │   ├── commands/             # 命令处理器
│   │   ├── queries/              # 查询处理器
│   │   ├── event_handlers/       # 事件处理器
│   │   └── dto/                  # 数据传输对象
│   ├── infrastructure/           # 基础设施层
│   │   ├── persistence/          # 持久化实现
│   │   ├── messaging/            # 消息传递
│   │   └── database/             # 数据库配置
│   └── interface/                # 接口层
│       ├── api/                  # REST API
│       └── schemas/              # API Schema
├── tests/
│   ├── unit/                     # 单元测试
│   └── integration/              # 集成测试
├── alembic/                      # 数据库迁移
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
├── README.md
└── .env.example
```

### 添加新实体

1. 在 `src/domain/models/` 创建新的聚合根和值对象
2. 在 `src/domain/repositories/` 定义仓库接口
3. 在 `src/infrastructure/persistence/` 实现仓库
4. 在 `src/application/` 创建命令和查询处理器
5. 在 `src/interface/api/routes/` 创建API路由
6. 在 `src/interface/schemas/` 创建API Schema

### 添加新事件

1. 在 `src/domain/events/` 定义新的领域事件
2. 在 `src/domain/models/` 中发布事件
3. 在 `src/application/event_handlers/` 处理事件
4. 在 `src/infrastructure/messaging/` 发布到消息队列

### 数据库迁移

```bash
# 创建新迁移
alembic revision --autogenerate -m "描述信息"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1

# 查看迁移历史
alembic history
```

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
curl http://localhost:8001/health
```

### 指标监控

服务暴露Prometheus指标：
- `http_requests_total` - HTTP请求总数
- `http_request_duration_seconds` - 请求持续时间
- `database_connections_active` - 活跃数据库连接数
- `events_published_total` - 发布的事件总数

### 日志

结构化日志格式：
```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "level": "info",
  "message": "Cutter created",
  "cutter_id": "abc123",
  "cutter_name": "10mm End Mill",
  "manufacturer_id": "manufacturer123"
}
```

## 部署

### Docker部署

```bash
# 构建镜像
docker build -t cnc-cutter-management:latest .

# 运行容器
docker run -d \
  --name cnc-cutter-management \
  -p 8001:8001 \
  --env-file .env \
  cnc-cutter-management:latest
```

### Kubernetes部署

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cnc-cutter-management
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cnc-cutter-management
  template:
    metadata:
      labels:
        app: cnc-cutter-management
    spec:
      containers:
      - name: cnc-cutter-management
        image: cnc-cutter-management:latest
        ports:
        - containerPort: 8001
        envFrom:
        - configMapRef:
            name: cutter-management-config
        - secretRef:
            name: cutter-management-secrets
```

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查 `DATABASE_URL` 配置
   - 确保PostgreSQL服务已启动
   - 检查网络连接和防火墙设置

2. **RabbitMQ连接失败**
   - 检查 `RABBITMQ_URL` 配置
   - 确保RabbitMQ服务已启动
   - 检查用户权限

3. **迁移失败**
   - 检查数据库用户权限
   - 确保数据库存在
   - 检查迁移文件语法

### 调试模式

```bash
# 启用调试模式
export DEBUG=true
export LOG_LEVEL=DEBUG

# 启动服务
uvicorn src.interface.api.app:app --reload --port 8001
```

## 性能优化

### 数据库优化

- 合理配置连接池大小
- 使用索引优化查询
- 定期分析查询性能
- 使用读写分离（如需要）

### 缓存策略

- Redis缓存热点数据
- 合理设置缓存过期时间
- 使用缓存预热策略

### 异步处理

- 使用异步数据库操作
- 异步消息队列处理
- 异步HTTP客户端

## 安全建议

1. **生产环境必须使用HTTPS**
2. **定期更换JWT密钥**
3. **限制数据库访问权限**
4. **启用数据库审计日志**
5. **定期备份数据库**
6. **定期更新依赖包**

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License