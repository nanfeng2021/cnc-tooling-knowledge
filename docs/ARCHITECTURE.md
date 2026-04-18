# 工程架构设计文档

## 📐 架构概览

本项目采用 **DDD (Domain-Driven Design) + CQRS + Clean Architecture** 的组合架构模式，确保代码的可维护性、可测试性和可扩展性。

```
┌─────────────────────────────────────────────────────────────┐
│                      Interface Layer                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   REST API      │  │   CLI Interface │  │   Web UI     │ │
│  │   (FastAPI)     │  │   (Typer)       │  │   (React)    │ │
│  └────────┬────────┘  └────────┬────────┘  └──────────────┘ │
└───────────┼────────────────────┼─────────────────────────────┘
            │                    │
            ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Command/Query Handlers                      │ │
│  │  ┌──────────────────┐  ┌────────────────────────────┐   │ │
│  │  │ CutterCommand    │  │ CutterQueryHandler         │   │ │
│  │  │ Handler          │  │                            │   │ │
│  │  └──────────────────┘  └────────────────────────────┘   │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │  Commands (Write)        │  Queries (Read)             │ │
│  │  - IngestCutterCommand   │  - SearchCuttersQuery       │ │
│  │  - UpdateCutterCommand   │  - GetCutterByIdQuery       │ │
│  │  - DeleteCutterCommand   │  - GetAllCuttersQuery       │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │  DTOs (Data Transfer Objects)                           │ │
│  │  - CutterDTO, CutterSearchResultDTO                     │ │
│  └─────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Domain Layer                            │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 Aggregate Roots                          │ │
│  │  ┌──────────────────────────────────────────────────┐   │ │
│  │  │ Cutter (Entity + Business Logic)                 │   │ │
│  │  │ - id, name, cutterType, material, geometry       │   │ │
│  │  │ - Methods: isSuitableForMaterial(),              │   │ │
│  │  │           getCuttingSpeed(), updateGuideline()   │   │ │
│  │  └──────────────────────────────────────────────────┘   │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │  Value Objects (Immutable)                               │ │
│  │  - CutterType (category, subcategory, coating)          │ │
│  │  - MaterialSpec (substrate, coating_type, hardness)     │ │
│  │  - GeometryParams (diameter, length, flutes, ...)       │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │  Repository Interfaces                                   │ │
│  │  - CutterRepository (add, get, search, update, delete)  │ │
│  └─────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                       │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Persistence Implementations                             │ │
│  │  ┌──────────────────┐  ┌────────────────────────────┐   │ │
│  │  │ ChromaCutter     │  │ EmbeddingService           │   │ │
│  │  │ Repository       │  │ (sentence-transformers)    │   │ │
│  │  │ (ChromaDB)       │  │                            │   │ │
│  │  └──────────────────┘  └────────────────────────────┘   │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │  External Services                                       │ │
│  │  - LLM Client (OpenAI, Local models)                    │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏗️ 设计原则

### 1. DDD (Domain-Driven Design)

**核心概念：**
- **Aggregate Root**: `Cutter` 是唯一的聚合根，所有业务操作都通过它进行
- **Value Objects**: `CutterType`, `MaterialSpec`, `GeometryParams` 是不可变值对象
- **Repository Pattern**: 领域层定义接口，基础设施层实现
- **Domain Services**: 跨聚合的业务逻辑放在领域服务中

**目录结构：**
```
src/domain/
├── models/
│   ├── cutter.py           # Cutter 聚合根
│   └── value_objects.py    # 值对象
├── repositories/
│   └── cutter_repo.py      # Repository 接口
└── services/
    └── knowledge_service.py # 领域服务
```

### 2. CQRS (Command Query Responsibility Segregation)

**写操作 (Commands)：**
```python
IngestCutterCommand → CutterCommandHandler → Repository.add()
UpdateCutterCommand → CutterCommandHandler → Repository.update()
DeleteCutterCommand → CutterCommandHandler → Repository.delete()
```

**读操作 (Queries)：**
```python
SearchCuttersQuery → CutterQueryHandler → Repository.search()
GetCutterByIdQuery → CutterQueryHandler → Repository.get_by_id()
GetAllCuttersQuery → CutterQueryHandler → Repository.get_all()
```

**优势：**
- 读写分离，优化各自性能
- 清晰的职责划分
- 易于扩展和优化

### 3. Clean Architecture

**依赖规则：**
- 外层可以依赖内层，内层绝不能依赖外层
- Domain Layer 是核心，不依赖任何外部库
- Application Layer 只依赖 Domain Layer
- Infrastructure 和 Interface 依赖 Application 和 Domain

**层次关系：**
```
Interface → Application → Domain ← Infrastructure
```

---

## 🎨 设计模式应用

### 1. Repository Pattern
```python
# Domain Layer 定义接口
class CutterRepository(ABC):
    @abstractmethod
    def add(self, cutter: Cutter) -> None: pass
    
    @abstractmethod
    def search_by_query(self, query: str, top_k: int) -> list: pass

# Infrastructure Layer 实现
class ChromaCutterRepository(CutterRepository):
    def add(self, cutter: Cutter) -> None:
        # ChromaDB specific implementation
        pass
