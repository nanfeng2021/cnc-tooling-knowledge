"""
AI Service - Lightweight ONNX Runtime version

提供嵌入生成和向量存储功能，通过 REST API 暴露给主后端服务。
使用 ONNX Runtime 替代 PyTorch，大幅减小镜像体积。

主要功能：
- POST /embeddings - 生成文本嵌入
- POST /embeddings/batch - 批量生成嵌入
- POST /vectors/add - 添加向量到 ChromaDB
- POST /vectors/search - 语义搜索
- PUT /vectors/{id} - 更新向量
- DELETE /vectors/{id} - 删除向量
- GET /health - 健康检查
"""

import json
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import chromadb
import numpy as np
from chromadb.config import Settings
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# 全局变量存储 ChromaDB 客户端和集合
chroma_client = None
collection = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global chroma_client, collection

    # 启动时初始化 ChromaDB
    persist_dir = os.getenv("CHROMA_PERSIST_DIR", "/app/vector_store")
    collection_name = os.getenv("CHROMA_COLLECTION", "cutter_knowledge")

    print(f"[AI Service] Initializing ChromaDB at {persist_dir}")
    chroma_client = chromadb.PersistentClient(
        path=persist_dir,
        settings=Settings(
            anonymized_telemetry=False,
            allow_reset=True,
        ),
    )
    collection = chroma_client.get_or_create_collection(
        name=collection_name,
        metadata={"description": "Cutter knowledge base"},
    )
    print(f"[AI Service] ChromaDB collection '{collection_name}' ready, {collection.count()} documents")

    yield

    # 关闭时清理
    print("[AI Service] Shutting down...")


app = FastAPI(
    title="CNC Tooling AI Service (ONNX)",
    description="AI microservice for embeddings and vector storage using ONNX Runtime",
    version="1.0.0",
    lifespan=lifespan,
)


# ============ Request/Response Models ============


class EmbeddingRequest(BaseModel):
    """单文本嵌入请求"""
    text: str = Field(..., description="要嵌入的文本")


class BatchEmbeddingRequest(BaseModel):
    """批量嵌入请求"""
    texts: list[str] = Field(..., description="要嵌入的文本列表")


class EmbeddingResponse(BaseModel):
    """嵌入响应"""
    embedding: list[float]
    dimension: int


class BatchEmbeddingResponse(BaseModel):
    """批量嵌入响应"""
    embeddings: list[list[float]]
    dimension: int
    count: int


class VectorAddRequest(BaseModel):
    """添加向量请求"""
    id: str = Field(..., description="向量ID")
    text: str = Field(..., description="文档文本（用于生成嵌入）")
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")


class VectorUpdateRequest(BaseModel):
    """更新向量请求"""
    text: str = Field(..., description="新的文档文本")
    metadata: dict[str, Any] = Field(default_factory=dict, description="新的元数据")


class VectorSearchRequest(BaseModel):
    """向量搜索请求"""
    query: str = Field(..., description="搜索查询文本")
    top_k: int = Field(default=5, ge=1, le=100, description="返回结果数量")
    filters: dict[str, Any] | None = Field(default=None, description="元数据过滤条件")


class VectorSearchResult(BaseModel):
    """搜索结果项"""
    id: str
    score: float
    metadata: dict[str, Any] | None = None
    document: str | None = None


class VectorSearchResponse(BaseModel):
    """搜索响应"""
    results: list[VectorSearchResult]
    total: int


class BulkAddRequest(BaseModel):
    """批量添加向量请求"""
    items: list[VectorAddRequest]


class BulkAddResponse(BaseModel):
    """批量添加响应"""
    added: int
    failed: int
    errors: list[dict[str, str]] = Field(default_factory=list)


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    collection_count: int
    model_info: dict[str, Any]


# ============ ONNX Embedding Model (lazy load) ============

_embedding_model = None
_tokenizer = None
_model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


