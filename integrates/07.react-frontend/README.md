# React + OpenFGA 集成示例

这是一个完整的 React 前端应用示例，展示如何集成 OpenFGA 进行细粒度的权限管理。

## 功能特性

### 核心功能
- ✅ 用户认证（登录/登出）
- ✅ 文档 CRUD 操作
- ✅ 基于 OpenFGA 的权限检查
- ✅ 权限缓存机制
- ✅ 受保护的路由
- ✅ 基于权限的 UI 元素显示/隐藏
- ✅ 乐观更新
- ✅ 批量权限检查

### 权限场景
- **查看文档列表**：需要登录
- **查看文档详情**：需要 `can_view` 权限
- **编辑文档**：需要 `can_edit` 权限
- **删除文档**：需要 `can_delete` 权限（通常是 owner）
- **分享文档**：需要 `can_share` 权限（通常是 owner）

## 技术栈

- **React 18+** - UI 框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **React Router** - 路由管理
- **TailwindCSS** - 样式框架
- **Axios** - HTTP 客户端
- **OpenFGA** - 权限管理

## 项目结构

```
07.react-frontend/
├── src/
│   ├── components/          # React 组件
│   │   ├── DocumentList.tsx       # 文档列表组件
│   │   ├── DocumentEditor.tsx     # 文档编辑器组件
│   │   ├── PermissionGate.tsx     # 权限门控组件
│   │   └── ProtectedRoute.tsx     # 受保护的路由组件
│   ├── hooks/               # 自定义 Hooks
│   │   ├── useAuth.ts             # 认证 Hook
│   │   └── usePermissions.ts      # 权限检查 Hook
│   ├── services/            # 服务层
│   │   ├── api.ts                 # API 服务
│   │   └── permissions.ts         # 权限服务
│   ├── types/               # TypeScript 类型定义
│   │   └── index.ts
│   ├── App.tsx              # 主应用组件
│   ├── main.tsx             # 入口文件
│   └── index.css            # 全局样式
├── index.html               # HTML 模板
├── package.json             # 依赖配置
├── tsconfig.json            # TypeScript 配置
├── vite.config.ts           # Vite 配置
├── tailwind.config.js       # TailwindCSS 配置
├── .env.example             # 环境变量示例
└── README.md                # 项目文档
```

## 快速开始

### 1. 安装依赖

```bash
pnpm install
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# API 配置
VITE_API_URL=http://localhost:8000
VITE_OPENFGA_API_URL=http://localhost:8080

# OpenFGA 配置
VITE_OPENFGA_STORE_ID=your-store-id
VITE_OPENFGA_MODEL_ID=your-model-id

# 认证配置
VITE_AUTH_TOKEN_KEY=auth_token
```

### 3. 启动开发服务器

```bash
pnpm dev
```

应用将在 http://localhost:3000 启动。

### 4. 构建生产版本

```bash
pnpm build
```

### 5. 预览生产版本

```bash
pnpm preview
```

## 核心组件说明

### 1. 权限检查 Hook (`usePermissions.ts`)

提供三个主要的 Hook：

#### `usePermission` - 单个权限检查

```typescript
const { hasPermission, isLoading, error, refetch } = usePermission({
  object: {
    type: 'document',
    id: 'doc-123',
  },
  relation: 'can_edit',
})
```

#### `useBatchPermissions` - 批量权限检查

```typescript
const { permissions, isLoading, error, refetch } = useBatchPermissions([
  { object: { type: 'document', id: 'doc-123' }, relation: 'can_view' },
  { object: { type: 'document', id: 'doc-123' }, relation: 'can_edit' },
])
```

#### `useResourcePermissions` - 资源权限检查

```typescript
const { permissions, isLoading, clearCache } = useResourcePermissions(
  'document',
  'doc-123',
  ['can_view', 'can_edit', 'can_delete']
)
```

### 2. 权限门控组件 (`PermissionGate.tsx`)

根据权限决定是否渲染子组件：

```tsx
<PermissionGate
  objectType="document"
  objectId={documentId}
  relation="can_edit"
  fallback={<p>您没有编辑权限</p>}
>
  <button>编辑文档</button>
</PermissionGate>
```