```

### 2. Factory Method
```python
class Cutter:
    @classmethod
    def create(
        cls,
        name: str,
        cutter_type: CutterType,
        material: MaterialSpec,
        geometry: GeometryParams,
        ...
    ) -> "Cutter":
        # 封装复杂的创建逻辑
        return cls(...)
```

### 3. Strategy Pattern
```python
class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # 可以轻松切换不同的嵌入模型
        self._model = load_model(model_name)
```

### 4. Dependency Injection
```python
# FastAPI 依赖注入
def get_command_handler() -> CutterCommandHandler:
    repo = ChromaCutterRepository()
    return CutterCommandHandler(repository=repo)

@app.post("/cutters")
async def ingest_cutter(
    request: IngestCutterRequest,
    handler: CutterCommandHandler = Depends(get_command_handler),
):
    return handler.handle_ingest(command)
```

### 5. DTO Pattern
```python
class CutterDTO(BaseModel):
    """数据传输对象，隔离外部与领域模型"""
    
    @classmethod
    def from_domain(cls, cutter: Cutter) -> "CutterDTO":
        # 从领域模型转换
        return cls(...)
```

---

## ✅ 代码规范

### Type Hints
```python
from typing import Optional, List
from uuid import UUID

def search_cutters(
    query: str,
    top_k: int = 5,
    filters: Optional[dict] = None,
) -> List[Cutter]:
    ...
```

### Docstrings
```python
class Cutter:
    """
    Aggregate Root: Represents a cutting tool in the knowledge base.
    
    This is the main entity that encapsulates all cutter-related data
    and business logic.
    """
    
    def is_suitable_for_material(self, material: str) -> bool:
        """
        Check if cutter is suitable for a given workpiece material.
        
        Args:
            material: The workpiece material name
            
        Returns:
            True if compatible, False otherwise
        """
```

### Error Handling
```python
from src.domain.repositories.cutter_repo import CutterNotFoundError

try:
    cutter = repository.get_by_id(cutter_id)
    if not cutter:
        raise CutterNotFoundError(f"Cutter {cutter_id} not found")
except RepositoryError as e:
    logger.error(f"Repository error: {e}")
    raise HTTPException(status_code=404, detail=str(e))
```

---

## 🧪 TDD 实践

### 测试金字塔
```
        /\
       /  \      E2E Tests (少量)
      /----\     
     /      \    Integration Tests
    /--------\   
   /          \  Unit Tests (大量)
  /------------\ 
```

### 单元测试示例
```python
class TestCutter:
    def test_is_suitable_for_material_match(self, valid_cutter_data):
        """Should return True for compatible material."""
        cutter = Cutter.create(**valid_cutter_data)
        
        assert cutter.is_suitable_for_material("steel") is True
        assert cutter.is_suitable_for_material("STAINLESS_STEEL") is True
```

### 运行测试
```bash
# 所有测试
pytest

# 单元测试
pytest tests/unit/ -v

# 带覆盖率报告
pytest --cov=src --cov-report=html
```

---

## 📦 项目结构

```
tooling-rag/
├── src/
│   ├── domain/                 # 领域层（业务核心）
│   │   ├── models/
│   │   ├── repositories/
│   │   └── services/
│   ├── application/            # 应用层（用例）
│   │   ├── commands/
│   │   ├── queries/
│   │   ├── handlers/
│   │   └── dto/
│   ├── infrastructure/         # 基础设施层
│   │   ├── persistence/
│   │   └── external/
│   └── interface/              # 接口层
│       ├── api/
│       └── cli/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── scripts/
├── data/
├── pyproject.toml
├── pytest.ini
├── mypy.ini
└── README.md
```

---

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install -e ".[dev]"

# 2. 初始化知识库
python scripts/init_knowledge_base.py

# 3. 启动服务
./start_server.sh

# 4. 访问 API 文档
open http://localhost:8000/docs

# 5. 运行测试
pytest tests/unit/domain/test_models.py -v
```

---

## 📝 检查清单

### 代码质量
- [x] Type hints 完整
- [x] Docstrings 完整
- [x] 单一职责原则
- [x] 依赖倒置原则
- [x] 开闭原则

### 测试覆盖
- [x] 领域模型单元测试
- [ ] 应用层测试
- [ ] 基础设施层测试
- [ ] 集成测试
- [ ] API 端点测试

### 工程规范
- [x] DDD 分层架构
- [x] CQRS 模式
- [x] Repository 模式
- [x] DTO 模式
- [x] 依赖注入
- [x] TDD 实践

---

## 🔧 扩展指南

### 添加新的 Cutter 属性
1. 在 `domain/models/value_objects.py` 添加新的 Value Object
2. 更新 `Cutter` 聚合根
3. 更新 `IngestCutterCommand`
4. 更新 `CutterDTO`
5. 添加相应的测试

### 添加新的搜索方式
1. 在 `application/queries/` 创建新的 Query 类
2. 在 `CutterQueryHandler` 添加处理方法
3. 在 `CutterRepository` 添加接口方法
4. 在 `ChromaCutterRepository` 实现
5. 在 API 层添加路由

### 更换向量数据库
1. 实现 `CutterRepository` 接口
2. 使用工厂模式或配置切换实现
3. 无需修改业务逻辑代码
