# 微服务架构拆分说明

## 概述

本项目已从单体架构拆分为微服务架构，将 AI/ML 相关的重依赖（PyTorch、ChromaDB、sentence-transformers）分离到独立的 AI 服务中。

## 架构对比

### 旧架构（单体）

```
┌─────────────────────────────────────┐
│           主后端服务                  │
│          (~3 GB)                    │
│                                     │
│  FastAPI + 业务逻辑                  │
│  + PyTorch + ChromaDB               │
│  + sentence-transformers            │
└─────────────────────────────────────┘
```

### 新架构（微服务）

```
┌─────────────────┐     HTTP/REST     ┌─────────────────┐
│   主后端服务      │ ◄──────────────► │   AI 服务        │
│  (FastAPI)       │                   │  (FastAPI)       │
│  ~150MB          │                   │  ~3GB            │
│                  │                   │                  │
│  业务逻辑         │                   │  EmbeddingService│
│  DTO/Handler     │                   │  ChromaDB        │
│  RemoteRepo      │                   │  sentence-trans  │
└─────────────────┘                   └─────────────────┘
```

## 文件结构

```
cnc-tooling-knowledge/
├── ai-service/                    # 新增：AI 微服务
│   ├── app.py                     # FastAPI 应用
│   ├── Dockerfile                 # AI 服务 Dockerfile
│   ├── requirements.txt           # ML 依赖
│   ├── test_service.py            # 测试脚本
│   └── README.md                  # AI 服务文档
│
├── src/                           # 主后端服务
│   └── infrastructure/
│       └── persistence/
│           ├── chroma_repo.py     # 原有：本地 ChromaDB 实现
│           └── remote_repo.py     # 新增：远程 AI 服务实现
│
├── Dockerfile.backend             # 原有：完整版 Dockerfile
├── Dockerfile.backend.lite        # 新增：轻量版 Dockerfile
├── Dockerfile.backend.optimized   # 优化版 Dockerfile
│
├── docker-compose.yml             # 更新：添加 AI 服务
│
└── requirements-lite.txt          # 新增：轻量级依赖
```

## 配置说明

### 环境变量

#### AI 服务
| 变量 | 默认值 | 说明 |
|------|--------|------|
| `CHROMA_PERSIST_DIR` | `/app/vector_store` | ChromaDB 持久化目录 |
| `CHROMA_COLLECTION` | `cutter_knowledge` | ChromaDB 集合名称 |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | 嵌入模型名称 |

#### 主后端服务
| 变量 | 默认值 | 说明 |
|------|--------|------|
| `USE_REMOTE_AI` | `false` | 是否使用远程 AI 服务 |
| `AI_SERVICE_URL` | `http://localhost:8001` | AI 服务 URL |

### Docker Compose 配置

```yaml
services:
  ai-service:
    build: ./ai-service
    ports:
      - "8001:8001"
    volumes:
      - vector_store:/app/vector_store
    environment:
      - CHROMA_PERSIST_DIR=/app/vector_store
      - EMBEDDING_MODEL=all-MiniLM-L6-v2

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend.lite
    ports:
      - "8000:8000"
    environment:
      - USE_REMOTE_AI=true
      - AI_SERVICE_URL=http://ai-service:8001
    depends_on:
      ai-service:
        condition: service_healthy
```

## 部署方式

### 方式 1：使用 Docker Compose（推荐）

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f ai-service
docker-compose logs -f backend
```

### 方式 2：单独部署

```bash
# 1. 部署 AI 服务
cd ai-service
docker build -t cnc-ai-service .
docker run -d \
  --name cnc-ai-service \
  -p 8001:8001 \
  -v ./vector_store:/app/vector_store \
  cnc-ai-service

# 2. 部署主后端服务
cd ..
docker build -f Dockerfile.backend.lite -t cnc-backend .
docker run -d \
  --name cnc-backend \
  -p 8000:8000 \
  -e USE_REMOTE_AI=true \
  -e AI_SERVICE_URL=http://host.docker.internal:8001 \
  cnc-backend
```

### 方式 3：本地开发

```bash
# 终端 1: 启动 AI 服务
cd ai-service
pip install -r requirements.txt
python app.py

