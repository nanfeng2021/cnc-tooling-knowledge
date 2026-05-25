# AI Service 变体版本

本项目提供三种 AI 服务变体，满足不同场景需求：

## 版本对比

| 版本 | 镜像大小 | 依赖 | 模型 | 适用场景 |
|------|---------|------|------|---------|
| **标准版** | ~3 GB | PyTorch, sentence-transformers | all-MiniLM-L6-v2 | 开发/测试，最高精度 |
| **ONNX版** | ~1.5 GB | ONNX Runtime, optimum | all-MiniLM-L6-v2 (ONNX) | 生产环境，平衡性能 |
| **FastEmbed版** | ~500 MB | FastEmbed | BAAI/bge-small-en-v1.5 | 资源受限环境，快速启动 |

## 版本详情

### 1. 标准版 (PyTorch)

**文件:**
- `Dockerfile`
- `requirements.txt`
- `app.py`

**特点:**
- 使用 PyTorch 作为后端
- 支持所有 sentence-transformers 模型
- 精度最高，但镜像最大

**使用方法:**
```bash
# 构建
docker build -f Dockerfile -t cnc-ai-service:standard .

# 运行
docker run -p 8001:8001 cnc-ai-service:standard
```

### 2. ONNX 版

**文件:**
- `Dockerfile.lite`
- `requirements-lite.txt`
- `app_onnx.py`

**特点:**
- 使用 ONNX Runtime 替代 PyTorch
- 镜像减小约 50%
- 支持模型导出和优化

**使用方法:**
```bash
# 构建
docker build -f Dockerfile.lite -t cnc-ai-service:onnx .

# 运行
docker run -p 8001:8001 cnc-ai-service:onnx
```

### 3. FastEmbed 版

**文件:**
- `Dockerfile.fastembed`
- `requirements-fastembed.txt`
- `app_fastembed.py`

**特点:**
- 使用 FastEmbed 库（基于 ONNX Runtime）
- 镜像最小，启动最快
- 使用 BAAI/bge-small-en-v1.5 模型

**使用方法:**
```bash
# 构建
docker build -f Dockerfile.fastembed -t cnc-ai-service:fastembed .

# 运行
docker run -p 8001:8001 cnc-ai-service:fastembed
```

## Docker Compose 配置

### 标准版 (默认)
```bash
docker-compose up -d
```

### FastEmbed 版
```bash
docker-compose -f docker-compose.fastembed.yml up -d
```

## 环境变量

所有版本支持以下环境变量：

| 变量 | 默认值 | 说明 |
|------|-------|------|
| `CHROMA_PERSIST_DIR` | `/app/vector_store` | ChromaDB 持久化目录 |
| `CHROMA_COLLECTION` | `cutter_knowledge` | ChromaDB 集合名称 |
| `EMBEDDING_MODEL` | 版本相关 | 嵌入模型名称 |

## 模型对比

| 模型 | 维度 | 大小 | 速度 | 精度 |
|------|------|------|------|------|
| all-MiniLM-L6-v2 | 384 | ~80 MB | 中等 | 高 |
| BAAI/bge-small-en-v1.5 | 384 | ~130 MB | 快 | 高 |

## 性能建议

### 开发环境
- 使用 **标准版**，便于调试和测试

### 生产环境
- 使用 **ONNX 版** 或 **FastEmbed 版**
- 考虑使用 GPU 加速（需要修改 Dockerfile）

### 资源受限环境
- 使用 **FastEmbed 版**
- 调整 `CHROMA_PERSIST_DIR` 到 SSD 存储

## 故障排除

### 模型下载失败
```bash
# 设置代理
export HTTP_PROXY=http://proxy:port
export HTTPS_PROXY=http://proxy:port

# 或使用国内镜像
export HF_ENDPOINT=https://hf-mirror.com
```

### 内存不足
```bash
# 限制 Docker 内存
docker run -m 2g cnc-ai-service:fastembed
```

### ChromaDB 性能
```bash
# 使用 SSD 存储
docker run -v /path/to/ssd:/app/vector_store cnc-ai-service:fastembed
```