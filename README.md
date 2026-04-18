# CNC Tooling Knowledge Base

**面向 2 轴/3 轴/5 轴 CNC 机床的刀具知识库**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**基于 RAG (Retrieval-Augmented Generation) 的智能刀具知识检索系统**

---

## 🎯 项目定位

为 CNC 编程人员、工艺工程师提供：
- 🔍 **智能语义搜索** - 自然语言查询刀具信息
- 🛠️ **多轴加工支持** - 覆盖 2 轴车削、3 轴铣削、5 轴联动加工
- 🏭 **厂商数据集成** - Sandvik、Kennametal、Mitsubishi、OSG、YAMAWA、ZCC 等
- ⚙️ **切削参数推荐** - 基于材料和工艺的智能化参数推荐
- 💬 **知识问答** - 集成 LLM 的智能问答系统

### 支持的刀具类型
- **车削刀具** - 外圆车刀、内孔车刀、切槽刀、螺纹刀
- **铣削刀具** - 立铣刀、面铣刀、球头刀、圆鼻刀
- **孔加工刀具** - 钻头、扩孔钻、铰刀、镗刀
- **螺纹加工** - 丝锥、板牙、螺纹铣刀
- **齿轮加工** - 滚刀、插齿刀、剃齿刀

### 集成的刀具厂商
| 国际品牌 | 国内品牌 |
|----------|----------|
| Sandvik Coromant | ZCC 株洲钻石 |
| Kennametal | OSG 中国 |
| Mitsubishi Hitachi | YAMAWA 雅马哈 |
| Walter | Harbin First Tool |
| Iscar | Chengdu Diamond |

---

## 🏗️ 技术架构

采用 **DDD (Domain-Driven Design) + CQRS** 的企业级架构：

```
┌─────────────────────────────────────────┐
│         Interface Layer (FastAPI)        │
├─────────────────────────────────────────┤
│     Application Layer (CQRS Handlers)    │
├─────────────────────────────────────────┤
│       Domain Layer (Business Logic)      │
├─────────────────────────────────────────┤
│   Infrastructure Layer (ChromaDB + LLM)  │
└─────────────────────────────────────────┘
```

### 核心技术栈
- **Backend**: Python 3.10+, FastAPI, Pydantic v2
- **Vector DB**: ChromaDB (语义检索)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **LLM**: 支持 OpenAI / 本地模型
- **Architecture**: DDD + CQRS + Repository Pattern

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd cnc-tooling-knowledge
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# 安装 LLM 和爬虫额外依赖
pip install openai ollama requests beautifulsoup4 lxml
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 OpenAI API Key 或其他配置
```

### 3. 抓取刀具厂商数据（可选）

```bash
# 爬取主流刀具厂商产品数据
python scripts/scrape_vendor_data.py --vendor all

# 或只爬取特定厂商
python scripts/scrape_vendor_data.py --vendor sandvik
python scripts/scrape_vendor_data.py --vendor kennametal
```

### 4. 导入知识库

```bash
# 将爬取的刀具数据导入向量数据库
python scripts/import_vendor_data.py
```

### 5. 初始化知识库

```bash
# 导入示例刀具数据（如果还没导入厂商数据）
python scripts/init_knowledge_base.py
```

### 6. 启动服务

```bash
./start_server.sh
# 或
python -m uvicorn src.interface.api.api:app --reload --port 8000
```

访问 API 文档：**http://localhost:8000/docs**

### 7. 打开 Web UI

直接用浏览器打开：
```bash
# macOS
open webui/index.html

# Linux
xdg-open webui/index.html

# Windows (WSL)
explorer.exe webui/index.html
```

或者使用简单的 HTTP 服务器：
```bash
cd webui
python -m http.server 3000
# 访问 http://localhost:3000
```

### 8. 测试搜索

```bash
# 语义搜索
python scripts/test_query.py "carbide end mill for steel"

# LLM 智能问答
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"question": "不锈钢精加工用什么刀具好？", "top_k": 5}'

