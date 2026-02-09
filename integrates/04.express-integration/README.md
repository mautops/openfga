# Express.js + OpenFGA 集成示例

这是一个完整的 Express.js 与 OpenFGA 集成示例，展示了如何在 Node.js Web 应用中实现基于关系的细粒度权限控制。

## 📋 目录

- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [授权模型](#授权模型)
- [API 接口](#api-接口)
- [权限控制流程](#权限控制流程)
- [开发说明](#开发说明)
- [最佳实践](#最佳实践)

## 🎯 功能特性

- ✅ **JWT 认证**: 基于 JSON Web Token 的用户认证
- ✅ **OpenFGA 授权**: 细粒度的基于关系的访问控制
- ✅ **中间件模式**: Express 风格的权限检查中间件
- ✅ **RESTful API**: 符合 REST 规范的文档管理接口
- ✅ **TypeScript**: 完整的类型安全支持
- ✅ **错误处理**: 统一的错误处理机制
- ✅ **请求日志**: 自动记录所有 API 请求

## 🛠 技术栈

- **运行时**: Node.js 18+
- **框架**: Express.js 4.x
- **语言**: TypeScript 5.x
- **认证**: jsonwebtoken
- **授权**: @openfga/sdk
- **工具**:
  - ts-node-dev (开发热重载)
  - dotenv (环境变量管理)

## 📁 项目结构

```
04.express-integration/
├── src/
│   ├── app.ts                    # Express 应用主文件
│   ├── config/
│   │   └── openfga.ts           # OpenFGA 客户端配置
│   ├── middleware/
│   │   ├── auth.ts              # JWT 认证中间件
│   │   └── permissions.ts       # OpenFGA 权限检查中间件
│   ├── routes/
│   │   ├── auth.ts              # 认证路由
│   │   └── documents.ts         # 文档路由
│   └── types/
│       └── index.ts             # TypeScript 类型定义
├── authorization_model.fga       # OpenFGA 授权模型
├── package.json
├── tsconfig.json
├── .env.example
└── README.md
```

## 🚀 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 启动 OpenFGA 服务

使用 Docker 启动 OpenFGA:

```bash
docker run -d \
  --name openfga \
  -p 8080:8080 \
  openfga/openfga run
```

### 3. 创建授权模型

```bash
# 创建 Store
curl -X POST http://localhost:8080/stores \
  -H "Content-Type: application/json" \
  -d '{"name": "express-demo"}'

# 记录返回的 store_id，例如: 01HQXYZ123456789ABCDEFGHIJK

# 创建授权模型
curl -X POST http://localhost:8080/stores/{store_id}/authorization-models \
  -H "Content-Type: application/json" \
  -d '{
    "schema_version": "1.1",
    "type_definitions": [
      {
        "type": "user"
      },
      {
        "type": "document",
        "relations": {
          "owner": {
            "this": {}
          },
          "editor": {
            "union": {
              "child": [
                {"this": {}},
                {"computedUserset": {"relation": "owner"}}
              ]
            }
          },
          "viewer": {
            "union": {
              "child": [
                {"this": {}},
                {"computedUserset": {"relation": "editor"}}
              ]
            }
          }
        }
      }
    ]
  }'

# 记录返回的 authorization_model_id
```

### 4. 配置环境变量

复制 `.env.example` 为 `.env` 并填入实际值:

```bash
cp .env.example .env
```

编辑 `.env`:

```env
PORT=3000
NODE_ENV=development

JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_EXPIRES_IN=24h

FGA_API_URL=http://localhost:8080
FGA_STORE_ID=01HQXYZ123456789ABCDEFGHIJK
FGA_AUTHORIZATION_MODEL_ID=01HQXYZ123456789ABCDEFGHIJK

LOG_LEVEL=info
```

### 5. 启动开发服务器

```bash
npm run dev
```

服务将在 http://localhost:3000 启动。

### 6. 生产环境构建

```bash
npm run build
npm start
```

## 🔐 授权模型

本示例使用以下授权模型：

```fga
model
  schema 1.1

type user

type document
  relations
    define owner: [user]
    define editor: [user] or owner
    define viewer: [user] or editor
```

### 权限层次

- **owner** (所有者): 拥有文档的完全控制权
  - 可以执行所有操作（查看、编辑、删除）

- **editor** (编辑者): 可以修改文档
  - 继承 owner 的所有权限
  - 可以查看和编辑文档

- **viewer** (查看者): 只能查看文档
  - 继承 editor 的查看权限
  - 只能读取文档内容

### 权限继承关系

```
owner (删除、编辑、查看)
  ↓
editor (编辑、查看)
  ↓
viewer (查看)
```

## 📡 API 接口

### 认证接口

#### 1. 登录

```bash
POST /auth/login
Content-Type: application/json

{
  "email": "alice@example.com",
  "password": "password123"
}
```

响应:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "userId": "user:alice",
    "email": "alice@example.com"
  }
}
```

#### 2. 获取当前用户信息

```bash
GET /auth/profile
Authorization: Bearer {token}
```

响应:

```json
{
  "user": {
    "userId": "user:alice",
    "email": "alice@example.com"
  }
}
```

### 文档接口

#### 1. 创建文档

```bash
POST /documents
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "我的文档",
  "content": "这是文档内容"
}
```

响应:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "我的文档",
  "content": "这是文档内容",
  "ownerId": "user:alice",
  "createdAt": "2024-01-15T10:30:00.000Z",
  "updatedAt": "2024-01-15T10:30:00.000Z"
}
```

#### 2. 获取文档列表

```bash
GET /documents
Authorization: Bearer {token}
```

响应:

```json
{
  "documents": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "我的文档",
      "ownerId": "user:alice",
      "createdAt": "2024-01-15T10:30:00.000Z"
    }
  ],
  "total": 1
}
```

#### 3. 获取文档详情

```bash
GET /documents/:id
Authorization: Bearer {token}
```

需要 `viewer` 权限。

#### 4. 更新文档

```bash
PUT /documents/:id
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "更新后的标题",
  "content": "更新后的内容"
}
```

需要 `editor` 权限。

#### 5. 删除文档

```bash
DELETE /documents/:id
Authorization: Bearer {token}
```

需要 `owner` 权限。

## 🔄 权限控制流程

### 1. 请求流程

```
客户端请求
    ↓
认证中间件 (authenticateToken)
    ↓ (验证 JWT)
权限中间件 (checkPermission)
    ↓ (调用 OpenFGA)
路由处理器
    ↓
响应客户端
```

### 2. 中间件链

```typescript
router.get(
  '/documents/:id',
  authenticateToken,                    // 1. 验证 JWT
  checkPermission('viewer'),            // 2. 检查 OpenFGA 权限
  async (req, res) => { /* ... */ }     // 3. 执行业务逻辑
);
```

### 3. OpenFGA 权限检查

```typescript
const { allowed } = await fgaClient.check({
  user: 'user:alice',
  relation: 'viewer',
  object: 'document:550e8400-e29b-41d4-a716-446655440000',
});

if (!allowed) {
  throw new Error('权限不足');
}
```

## 🧪 测试示例

### 1. 完整流程测试

```bash
# 1. 登录获取 token
TOKEN=$(curl -s -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"password123"}' \
  | jq -r '.token')

# 2. 创建文档
DOC_ID=$(curl -s -X POST http://localhost:3000/documents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"测试文档","content":"测试内容"}' \
  | jq -r '.id')

# 3. 查看文档（作为 owner 自动拥有权限）
curl -X GET http://localhost:3000/documents/$DOC_ID \
  -H "Authorization: Bearer $TOKEN"

# 4. 更新文档
curl -X PUT http://localhost:3000/documents/$DOC_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"更新后的标题","content":"更新后的内容"}'

# 5. 删除文档
curl -X DELETE http://localhost:3000/documents/$DOC_ID \
  -H "Authorization: Bearer $TOKEN"
```

### 2. 添加共享权限

```bash
# 为 bob 添加 viewer 权限
curl -X POST http://localhost:8080/stores/{store_id}/write \
  -H "Content-Type: application/json" \
  -d '{
    "writes": {
      "tuple_keys": [
        {
          "user": "user:bob",
          "relation": "viewer",
          "object": "document:'$DOC_ID'"
        }
      ]
    }
  }'

# 现在 bob 可以查看文档
BOB_TOKEN=$(curl -s -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@example.com","password":"password123"}' \
  | jq -r '.token')

curl -X GET http://localhost:3000/documents/$DOC_ID \
  -H "Authorization: Bearer $BOB_TOKEN"
```

## 💡 开发说明

### TypeScript 配置

项目使用严格的 TypeScript 配置：

- 启用严格模式 (`strict: true`)
- 未使用的变量检查
- 完整的类型定义
- ES2020 目标

### 错误处理

所有异步操作都使用 try-catch 包裹：

```typescript
try {
  const result = await someAsyncOperation();
  res.json(result);
} catch (error) {
  next(error); // 传递给全局错误处理中间件
}
```

### 中间件开发

创建新的权限检查中间件：

```typescript
export const checkCustomPermission = (
  relation: string,
  objectType: string
) => {
  return async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const { allowed } = await fgaClient.check({
        user: req.user!.userId,
        relation: relation,
        object: `${objectType}:${req.params.id}`,
      });

      if (!allowed) {
        return res.status(403).json({ error: '权限不足' });
      }

      next();
    } catch (error) {
      next(error);
    }
  };
};
```

## ✨ 最佳实践

### 1. OpenFGA 客户端单例

```typescript
// ✅ 正确：全局单例
const fgaClient = new OpenFgaClient({ /* ... */ });
export { fgaClient };

// ❌ 错误：每次创建新实例
function getClient() {
  return new OpenFgaClient({ /* ... */ });
}
```

### 2. 中间件顺序

```typescript
// 正确的顺序
app.use(express.json());              // 1. 解析请求体
app.use(loggingMiddleware);           // 2. 日志
app.use('/api', routes);              // 3. 业务路由
app.use(notFoundHandler);             // 4. 404 处理
app.use(errorHandler);                // 5. 错误处理（必须最后）
```

### 3. 错误处理中间件

```typescript
// 必须有 4 个参数
app.use((err: any, req: Request, res: Response, next: NextFunction) => {
  // 错误处理逻辑
});
```

### 4. 异步路由处理

```typescript
// ✅ 正确：捕获异步错误
router.get('/path', async (req, res, next) => {
  try {
    const result = await asyncOperation();
    res.json(result);
  } catch (error) {
    next(error);
  }
});

// 或使用包装函数
const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

router.get('/path', asyncHandler(async (req, res) => {
  const result = await asyncOperation();
  res.json(result);
}));
```

### 5. 环境变量验证

```typescript
// 启动时验证必需的环境变量
const requiredEnvVars = [
  'FGA_API_URL',
  'FGA_STORE_ID',
  'JWT_SECRET',
];

for (const varName of requiredEnvVars) {
  if (!process.env[varName]) {
    throw new Error(`缺少必需的环境变量: ${varName}`);
  }
}
```

## 📚 相关资源

- [Express.js 官方文档](https://expressjs.com/)
- [OpenFGA 文档](https://openfga.dev/docs)
- [OpenFGA JavaScript SDK](https://github.com/openfga/js-sdk)
- [TypeScript 文档](https://www.typescriptlang.org/)
- [JWT 介绍](https://jwt.io/)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
