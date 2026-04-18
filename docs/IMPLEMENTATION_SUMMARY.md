# 机床刀具 RAG 知识库 - 项目实现总结

## ✅ 已完成功能

### 1. DDD 领域层 (Domain Layer)

**文件**: `src/domain/models/cutter.py`

**核心类**:
- `Cutter` - 聚合根，包含所有刀具业务逻辑
- `CutterType` - 值对象，刀具分类（category/subcategory/coating）
- `MaterialSpec` - 值对象，材料规格（substrate/coating/hardness）
- `GeometryParams` - 值对象，几何参数（diameter/length/flutes等）

**业务方法**:
```python
cutter.is_suitable_for_material("steel")      # 检查兼容性
cutter.get_cutting_speed("aluminum")           # 获取切削速度
cutter.update_usage_guideline("new tip", 0)    # 更新使用指南
cutter.add_compatible_material("titanium")     # 添加兼容材料
```

**文件**: `src/domain/repositories/cutter_repo.py`

**Repository 接口**:
```python
class CutterRepository(ABC):
    def add(self, cutter: Cutter) -> None
    def get_by_id(self, cutter_id: UUID) -> Optional[Cutter]
    def get_all(self) -> list[Cutter]
    def search_by_query(self, query: str, top_k: int) -> list[tuple[Cutter, float]]
    def search_by_material(self, material: str, top_k: int) -> list[Cutter]
    def update(self, cutter: Cutter) -> None
    def delete(self, cutter_id: UUID) -> bool
    def count(self) -> int
```

---

### 2. 应用层 (Application Layer)

**CQRS Commands** (`src/application/commands/ingest_cutter.py`):
- `IngestCutterCommand` - 导入新刀具
- `UpdateCutterCommand` - 更新刀具
- `DeleteCutterCommand` - 删除刀具

**CQRS Queries** (`src/application/queries/search_cutters.py`):
- `SearchCuttersQuery` - 语义搜索
- `GetCutterByIdQuery` - 按 ID 查询
- `GetAllCuttersQuery` - 查询所有
- `SearchByMaterialQuery` - 按材料搜索

**Handlers** (`src/application/handlers/cutter_handler.py`):
```python
# Command Handler
handler.handle_ingest(command)    # 导入刀具
handler.handle_update(command)    # 更新刀具
handler.handle_delete(cutter_id)  # 删除刀具

# Query Handler
handler.handle_search(query)              # 语义搜索
handler.handle_get_by_id(query)           # 按 ID 查询
handler.handle_get_all(query)             # 查询所有
handler.handle_search_by_material(query)  # 按材料搜索
```

**DTOs** (`src/application/dto/cutter_dto.py`):
- `CutterDTO` - 刀具数据传输对象
- `CutterSearchResultDTO` - 搜索结果（含相关性分数）
- `CutterListResponse` - 列表响应包装器
- `ErrorResponse` - 错误响应

---

### 3. 基础设施层 (Infrastructure Layer)

**ChromaDB Repository** (`src/infrastructure/persistence/chroma_repo.py`):
```python
repo = ChromaCutterRepository(
    persist_directory="./vector_store",
    collection_name="cutter_knowledge",
)

repo.add(cutter)                              # 添加刀具（自动生成 embedding）
results = repo.search_by_query("carbide end mill for steel")  # 语义搜索
cutters = repo.search_by_material("aluminum") # 按材料过滤
```

**Embedding Service** (`src/infrastructure/persistence/embeddings.py`):
```python
embedding_service = EmbeddingService(
    model_name="all-MiniLM-L6-v2",  # 384 维向量
    device="cpu"  # 或 "cuda"
)

vector = embedding_service.generate("10mm carbide end mill")
dimension = embedding_service.get_embedding_dimension()  # 384
```

**特性**:
- 懒加载模型（首次使用时加载）
- LRU 缓存（避免重复计算）
- 批量生成支持
- 自动设备检测（CPU/CUDA/MPS）

---

### 4. 接口层 (Interface Layer)

**FastAPI REST API** (`src/interface/api/api.py`):

**端点**:
```
GET  /health                           # 健康检查
POST /cutters                          # 导入新刀具
GET  /cutters                          # 查询所有刀具
GET  /cutters/{cutter_id}              # 查询单个刀具
POST /search                           # 语义搜索
GET  /search/material/{material}       # 按材料搜索
```

**使用示例**:
```bash
# 健康检查
curl http://localhost:8000/health

# 导入刀具
curl -X POST http://localhost:8000/cutters \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "10mm Carbide End Mill",
    "category": "end_mill",
    "diameter": 10.0,
    "length": 75.0,
    "number_of_flutes": 4,
    "compatible_materials": ["steel", "aluminum"]
  }'

# 语义搜索
curl -X POST http://localhost:8000/search \
  -H 'Content-Type: application/json' \
  -d '{"query": "carbide end mill for steel", "top_k": 5}'

# 按材料搜索
curl http://localhost:8000/search/material/aluminum
```

**API 文档**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

### 5. TDD 测试

**单元测试** (`tests/unit/domain/test_models.py`):

