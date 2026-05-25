"""
Embedding Model Service

复用原embeddings.py逻辑，提供嵌入向量生成服务。
使用sentence-transformers模型，支持懒加载和缓存。
"""

import os
from functools import lru_cache


class EmbeddingModel:
    """嵌入模型服务"""

    _model_cache: dict[str, any] = {}

    def __init__(
        self,
        model_name: str | None = None,
        device: str | None = None,
    ) -> None:
        self._model_name = model_name or os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self._device = device or self._auto_detect_device()
        self._model = None

    @staticmethod
    def _auto_detect_device() -> str:
        """自动检测最佳设备"""
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
            if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                return "mps"
        except ImportError:
            pass
        return "cpu"

    def _load_model(self) -> None:
        """懒加载模型"""
        if self._model is not None:
            return

        if self._model_name in EmbeddingModel._model_cache:
            self._model = EmbeddingModel._model_cache[self._model_name]
            return

        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self._model_name, device=self._device)
            EmbeddingModel._model_cache[self._model_name] = self._model
        except ImportError as e:
            raise ImportError(
                "sentence-transformers is required. Install with: pip install sentence-transformers"
            ) from e

    @lru_cache(maxsize=10000)
    def generate(self, text: str) -> list[float]:
        """生成单个文本的嵌入向量"""
        self._load_model()
        embedding = self._model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        return embedding.tolist()

    def generate_batch(self, texts: list[str]) -> list[list[float]]:
        """批量生成嵌入向量"""
        self._load_model()
        embeddings = self._model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=len(texts) > 10,
        )
        return [emb.tolist() for emb in embeddings]

    def get_dimension(self) -> int:
        """获取嵌入向量维度"""
        self._load_model()
        return self._model.get_sentence_embedding_dimension()


# 全局单例
_embedding_model: EmbeddingModel | None = None


def get_embedding_model() -> EmbeddingModel:
    """获取嵌入模型单例"""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = EmbeddingModel()
    return _embedding_model