# 终端 2: 启动主后端服务
export USE_REMOTE_AI=true
export AI_SERVICE_URL=http://localhost:8001
uvicorn src.interface.api.api:app --reload
```

## 镜像大小对比

| 服务 | 镜像大小 | 说明 |
|------|---------|------|
| AI 服务 | ~3 GB | 包含 PyTorch、ChromaDB、sentence-transformers |
| 主后端 (Lite) | ~150 MB | 仅包含 FastAPI、pandas、numpy |
| 主后端 (Full) | ~3 GB | 包含所有依赖（单体模式） |

**优化效果**：主后端镜像减小 **95%**（从 3GB 到 150MB）

## API 接口

### AI 服务端点 (端口 8001)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/embeddings` | POST | 生成单个嵌入 |
| `/embeddings/batch` | POST | 批量生成嵌入 |
| `/vectors/add` | POST | 添加向量 |
| `/vectors/bulk-add` | POST | 批量添加向量 |
| `/vectors/search` | POST | 语义搜索 |
| `/vectors/{id}` | GET | 获取向量 |
| `/vectors/{id}` | PUT | 更新向量 |
| `/vectors/{id}` | DELETE | 删除向量 |

### 主后端端点 (端口 8000)

API 接口保持不变，客户端无需修改。

## 代码变更说明

### 新增文件

1. **`ai-service/app.py`**
   - AI 服务主应用
   - 包含嵌入生成和向量存储功能
   - 暴露 REST API

2. **`src/infrastructure/persistence/remote_repo.py`**
   - 远程仓库实现
   - 通过 HTTP 调用 AI 服务
   - 实现 `CutterRepository` 接口

3. **`Dockerfile.backend.lite`**
   - 轻量级 Dockerfile
   - 不包含 ML 依赖

### 修改文件

1. **`src/interface/api/deps.py`**
   - 添加环境变量读取
   - 支持本地/远程模式切换

2. **`docker-compose.yml`**
   - 添加 AI 服务配置
   - 配置服务依赖关系

## 测试

### 测试 AI 服务

```bash
# 运行测试脚本
cd ai-service
python test_service.py http://localhost:8001

# 或使用 curl
curl http://localhost:8001/health
curl -X POST http://localhost:8001/embeddings \
  -H "Content-Type: application/json" \
  -d '{"text": "测试文本"}'
```

### 测试完整系统

```bash
# 启动所有服务
docker-compose up -d

# 等待服务就绪
docker-compose ps

# 测试主后端 API
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/cutters
```

## 故障排查

### AI 服务无法启动

```bash
# 查看日志
docker-compose logs ai-service

# 常见问题：
# 1. 内存不足 - PyTorch 需要较多内存
# 2. 端口冲突 - 确保 8001 端口未被占用
```

### 主后端无法连接 AI 服务

```bash
# 检查环境变量
docker-compose exec backend env | grep AI

# 测试连接
docker-compose exec backend curl http://ai-service:8001/health

# 常见问题：
# 1. AI 服务未就绪 - 检查 depends_on 配置
# 2. 网络问题 - 确保在同一 Docker 网络
```

### 向量数据丢失

```bash
# 检查 volume 挂载
docker-compose exec ai-service ls -la /app/vector_store

# 备份向量数据
docker run --rm -v cnc-tooling-knowledge_vector_store:/data -v $(pwd):/backup alpine tar czf /backup/vector_store_backup.tar.gz /data
```

## 扩展建议

### 1. 使用 GPU 加速

```yaml
# docker-compose.yml
ai-service:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
  environment:
    - NVIDIA_VISIBLE_DEVICES=all
```

### 2. 添加缓存层

在 AI 服务前添加 Redis 缓存，减少重复嵌入计算。

### 3. 负载均衡

部署多个 AI 服务实例，使用 Nginx 或 HAProxy 进行负载均衡。

### 4. 监控和日志

添加 Prometheus + Grafana 监控，以及 ELK 日志系统。

## 总结

通过微服务拆分：

1. ✅ **镜像大小优化**：主后端从 3GB 减小到 150MB
2. ✅ **服务解耦**：AI 服务可独立升级和扩展
3. ✅ **资源优化**：可针对不同服务配置不同资源
4. ✅ **开发效率**：主后端开发不需要等待 ML 依赖
5. ✅ **部署灵活**：可单独部署和扩展各服务