### 3. 权限按钮组件 (`PermissionButton`)

只有当用户有权限时才显示的按钮：

```tsx
<PermissionButton
  objectType="document"
  objectId={documentId}
  relation="owner"
  onClick={handleDelete}
  className="btn-danger"
>
  删除
</PermissionButton>
```

### 4. 受保护的路由 (`ProtectedRoute.tsx`)

保护需要认证的路由：

```tsx
<Route
  path="/documents"
  element={
    <ProtectedRoute>
      <DocumentList />
    </ProtectedRoute>
  }
/>
```

### 5. 认证 Hook (`useAuth.ts`)

管理用户认证状态：

```typescript
const { user, isAuthenticated, isLoading, login, logout } = useAuth()
```

## 权限缓存机制

为了优化性能，权限检查结果会被缓存 5 分钟：

```typescript
// 权限服务会自动缓存结果
const result = await checkPermission(request)

// 手动清除缓存
clearPermissionCache('document', 'doc-123', 'can_edit')

// 清除所有缓存
clearPermissionCache()
```

## 乐观更新示例

在删除文档时使用乐观更新：

```typescript
const handleDeleteDocument = async (documentId: string) => {
  // 1. 先从 UI 中移除
  const originalDocuments = [...documents]
  setDocuments(documents.filter((doc) => doc.id !== documentId))

  try {
    // 2. 发送删除请求
    await api.deleteDocument(documentId)
  } catch (err) {
    // 3. 失败时恢复
    setDocuments(originalDocuments)
    alert('删除失败')
  }
}
```

## API 接口说明

### 认证接口

```typescript
// 登录
POST /api/auth/login
Body: { username: string, password: string }
Response: { token: string, user: User }

// 获取当前用户
GET /api/auth/me
Headers: { Authorization: 'Bearer <token>' }
Response: User

// 登出
POST /api/auth/logout
Headers: { Authorization: 'Bearer <token>' }
```

### 文档接口

```typescript
// 获取文档列表
GET /api/documents
Headers: { Authorization: 'Bearer <token>' }
Response: Document[]

// 获取单个文档
GET /api/documents/:id
Headers: { Authorization: 'Bearer <token>' }
Response: Document

// 创建文档
POST /api/documents
Headers: { Authorization: 'Bearer <token>' }
Body: { title: string, content: string }
Response: Document

// 更新文档
PUT /api/documents/:id
Headers: { Authorization: 'Bearer <token>' }
Body: { title?: string, content?: string }
Response: Document

// 删除文档
DELETE /api/documents/:id
Headers: { Authorization: 'Bearer <token>' }

// 分享文档
POST /api/documents/:id/share
Headers: { Authorization: 'Bearer <token>' }
Body: { userId: string, permission: 'viewer' | 'editor' }
```

### 权限检查接口

```typescript
// 单个权限检查
POST /api/permissions/check
Headers: { Authorization: 'Bearer <token>' }
Body: {
  object: { type: string, id: string },
  relation: string
}
Response: { allowed: boolean }

// 批量权限检查
POST /api/permissions/batch-check
Headers: { Authorization: 'Bearer <token>' }
Body: {
  checks: Array<{
    object: { type: string, id: string },
    relation: string
  }>
}
Response: {
  results: Array<{ allowed: boolean }>
}
```

## OpenFGA 授权模型

本示例使用以下授权模型：

```
model
  schema 1.1

type user

type document
  relations
    define owner: [user]
    define editor: [user] or owner
    define viewer: [user] or editor
    define can_view: viewer
    define can_edit: editor
    define can_delete: owner
    define can_share: owner
```

## 最佳实践

### 1. 权限检查时机

- **路由级别**：使用 `ProtectedRoute` 保护整个页面
- **组件级别**：使用 `PermissionGate` 控制组件显示
- **操作级别**：在执行操作前再次检查权限

### 2. 批量权限检查

当需要检查多个权限时，使用批量检查减少网络请求：