def get_embedding_model():
    """延迟加载 ONNX 嵌入模型"""
    global _embedding_model, _tokenizer
    if _embedding_model is None:
        print(f"[AI Service] Loading ONNX embedding model: {_model_name}")
        try:
            from optimum.onnxruntime import ORTModelForFeatureExtraction
            from transformers import AutoTokenizer

            # 加载 ONNX 模型（自动导出）
            _embedding_model = ORTModelForFeatureExtraction.from_pretrained(
                f"sentence-transformers/{_model_name}",
                export=True
            )
            _tokenizer = AutoTokenizer.from_pretrained(f"sentence-transformers/{_model_name}")
            print(f"[AI Service] ONNX model loaded successfully")
        except Exception as e:
            print(f"[AI Service] Failed to load ONNX model: {e}")
            # Fallback: 使用更简单的加载方式
            from sentence_transformers import SentenceTransformer
            _embedding_model = SentenceTransformer(_model_name, device="cpu")
            print(f"[AI Service] Fallback: Loaded SentenceTransformer model")

    return _embedding_model


def mean_pooling(model_output, attention_mask):
    """平均池化"""
    import torch
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


def generate_embedding(text: str) -> list[float]:
    """生成单个文本的嵌入向量"""
    model = get_embedding_model()

    # 检查是否是 ONNX 模型
    if hasattr(model, 'generate'):
        # ONNX 模型
        inputs = _tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        outputs = model.generate(**inputs)
        # 平均池化得到句子嵌入
        import torch
        embedding = mean_pooling(outputs, inputs['attention_mask'])
        # 归一化
        embedding = torch.nn.functional.normalize(embedding, p=2, dim=1)
        return embedding.detach().numpy()[0].tolist()
    else:
        # SentenceTransformer 模型
        embedding = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        return embedding.tolist()


def generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """批量生成嵌入向量"""
    model = get_embedding_model()

    # 检查是否是 ONNX 模型
    if hasattr(model, 'generate'):
        # ONNX 模型
        inputs = _tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=512)
        outputs = model.generate(**inputs)
        # 平均池化得到句子嵌入
        import torch
        embeddings = mean_pooling(outputs, inputs['attention_mask'])
        # 归一化
        embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
        return [emb.tolist() for emb in embeddings.detach().numpy()]
    else:
        # SentenceTransformer 模型
        embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        return [emb.tolist() for emb in embeddings]


# ============ API Endpoints ============


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    model = get_embedding_model()

    # 获取模型维度
    if hasattr(model, 'generate'):
        # ONNX 模型，使用默认维度
        dimension = 384  # all-MiniLM-L6-v2 默认维度
    else:
        dimension = model.get_sentence_embedding_dimension()

    return HealthResponse(
        status="healthy",
        collection_count=collection.count() if collection else 0,
        model_info={
            "name": _model_name,
            "dimension": dimension,
            "device": "cpu",
            "backend": "onnx" if hasattr(model, 'generate') else "pytorch",
        },
    )


