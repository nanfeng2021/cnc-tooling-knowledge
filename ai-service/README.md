# AI Intelligence Service

CNC刀具知识库系统的AI智能服务，提供语义搜索、智能推荐和场景匹配功能。

## 功能特性

### 语义搜索服务
- **向量嵌入生成**：将文本转换为向量表示
- **语义相似度搜索**：基于向量相似度的智能搜索
- **文档索引管理**：向量文档的增删改查
- **批量处理**：支持批量嵌入生成和索引

### 智能推荐服务
- **切削参数推荐**：基于材料和工艺的参数推荐
- **刀具推荐**：根据加工需求推荐合适刀具
- **相似刀具查找**：查找功能相似的刀具
- **置信度评估**：推荐结果的置信度评分

### 场景匹配服务
- **加工场景识别**：识别用户的加工场景
- **场景匹配算法**：基于多维度特征的场景匹配
- **结果排序**：按匹配度排序推荐结果
- **场景库管理**：加工场景的存储和管理

## 架构

本服务采用DDD架构，包含三个子域：

```
┌─────────────────────────────────────────────────────────────┐
│                      AI Intelligence Service                 │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  语义搜索     │  │  智能推荐     │  │  场景匹配     │      │
│  │  子域        │  │  子域        │  │  子域        │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                 │                 │               │
│         ▼                 ▼                 ▼               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    共享内核                          │   │
│  │  • 嵌入模型  • 向量存储  • 事件处理  • 配置管理      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 子域划分

#### 1. 语义搜索子域
- **领域模型**：SearchQuery, SearchResult, Document
- **领域服务**：EmbeddingService, SearchService
- **仓库接口**：VectorRepository
- **应用服务**：SemanticSearchQuery, IndexDocumentCommand

#### 2. 智能推荐子域
- **领域模型**：Recommendation, CuttingParameters
- **领域服务**：RecommendationService
- **应用服务**：GetRecommendationsQuery

#### 3. 场景匹配子域
- **领域模型**：MachiningScenario, ScenarioMatch
- **领域服务**：ScenarioMatchingService
- **应用服务**：MatchScenarioQuery

#### 4. 共享内核
- **事件处理**：CutterEvent, CutterEventHandler
- **基础设施**：EmbeddingModel, VectorStore, MessageQueue
- **配置管理**：ServiceConfig, ModelConfig

## API端点

### 语义搜索
- `POST /api/v1/search` - 语义搜索
- `POST /api/v1/search/similar` - 查找相似文档
- `POST /api/v1/search/index` - 索引文档
- `POST /api/v1/search/index/batch` - 批量索引文档
- `GET /api/v1/search/documents/{id}` - 获取文档详情
- `DELETE /api/v1/search/documents/{id}` - 删除文档

### 智能推荐
- `GET /api/v1/recommendations/parameters` - 获取切削参数推荐
- `GET /api/v1/recommendations/tools` - 获取刀具推荐
- `GET /api/v1/recommendations/similar/{id}` - 获取相似刀具

### 场景匹配
- `POST /api/v1/scenarios/match` - 场景匹配
- `GET /api/v1/scenarios` - 获取场景列表
- `GET /api/v1/scenarios/{id}` - 获取场景详情

### 嵌入生成
- `POST /api/v1/embeddings` - 生成单文本嵌入
- `POST /api/v1/embeddings/batch` - 批量生成嵌入

### 向量操作
- `POST /api/v1/vectors/add` - 添加向量
- `POST /api/v1/vectors/search` - 向量搜索
- `GET /api/v1/vectors/{id}` - 获取向量详情
- `PUT /api/v1/vectors/{id}` - 更新向量
- `DELETE /api/v1/vectors/{id}` - 删除向量

### 系统
- `GET /health` - 健康检查
- `GET /docs` - API文档
- `GET /redoc` - ReDoc文档

## 快速开始

### 1. 安装依赖

```bash
cd ai-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置模型路径和ChromaDB设置
```

### 3. 下载模型

```bash
# 下载预训练模型（首次运行需要）
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### 4. 启动服务

```bash
# 开发模式
uvicorn api.app:app --reload --port 8002

# 生产模式
python -m uvicorn api.app:app --host 0.0.0.0 --port 8002
```

