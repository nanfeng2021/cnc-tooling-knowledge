# Frontend Service

CNC刀具知识库系统的前端服务，提供用户界面和交互体验。

## 功能特性

- **刀具管理界面**：刀具的增删改查操作
- **智能搜索界面**：语义搜索和结果展示
- **推荐服务界面**：切削参数推荐和刀具推荐
- **场景匹配界面**：加工场景匹配和结果展示
- **响应式设计**：支持多种设备屏幕
- **Mock模式**：支持离线开发和测试
- **状态管理**：Zustand状态管理
- **路由管理**：React Router路由管理
- **UI组件库**：Radix UI组件库

## 架构

本服务采用React + TypeScript + Vite技术栈：

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Application                     │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Components │  │    Pages     │  │   Services   │      │
│  │   (UI组件)   │  │   (页面)     │  │   (API服务)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                 │                 │               │
│         ▼                 ▼                 ▼               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    State Management                  │   │
│  │               (Zustand Store)                        │   │
│  └─────────────────────────────────────────────────────┘   │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    API Gateway                       │   │
│  │              (cnc-api-gateway:8000)                  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 目录结构

```
frontend/
├── src/
│   ├── components/               # UI组件
│   │   ├── CutterCard.tsx       # 刀具卡片组件
│   │   ├── SearchBar.tsx        # 搜索栏组件
│   │   ├── RecommendationPanel.tsx # 推荐面板组件
│   │   └── ScenarioMatcher.tsx  # 场景匹配组件
│   ├── pages/                   # 页面组件
│   │   ├── Home.tsx             # 首页
│   │   ├── CutterList.tsx       # 刀具列表页
│   │   ├── CutterDetail.tsx     # 刀具详情页
│   │   ├── Search.tsx           # 搜索页
│   │   └── Recommendations.tsx  # 推荐页
│   ├── services/                # API服务
│   │   ├── api.ts               # API客户端
│   │   ├── cutterService.ts     # 刀具服务
│   │   ├── searchService.ts     # 搜索服务
│   │   └── recommendationService.ts # 推荐服务
│   ├── hooks/                   # 自定义Hooks
│   │   ├── useCutters.ts       # 刀具Hook
│   │   ├── useSearch.ts        # 搜索Hook
│   │   └── useRecommendations.ts # 推荐Hook
│   ├── store/                   # 状态管理
│   │   ├── cutterStore.ts      # 刀具状态
│   │   └── searchStore.ts      # 搜索状态
│   ├── types/                   # TypeScript类型
│   │   ├── cutter.ts           # 刀具类型
│   │   └── search.ts           # 搜索类型
│   ├── utils/                   # 工具函数
│   │   └── helpers.ts          # 辅助函数
│   ├── App.tsx                  # 应用根组件
│   ├── main.tsx                 # 应用入口
│   └── index.css                # 全局样式
├── public/                      # 静态资源
│   ├── index.html              # HTML模板
│   └── favicon.ico             # 网站图标
├── tests/                       # 测试文件
│   ├── components/             # 组件测试
│   └── pages/                  # 页面测试
├── Dockerfile                   # Docker配置
├── package.json                 # 项目配置
├── tsconfig.json               # TypeScript配置
├── vite.config.ts              # Vite配置
├── README.md                   # 项目文档
└── .env.example                # 环境变量示例
```

## 快速开始

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置API网关地址
```

### 3. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173 查看应用。

### 4. 构建生产版本

```bash
npm run build
```

### 5. 使用Docker

```bash
# 构建镜像
docker build -t cnc-frontend .

# 运行容器
docker run -p 80:80 cnc-frontend