@app.post("/embeddings", response_model=EmbeddingResponse)
async def create_embedding(request: EmbeddingRequest):
    """生成单个文本嵌入"""
    try:
        embedding = generate_embedding(request.text)
        return EmbeddingResponse(
            embedding=embedding,
            dimension=len(embedding),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/embeddings/batch", response_model=BatchEmbeddingResponse)
async def create_embeddings_batch(request: BatchEmbeddingRequest):
    """批量生成嵌入"""
    try:
        embeddings = generate_embeddings_batch(request.texts)
        return BatchEmbeddingResponse(
            embeddings=embeddings,
            dimension=len(embeddings[0]) if embeddings else 0,
            count=len(embeddings),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vectors/add", response_model=dict)
async def add_vector(request: VectorAddRequest):
    """添加向量到 ChromaDB"""
    try:
        embedding = generate_embedding(request.text)

        # 处理元数据，确保 ChromaDB 兼容
        meta = flatten_metadata(request.metadata)
        meta["_data"] = json.dumps(request.metadata, ensure_ascii=False, default=str)

        collection.add(
            ids=[request.id],
            embeddings=[embedding],
            metadatas=[meta],
            documents=[request.text],
        )
        return {"status": "ok", "id": request.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vectors/bulk-add", response_model=BulkAddResponse)
async def add_vectors_bulk(request: BulkAddRequest):
    """批量添加向量"""
    added = 0
    failed = 0
    errors = []

    for item in request.items:
        try:
            embedding = generate_embedding(item.text)
            meta = flatten_metadata(item.metadata)
            meta["_data"] = json.dumps(item.metadata, ensure_ascii=False, default=str)

            collection.add(
                ids=[item.id],
                embeddings=[embedding],
                metadatas=[meta],
                documents=[item.text],
            )
            added += 1
        except Exception as e:
            failed += 1
            errors.append({"id": item.id, "error": str(e)})

    return BulkAddResponse(added=added, failed=failed, errors=errors)


@app.post("/vectors/search", response_model=VectorSearchResponse)
async def search_vectors(request: VectorSearchRequest):
    """语义搜索"""
    try:
        query_embedding = generate_embedding(request.query)

        where_filter = None
        if request.filters:
            where_filter = build_where_filter(request.filters)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=request.top_k,
            where=where_filter,
            include=["metadatas", "distances", "documents"],
        )

        search_results = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i] if results["distances"] else 0.0
                similarity = 1.0 / (1.0 + distance)

                search_results.append(VectorSearchResult(
                    id=doc_id,
                    score=similarity,
                    metadata=results["metadatas"][0][i] if results["metadatas"] else None,
                    document=results["documents"][0][i] if results["documents"] else None,
                ))

        return VectorSearchResponse(
            results=search_results,
            total=len(search_results),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/vectors/{vector_id}", response_model=dict)
async def update_vector(vector_id: str, request: VectorUpdateRequest):
    """更新向量"""
    try:
        embedding = generate_embedding(request.text)
        meta = flatten_metadata(request.metadata)
        meta["_data"] = json.dumps(request.metadata, ensure_ascii=False, default=str)

        collection.update(
            ids=[vector_id],
            embeddings=[embedding],
            metadatas=[meta],
            documents=[request.text],
        )
        return {"status": "ok", "id": vector_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/vectors/{vector_id}", response_model=dict)
async def delete_vector(vector_id: str):
    """删除向量"""
    try:
        collection.delete(ids=[vector_id])
        return {"status": "ok", "id": vector_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/vectors/{vector_id}", response_model=dict)
async def get_vector(vector_id: str):
    """获取向量详情"""
    try:
        result = collection.get(
            ids=[vector_id],
            include=["metadatas", "documents"],
        )
        if not result["ids"]:
            raise HTTPException(status_code=404, detail="Vector not found")

        return {
            "id": result["ids"][0],
            "metadata": result["metadatas"][0] if result["metadatas"] else None,
            "document": result["documents"][0] if result["documents"] else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/vectors", response_model=dict)
async def list_vectors(limit: int = 100, offset: int = 0):
    """列出向量"""
    try:
        result = collection.get(
            limit=limit,
            offset=offset,
            include=["metadatas"],
        )
        return {
            "ids": result["ids"],
            "metadatas": result["metadatas"],
            "total": collection.count(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Helper Functions ============


def flatten_metadata(data: dict) -> dict:
    """将嵌套字典展平为 ChromaDB 兼容格式"""
    flat: dict = {}
    for key, value in data.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                coerced = coerce_value(sub_value)
                if coerced is not None:
                    flat[f"{key}.{sub_key}"] = coerced
        else:
            coerced = coerce_value(value)
            if coerced is not None:
                flat[key] = coerced
    return flat


def coerce_value(value):
    """转换值为 ChromaDB 兼容类型"""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def build_where_filter(filters: dict) -> dict:
    """构建 ChromaDB where 过滤条件"""
    where = {}
    for key, value in filters.items():
        if isinstance(value, (str, int, float)):
            where[key] = value
    return where if where else None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)