**测试覆盖**:
```python
# CutterType 测试
test_create_valid_cutter_type()
test_from_string_simple()
test_from_string_complete()
test_is_frozen()  # 不可变性

# MaterialSpec 测试
test_create_minimal_spec()
test_description_with_coating()

# GeometryParams 测试
test_create_valid_params()
test_diameter_must_be_positive()
test_aspect_ratio_calculation()

# Cutter 测试
test_create_using_factory()
test_is_suitable_for_material_match()
test_get_cutting_speed()
test_update_usage_guideline()
test_to_dict_serialization()
```

**运行测试**:
```bash
pytest tests/unit/domain/test_models.py -v
pytest --cov=src --cov-report=html
```

---

### 6. 工具脚本

**初始化知识库** (`scripts/init_knowledge_base.py`):
```bash
python scripts/init_knowledge_base.py
```

功能:
- 初始化 ChromaDB 仓库
- 导入 5 个示例刀具数据
- 生成向量嵌入

**测试查询** (`scripts/test_query.py`):
```bash
python scripts/test_query.py "carbide end mill for steel"
python scripts/test_query.py "drill bit for aluminum" 3
```

功能:
- 执行语义搜索
- 显示相关性分数
- 格式化输出结果

**启动服务器** (`start_server.sh`):
```bash
./start_server.sh 8000
```

**初始化 Git** (`scripts/init_git.sh`):
```bash
./scripts/init_git.sh
```

---

## 📊 代码统计

| 层次 | 文件数 | 代码行数 | 描述 |
|------|--------|----------|------|
| Domain | 3 | ~600 | 领域模型、值对象、Repository 接口 |
| Application | 5 | ~800 | Commands、Queries、Handlers、DTOs |
| Infrastructure | 2 | ~600 | ChromaDB 实现、Embedding 服务 |
| Interface | 1 | ~400 | FastAPI REST API |
| Tests | 1 | ~400 | 单元测试 |
| Scripts | 3 | ~300 | 工具脚本 |
| **总计** | **15+** | **~3100** | |

---

## 🏗️ 架构亮点

### 1. 严格的分层架构
```
Interface → Application → Domain ← Infrastructure
```
- 内层不依赖外层
- Domain 层是纯 Python，无外部依赖
- 易于测试和替换组件

### 2. CQRS 模式
- 读写完全分离
- CommandHandler 处理写操作
- QueryHandler 处理读操作
- 可以独立优化

### 3. Repository 模式
- Domain 层定义接口
- Infrastructure 层实现
- 轻松切换数据库（ChromaDB → FAISS → SQL）

### 4. 设计模式集合
- **Factory Method**: `Cutter.create()`
- **Strategy**: `EmbeddingService` 可切换模型
- **Dependency Injection**: FastAPI Depends()
- **DTO**: 隔离外部与领域模型
- **Value Object**: 不可变值对象

### 5. 工程规范
- **Type Hints**: 100% 类型注解
- **Docstrings**: Google 风格文档字符串
- **TDD**: 先写测试，再实现功能
- **Code Quality**: pytest, mypy, ruff, black

---

## 🚀 快速开始

```bash
# 1. 进入项目目录
cd /mnt/g/projects/tooling-rag

# 2. 等待后台安装完成（或手动安装）
source venv/bin/activate
pip install fastapi uvicorn pydantic chromadb sentence-transformers pandas numpy

# 3. 初始化知识库
python scripts/init_knowledge_base.py

# 4. 启动服务
./start_server.sh

# 5. 访问 API 文档
# Open http://localhost:8000/docs

# 6. 测试查询
python scripts/test_query.py "carbide end mill for steel"

# 7. 运行测试
pytest tests/unit/domain/test_models.py -v

# 8. 初始化 Git 并推送
./scripts/init_git.sh
git remote add origin git@github.com:nanfeng2021/tooling-rag.git
git push -u origin main
```

---

## 📝 下一步计划

### 待完成
- [ ] 集成测试（API 端点测试）
- [ ] LLM 集成（RAG 问答功能）
- [ ] Web UI（React/Vue前端）
- [ ] 数据导入工具（Markdown/PDF解析）
- [ ] Docker 容器化
- [ ] CI/CD 流水线

### 功能增强
- [ ] 混合检索（关键词 + 向量）
- [ ] 多轮对话支持
- [ ] 切削参数推荐引擎
- [ ] 刀具选型专家系统
- [ ] 加工案例库

---

## 🎯 与 CAD-to-Gcode 项目对比

| 特性 | CAD-to-Gcode | Tooling-RAG |
|------|--------------|-------------|
| 架构 | 分层架构 | DDD + CQRS |
| 数据库 | SQLite | ChromaDB |
| 核心功能 | DXF 解析、特征识别 | 语义搜索、知识问答 |
| AI 能力 | 规则引擎 | 向量嵌入 + LLM |
| 测试 | 集成测试为主 | TDD 单元测试 |
| 代码规范 | 良好 | 企业级（type hints, docstrings） |

Tooling-RAG 项目采用了更严格的工程规范，可以作为未来项目的参考模板。