### 5. 使用Docker

```bash
# 构建镜像
docker build -t cnc-ai-service .

# 运行容器
docker run -p 8002:8002 -v ./vector_store:/app/vector_store --env-file .env cnc-ai-service

# 使用Docker Compose
docker-compose up -d
```

## 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `HOST` | `0.0.0.0` | 服务监听地址 |
| `PORT` | `8002` | 服务端口 |
| `DEBUG` | `false` | 调试模式 |
| `CHROMA_PERSIST_DIR` | `/app/vector_store` | ChromaDB持久化目录 |
| `CHROMA_COLLECTION` | `cutter_knowledge` | ChromaDB集合名称 |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | 嵌入模型名称 |
| `EMBEDDING_DEVICE` | `cpu` | 嵌入设备（cpu/cuda） |
| `EMBEDDING_BATCH_SIZE` | `32` | 嵌入批处理大小 |
| `RABBITMQ_URL` | `amqp://rabbitmq:5672` | RabbitMQ连接地址 |
| `REDIS_URL` | `redis://redis:6379/2` | Redis连接地址 |
| `CUTTER_SERVICE_URL` | `http://cutter-management:8001` | 刀具管理服务地址 |
| `JWT_SECRET_KEY` | - | JWT密钥（必须配置） |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `LOG_FORMAT` | `json` | 日志格式 |
| `MODEL_CACHE_DIR` | `/app/models` | 模型缓存目录 |
| `MAX_SEQUENCE_LENGTH` | `512` | 最大序列长度 |
| `SEARCH_DEFAULT_TOP_K` | `10` | 默认搜索结果数量 |
| `SEARCH_MAX_TOP_K` | `100` | 最大搜索结果数量 |
| `SEARCH_SIMILARITY_THRESHOLD` | `0.7` | 相似度阈值 |
| `RECOMMENDATION_MAX_RESULTS` | `5` | 最大推荐结果数量 |
| `RECOMMENDATION_MIN_CONFIDENCE` | `0.6` | 最小置信度 |
| `SCENARIO_MATCHING_MAX_RESULTS` | `10` | 最大场景匹配结果数量 |
| `SCENARIO_MATCHING_MIN_SCORE` | `0.5` | 最小匹配分数 |

### 模型配置

1. **嵌入模型**：默认使用 `all-MiniLM-L6-v2`
2. **设备选择**：支持CPU和CUDA（GPU）
3. **批处理大小**：根据内存调整
4. **模型缓存**：本地缓存模型文件

### 向量存储配置

1. **ChromaDB**：本地向量数据库
2. **持久化目录**：向量数据存储位置
3. **集合管理**：按业务划分集合

## 开发指南

### 项目结构

```
ai-service/
├── src/
│   ├── semantic_search/           # 语义搜索子域
│   │   ├── domain/
│   │   ├── application/
│   │   └── infrastructure/
│   ├── recommendation/            # 推荐子域
│   │   ├── domain/
│   │   ├── application/
│   │   └── infrastructure/
│   ├── scenario_matching/         # 场景匹配子域
│   │   ├── domain/
│   │   ├── application/
│   │   └── infrastructure/
│   └── shared/                    # 共享内核
│       ├── events/
│       └── infrastructure/
├── api/
│   ├── app.py                    # FastAPI应用
│   ├── routes/
│   │   ├── search.py
│   │   ├── recommendations.py
│   │   ├── scenarios.py
│   │   ├── embeddings.py
│   │   ├── vectors.py
│   │   └── health.py
│   └── dependencies.py
├── tests/
│   ├── unit/
│   │   ├── semantic_search/
│   │   ├── recommendation/
│   │   └── scenario_matching/
│   └── integration/
│       └── api/
├── scripts/
│   ├── download_models.py
│   └── init_vector_store.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
├── README.md
└── .env.example
```

### 添加新子域

1. 在 `src/` 创建新的子域目录
2. 实现领域模型、服务和仓库
3. 实现应用层命令和查询
4. 在 `api/routes/` 添加API路由
5. 在 `api/dependencies.py` 添加依赖注入

### 添加新模型