# 使用Docker Compose
docker-compose up -d
```

## 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `VITE_API_BASE_URL` | `/api` | API基础URL |
| `VITE_API_MODE` | `""` | API模式（mock/空） |
| `VITE_APP_TITLE` | `CNC Tooling Knowledge` | 应用标题 |
| `VITE_APP_VERSION` | `1.0.0` | 应用版本 |

### API模式

- **正常模式**：连接API网关服务
- **Mock模式**：使用本地Mock数据，支持离线开发

### 构建配置

1. **API基础URL**：配置API网关地址
2. **构建优化**：Vite自动优化打包
3. **代码分割**：自动代码分割和懒加载

## 开发指南

### 添加新页面

1. 在 `src/pages/` 创建新的页面组件
2. 在 `src/App.tsx` 添加路由配置
3. 在 `src/services/` 添加API服务

### 添加新组件

1. 在 `src/components/` 创建新的UI组件
2. 使用TypeScript定义组件Props
3. 添加组件测试

### 状态管理

```typescript
// src/store/cutterStore.ts
import { create } from 'zustand'

interface CutterStore {
  cutters: Cutter[]
  loading: boolean
  error: string | null
  fetchCutters: () => Promise<void>
  addCutter: (cutter: Cutter) => Promise<void>
  updateCutter: (id: string, cutter: Partial<Cutter>) => Promise<void>
  deleteCutter: (id: string) => Promise<void>
}

export const useCutterStore = create<CutterStore>((set) => ({
  cutters: [],
  loading: false,
  error: null,
  fetchCutters: async () => {
    set({ loading: true, error: null })
    try {
      const cutters = await cutterService.getAll()
      set({ cutters, loading: false })
    } catch (error) {
      set({ error: error.message, loading: false })
    }
  },
  // ... 其他方法
}))
```

### API服务

```typescript
// src/services/api.ts
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加认证token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // 处理错误
    if (error.response?.status === 401) {
      // 处理认证失败
    }
    return Promise.reject(error)
  }
)

export default api
```

## 测试

```bash
# 运行所有测试
npm test

# 运行单元测试
npm run test:unit

# 运行集成测试
npm run test:integration

# 生成覆盖率报告
npm run test:coverage

# 运行E2E测试
npm run test:e2e
```

## 部署

### Docker部署

```bash
# 构建镜像
docker build -t cnc-frontend:latest .

# 运行容器
docker run -d \
  --name cnc-frontend \
  -p 80:80 \
  cnc-frontend:latest
```

### Nginx部署

```bash
# 构建生产版本
npm run build

# 将dist目录部署到Nginx
cp -r dist/* /var/www/html/
```

### Kubernetes部署

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cnc-frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cnc-frontend
  template:
    metadata:
      labels:
        app: cnc-frontend
    spec:
      containers:
      - name: cnc-frontend
        image: cnc-frontend:latest
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: cnc-frontend-service
spec:
  selector:
    app: cnc-frontend
  ports:
  - port: 80
    targetPort: 80
  type: LoadBalancer
```

## 性能优化

### 代码分割

```typescript
// 路由懒加载
const CutterList = lazy(() => import('./pages/CutterList'))
const CutterDetail = lazy(() => import('./pages/CutterDetail'))
const Search = lazy(() => import('./pages/Search'))
```

### 图片优化

- 使用WebP格式
- 实现图片懒加载
- 使用CDN加速

### 缓存策略

- 静态资源缓存
- API响应缓存
- 本地存储缓存

## 安全建议

1. **使用HTTPS**：生产环境必须使用HTTPS
2. **XSS防护**：对用户输入进行转义
3. **CSRF防护**：使用CSRF Token
4. **内容安全策略**：配置CSP头
5. **依赖安全**：定期更新依赖包

## 故障排除

### 常见问题

1. **API连接失败**
   - 检查 `VITE_API_BASE_URL` 配置
   - 确保API网关服务已启动
   - 检查网络连接

2. **构建失败**
   - 检查Node.js版本（需要18+）
   - 清除node_modules重新安装
   - 检查TypeScript错误

3. **页面空白**
   - 检查控制台错误
   - 检查路由配置
   - 检查API响应

### 调试模式

```bash
# 启用详细日志
VITE_DEBUG=true npm run dev

# 检查构建输出
npm run build -- --debug
```

## 开发工具

### 推荐IDE配置

- VSCode + ESLint + Prettier
- TypeScript支持
- React Developer Tools

### 代码规范

```bash
# 代码检查
npm run lint

# 代码格式化
npm run format

# 类型检查
npm run type-check
```

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License