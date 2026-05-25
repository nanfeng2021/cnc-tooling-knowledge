# AI Service 版本选择指南

## 快速决策

根据您的需求选择合适的版本：

### 选择标准版 (PyTorch) 如果：
- ✅ 您需要最高精度的嵌入
- ✅ 您有充足的磁盘空间（>3GB）
- ✅ 您正在开发或测试环境
- ✅ 您需要使用特定的 sentence-transformers 模型

### 选择 ONNX 版 如果：
- ✅ 您需要平衡性能和精度
- ✅ 您希望减小镜像大小（~1.5GB）
- ✅ 您在生产环境中部署
- ✅ 您需要模型优化和导出功能

### 选择 FastEmbed 版 如果：
- ✅ 您有严格的资源限制
- ✅ 您需要快速启动时间
- ✅ 您不需要最高精度
- ✅ 您在资源受限的环境中部署

## 性能对比

| 指标 | 标准版 | ONNX版 | FastEmbed版 |
|------|--------|--------|-------------|
| **镜像大小** | ~3 GB | ~1.5 GB | ~500 MB |
| **启动时间** | 慢 | 中等 | 快 |
| **内存使用** | 高 | 中等 | 低 |
| **CPU 使用** | 高 | 中等 | 低 |
| **嵌入精度** | 最高 | 高 | 高 |
| **支持模型** | 所有 | ONNX兼容 | FastEmbed支持 |

## 使用场景

### 1. 开发环境
**推荐版本：标准版**
```bash
cd ai-service
docker build -f Dockerfile -t cnc-ai-service:dev .
docker run -p 8001:8001 cnc-ai-service:dev
```

**原因：**
- 支持所有模型，便于调试
- 精度最高，便于验证算法
- 开发环境对资源要求不敏感

### 2. 生产环境（资源充足）
**推荐版本：ONNX版**
```bash
cd ai-service
docker build -f Dockerfile.lite -t cnc-ai-service:prod .
docker run -p 8001:8001 cnc-ai-service:prod
```

**原因：**
- 镜像大小适中
- 性能和精度平衡
- 支持模型优化

### 3. 生产环境（资源受限）
**推荐版本：FastEmbed版**
```bash
cd ai-service
docker build -f Dockerfile.fastembed -t cnc-ai-service:prod .
docker run -p 8001:8001 cnc-ai-service:prod
```

**原因：**
- 镜像最小
- 启动最快
- 资源消耗最低

### 4. 边缘计算/嵌入式设备
**推荐版本：FastEmbed版**
```bash
# 使用更小的模型
docker run -e EMBEDDING_MODEL=BAAI/bge-small-en-v1.5 -p 8001:8001 cnc-ai-service:prod
```

**原因：**
- 内存占用小
- CPU 要求低
- 适合资源受限环境

## 模型选择建议

### 标准版/ONNX版模型
| 模型 | 维度 | 大小 | 速度 | 精度 | 适用场景 |
|------|------|------|------|------|---------|
| all-MiniLM-L6-v2 | 384 | ~80 MB | 中等 | 高 | 通用场景 |
| all-mpnet-base-v2 | 768 | ~420 MB | 慢 | 最高 | 高精度需求 |
| paraphrase-multilingual-MiniLM-L12-v2 | 384 | ~470 MB | 中等 | 高 | 多语言支持 |

### FastEmbed版模型
| 模型 | 维度 | 大小 | 速度 | 精度 | 适用场景 |
|------|------|------|------|------|---------|
| BAAI/bge-small-en-v1.5 | 384 | ~130 MB | 快 | 高 | 通用场景 |
| BAAI/bge-base-en-v1.5 | 768 | ~440 MB | 中等 | 最高 | 高精度需求 |
| sentence-transformers/all-MiniLM-L6-v2 | 384 | ~80 MB | 中等 | 高 | 兼容性需求 |

## 部署架构建议

### 小型部署（单机）
```yaml
# docker-compose.fastembed.yml
services:
  ai-service:
    image: cnc-ai-service:fastembed
    # ... 其他配置
```

### 中型部署（多服务）
```yaml
# docker-compose.yml
services:
  ai-service:
    image: cnc-ai-service:onnx
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2'
```

### 大型部署（集群）
```yaml
# 使用 Kubernetes
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-service
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: ai-service
        image: cnc-ai-service:onnx
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
```

## 性能优化建议

### 1. 模型预加载
```bash
# 在 Dockerfile 中预加载模型
RUN python -c "from fastembed import TextEmbedding; TextEmbedding(model_name='BAAI/bge-small-en-v1.5')"
```

### 2. 使用 SSD 存储
```bash
# 使用 SSD 存储向量数据库
docker run -v /path/to/ssd:/app/vector_store cnc-ai-service:fastembed
```

### 3. 限制资源使用
```bash
# 限制内存和 CPU
docker run -m 2g --cpus 2 cnc-ai-service:fastembed
```

### 4. 使用环境变量优化
```bash
# 设置环境变量
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4
docker run -e OMP_NUM_THREADS -e MKL_NUM_THREADS cnc-ai-service:fastembed
```

## 故障排除

### 问题：模型下载失败
**解决方案：**
```bash
# 设置代理
export HTTP_PROXY=http://proxy:port
export HTTPS_PROXY=http://proxy:port

# 或使用国内镜像
export HF_ENDPOINT=https://hf-mirror.com
```

### 问题：内存不足
**解决方案：**
```bash
# 限制 Docker 内存
docker run -m 2g cnc-ai-service:fastembed

# 或使用更小的模型
docker run -e EMBEDDING_MODEL=BAAI/bge-small-en-v1.5 cnc-ai-service:fastembed
```

### 问题：启动时间过长
**解决方案：**
```bash
# 使用 FastEmbed 版本
docker build -f Dockerfile.fastembed -t cnc-ai-service:fastembed .

# 或预加载模型
docker run -e PRELOAD_MODEL=true cnc-ai-service:fastembed
```

## 监控和日志

### 健康检查
```bash
# 检查服务状态
curl http://localhost:8001/health

# 响应示例
{
  "status": "healthy",
  "collection_count": 100,
  "model_info": {
    "name": "BAAI/bge-small-en-v1.5",
    "dimension": 384,
    "device": "cpu",
    "backend": "fastembed"
  }
}
```

### 日志查看
```bash
# 查看容器日志
docker logs cnc-ai-service

# 实时查看日志
docker logs -f cnc-ai-service
```

## 迁移指南

### 从标准版迁移到 FastEmbed版
1. 备份向量数据库
2. 重新构建镜像
3. 测试兼容性
4. 更新环境变量
5. 重新导入数据

### 从 ONNX 版迁移到 FastEmbed版
1. 检查模型兼容性
2. 测试嵌入质量
3. 更新配置
4. 重新部署

## 总结

| 场景 | 推荐版本 | 原因 |
|------|---------|------|
| 开发测试 | 标准版 | 精度高，便于调试 |
| 生产环境（资源充足） | ONNX版 | 性能平衡 |
| 生产环境（资源受限） | FastEmbed版 | 资源消耗最低 |
| 边缘计算 | FastEmbed版 | 适合资源受限环境 |
| 高精度需求 | 标准版+大模型 | 精度最高 |