# 刀具推荐
curl -X POST http://localhost:8000/recommend/tool \
  -H 'Content-Type: application/json' \
  -d '{"workpiece_material": "stainless_steel", "operation": "finishing", "machine_type": "3-axis"}'
```

---

## 📖 API 使用示例

### 健康检查
```bash
curl http://localhost:8000/health
```

### 导入刀具
```bash
curl -X POST http://localhost:8000/cutters \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "10mm 硬质合金立铣刀",
    "category": "end_mill",
    "diameter": 10.0,
    "length": 75.0,
    "number_of_flutes": 4,
    "compatible_materials": ["steel", "stainless_steel", "aluminum"]
  }'
```

### 语义搜索
```bash
curl -X POST http://localhost:8000/search \
  -H 'Content-Type: application/json' \
  -d '{"query": "不锈钢精加工用什么刀具", "top_k": 5}'
```

### 按材料搜索
```bash
curl http://localhost:8000/search/material/aluminum
```

---

## 📁 项目结构

```
cnc-tooling-knowledge/
├── src/
│   ├── domain/                 # 领域层（业务核心）
│   │   ├── models/             # 实体与值对象
│   │   ├── repositories/       # Repository 接口
│   │   └── services/           # 领域服务
│   ├── application/            # 应用层（用例）
│   │   ├── commands/           # CQRS Commands
│   │   ├── queries/            # CQRS Queries
│   │   ├── handlers/           # Command/Query Handlers
│   │   └── dto/                # DTOs
│   ├── infrastructure/         # 基础设施层
│   │   ├── persistence/        # ChromaDB + Embedding
│   │   └── external/           # LLM Client
│   └── interface/              # 接口层
│       ├── api/                # FastAPI REST API
│       └── cli/                # CLI 工具
├── tests/                      # TDD 测试
│   ├── unit/                   # 单元测试
│   └── integration/            # 集成测试
├── scripts/                    # 工具脚本
│   ├── init_knowledge_base.py  # 初始化知识库
│   ├── test_query.py           # 测试查询
│   └── init_git.sh             # Git 初始化
├── data/                       # 数据目录
│   ├── raw/                    # 原始数据
│   └── processed/              # 处理后数据
├── docs/                       # 文档
│   ├── ARCHITECTURE.md         # 架构设计
│   └── IMPLEMENTATION_SUMMARY.md # 实现总结
├── pyproject.toml              # 项目配置
├── pytest.ini                  # 测试配置
└── README.md                   # 本文件
```

---

## 🧪 运行测试

```bash
# 所有测试
pytest

# 单元测试
pytest tests/unit/ -v

# 带覆盖率报告
pytest --cov=src --cov-report=html

# 查看 HTML 报告
open output/coverage/index.html
```

---

## 📊 代码质量

```bash
# 类型检查
mypy src/

# 代码格式化
black src/ tests/

# 代码检查
ruff check src/ tests/
```

---

## 🔧 开发指南

### 添加新的刀具类型
1. 在 `src/domain/models/value_objects.py` 中扩展 `CutterType`
2. 更新 `src/application/dto/cutter_dto.py`
3. 添加相应的测试

### 添加新的搜索方式
1. 在 `src/application/queries/` 创建新的 Query 类
2. 在 `CutterQueryHandler` 添加处理方法
3. 在 API 层添加路由

### 更换向量数据库
实现 `CutterRepository` 接口即可，无需修改业务逻辑。

---

## 📝 待办事项

- [ ] 集成 LLM 实现智能问答
- [ ] 添加 Web UI (React/Vue)
- [ ] 支持 PDF/Markdown 数据导入
- [ ] Docker 容器化部署
- [ ] CI/CD 流水线
- [ ] 混合检索（关键词 + 向量）
- [ ] 多轮对话支持

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 👤 作者

**nanfeng** - [GitHub](https://github.com/nanfeng2021)

---

**Built with ❤️ using DDD + CQRS Architecture**