1. 在 `src/shared/infrastructure/ml/` 添加新模型
2. 实现模型加载和推理接口
3. 更新配置文件
4. 添加模型测试

### 事件处理

```python
# 监听刀具事件
class CutterEventHandler:
    async def handle_cutter_created(self, event: CutterCreatedEvent):
        """处理刀具创建事件"""
        # 1. 获取刀具数据
        # 2. 生成嵌入向量
        # 3. 添加到向量索引
    
    async def handle_cutter_updated(self, event: CutterUpdatedEvent):
        """处理刀具更新事件"""
        # 1. 获取更新后的刀具数据
        # 2. 重新生成嵌入向量
        # 3. 更新向量索引
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

# 测试嵌入模型
python -c "from src.shared.infrastructure.ml.embedding_model import EmbeddingModel; model = EmbeddingModel(); print(model.encode('test'))"
```

## 监控

### 健康检查

```bash
curl http://localhost:8002/health
```

### 指标监控

服务暴露Prometheus指标：
- `http_requests_total` - HTTP请求总数
- `http_request_duration_seconds` - 请求持续时间
- `embedding_generation_duration_seconds` - 嵌入生成时间
- `vector_search_duration_seconds` - 向量搜索时间
- `model_load_duration_seconds` - 模型加载时间
- `vector_store_size` - 向量存储大小

### 日志

结构化日志格式：
```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "level": "info",
  "message": "Semantic search completed",
  "query": "carbide end mill for steel",
  "results_count": 10,
  "duration_ms": 150,
  "similarity_threshold": 0.7
}
```

## 部署

### Docker部署

```bash
# 构建镜像
docker build -t cnc-ai-service:latest .

# 运行容器
docker run -d \
  --name cnc-ai-service \
  -p 8002:8002 \
  -v ./vector_store:/app/vector_store \
  --env-file .env \
  cnc-ai-service:latest
```

### GPU支持

```bash
# 使用GPU版本
docker run -d \
  --name cnc-ai-service \
  --gpus all \
  -p 8002:8002 \
  -v ./vector_store:/app/vector_store \
  --env-file .env \
  -e EMBEDDING_DEVICE=cuda \
  cnc-ai-service:latest
```

### Kubernetes部署

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cnc-ai-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: cnc-ai-service
  template:
    metadata:
      labels:
        app: cnc-ai-service
    spec:
      containers:
      - name: cnc-ai-service
        image: cnc-ai-service:latest
        ports:
        - containerPort: 8002
        envFrom:
        - configMapRef:
            name: ai-service-config
        - secretRef:
            name: ai-service-secrets
        volumeMounts:
        - name: vector-store
          mountPath: /app/vector_store
      volumes:
      - name: vector-store
        persistentVolumeClaim:
          claimName: vector-store-pvc
```

## 故障排除

### 常见问题

1. **模型加载失败**
   - 检查网络连接（首次需要下载模型）
   - 检查磁盘空间
   - 检查模型路径配置

2. **ChromaDB连接失败**
   - 检查 `CHROMA_PERSIST_DIR` 配置
   - 确保目录有写入权限
   - 检查磁盘空间

3. **内存不足**
   - 减小 `EMBEDDING_BATCH_SIZE`
   - 使用更小的嵌入模型
   - 增加系统内存

4. **搜索结果不准确**
   - 调整 `SEARCH_SIMILARITY_THRESHOLD`
   - 检查嵌入模型质量
   - 优化查询文本

### 调试模式

```bash
# 启用调试模式
export DEBUG=true
export LOG_LEVEL=DEBUG

# 启动服务
uvicorn api.app:app --reload --port 8002
```

## 性能优化

### 模型优化

- 使用量化模型减少内存占用
- 使用GPU加速嵌入生成
- 批处理提高吞吐量

### 向量存储优化

- 合理设置向量维度
- 使用索引加速搜索
- 定期清理无用向量

### 缓存策略

- Redis缓存热点查询
- 本地缓存频繁访问的数据
- 预计算常用嵌入

## 安全建议

1. **生产环境必须使用HTTPS**
2. **定期更换JWT密钥**
3. **限制API访问权限**
4. **监控异常请求**
5. **定期备份向量数据**
6. **定期更新依赖包**

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License