```typescript
// ❌ 不好 - 多次请求
const canView = await checkPermission({ object, relation: 'can_view' })
const canEdit = await checkPermission({ object, relation: 'can_edit' })

// ✅ 好 - 一次请求
const results = await checkBatchPermissions([
  { object, relation: 'can_view' },
  { object, relation: 'can_edit' },
])
```

### 3. 权限缓存管理

- 权限变更后及时清除缓存
- 使用合适的缓存时间（默认 5 分钟）
- 敏感操作不使用缓存

### 4. 错误处理

```typescript
const { hasPermission, error } = usePermission(request)

if (error) {
  // 处理错误，可能需要重新登录
  console.error('权限检查失败:', error)
}
```

### 5. 加载状态

```typescript
<PermissionGate
  objectType="document"
  objectId={id}
  relation="can_edit"
  loading={<Spinner />}
  fallback={<NoPermission />}
>
  <EditButton />
</PermissionGate>
```

## 开发调试

### 查看权限信息

在开发模式下，`DocumentEditor` 组件会显示当前用户的权限信息：

```typescript
{process.env.NODE_ENV === 'development' && (
  <div className="mt-6 p-4 bg-gray-100 rounded">
    <h3 className="font-semibold mb-2">当前权限（开发模式）：</h3>
    <ul className="text-sm text-gray-600">
      <li>查看权限: {canView ? '✓' : '✗'}</li>
      <li>编辑权限: {canEdit ? '✓' : '✗'}</li>
      <li>删除权限: {canDelete ? '✓' : '✗'}</li>
      <li>分享权限: {canShare ? '✓' : '✗'}</li>
    </ul>
  </div>
)}
```

### 清除权限缓存

在浏览器控制台中：

```javascript
// 清除所有缓存
localStorage.clear()

// 或者在代码中
import { clearPermissionCache } from './services/permissions'
clearPermissionCache()
```

## 常见问题

### 1. 权限检查失败

**问题**：权限检查总是返回 false

**解决方案**：
- 检查后端 API 是否正常运行
- 确认 OpenFGA 配置正确
- 检查用户是否已登录
- 查看浏览器控制台的错误信息

### 2. 权限缓存不更新

**问题**：权限变更后 UI 没有更新

**解决方案**：
```typescript
// 手动清除缓存并刷新
const { refetch, clearCache } = useResourcePermissions(...)
clearCache()
await refetch()
```

### 3. 批量权限检查性能问题

**问题**：批量检查太多权限导致响应慢

**解决方案**：
- 只检查必要的权限
- 使用权限缓存
- 考虑在后端预计算权限

## 扩展功能

### 1. 添加新的权限类型

在 `src/types/index.ts` 中添加：

```typescript
export type PermissionRelation = 'owner' | 'editor' | 'viewer' | 'commenter'
```

### 2. 添加新的资源类型

创建新的组件和 Hook：

```typescript
// src/hooks/useProjectPermissions.ts
export function useProjectPermissions(projectId: string) {
  return useResourcePermissions('project', projectId, [
    'can_view',
    'can_edit',
    'can_delete',
  ])
}
```

### 3. 集成其他认证方式

修改 `src/services/api.ts` 支持 OAuth、JWT 等：

```typescript
export async function loginWithOAuth(provider: string) {
  // 实现 OAuth 登录
}
```

## 性能优化建议

1. **使用 React.memo** 避免不必要的重渲染
2. **权限预加载** 在列表页面预加载所有文档的权限
3. **虚拟滚动** 处理大量文档列表
4. **代码分割** 使用 React.lazy 和 Suspense
5. **Service Worker** 缓存静态资源

## 安全注意事项

1. **永远不要只依赖前端权限检查** - 后端必须再次验证
2. **使用 HTTPS** - 保护 token 传输
3. **Token 过期处理** - 实现自动刷新或重新登录
4. **XSS 防护** - 避免直接渲染用户输入
5. **CSRF 防护** - 使用 CSRF token

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 相关资源

- [OpenFGA 官方文档](https://openfga.dev/)
- [React 官方文档](https://react.dev/)
- [TypeScript 官方文档](https://www.typescriptlang.org/)
- [Vite 官方文档](https://vitejs.dev/)
- [TailwindCSS 官方文档](https://tailwindcss.com/)
