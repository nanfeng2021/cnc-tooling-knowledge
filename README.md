# 机床刀具 RAG 知识库

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**基于 RAG (Retrieval-Augmented Generation) 的机床刀具知识问答系统**

---

## 🎯 项目目标

构建一个智能的机床刀具知识库，支持：
- 📚 刀具参数、使用说明、加工案例的知识存储
- 🔍 语义搜索和智能检索
- 💬 自然语言问答（集成 LLM）
- 📊 刀具选型推荐

---

## 🚀 快速开始

### 安装依赖

```bash
cd tooling-rag
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 运行服务

```bash
# 初始化知识库
python scripts/init_knowledge_base.py

# 启动 API 服务
python -m uvicorn src.web.api:app --reload --host 0.0.0.0 --port 8000
```

访问 API 文档：http://localhost:8000/docs

### 测试问答

```bash
python scripts/test_query.py "不锈钢加工用什么刀具？"
```

---

## 📁 项目结构

```
tooling-rag/
├── src/
│   ├── data/                    # 数据处理模块
│   │   ├── loader.py            # 数据加载器
│   │   └── models.py            # 数据模型
│   ├── knowledge/               # 知识库核心
│   │   ├── indexer.py           # 向量索引
│   │   └── store.py             # 向量存储
│   ├── retrieval/               # 检索模块
│   │   ├── retriever.py         # 语义检索器
│   │   └── ranker.py            # 结果排序
│   └── web/                     # Web API
│       └── api.py               # FastAPI 应用
├── data/
│   ├── raw/                     # 原始数据
│   └── processed/               # 处理后的数据
├── scripts/                     # 工具脚本
├── tests/                       # 测试
└── requirements.txt             # 依赖
```

---

## 🔧 核心功能

### 1. 数据加载
- 支持 Markdown、JSON、CSV 格式
- 自动分块和元数据提取

### 2. 向量嵌入
- 使用 sentence-transformers 生成嵌入
- 支持多种嵌入模型

### 3. 语义检索
- 余弦相似度搜索
- 混合检索（关键词 + 向量）

### 4. 智能问答
- RAG 模式：检索 + 生成
- 支持上下文多轮对话

---

## 📊 数据来源

- 刀具厂商技术手册
- 加工工艺案例
- 刀具选型指南
- 切削参数数据库

---

## 🛠️ 技术栈

- **后端**: Python 3.10+, FastAPI
- **向量数据库**: Chroma / FAISS
- **嵌入模型**: sentence-transformers
- **LLM 集成**: OpenAI / 本地模型

---

## 📝 License

MIT License
