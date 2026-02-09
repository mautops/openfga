# Express + OpenFGA 开发指南

本文档提供了深入的开发指南，帮助您理解和扩展这个集成示例。

## 目录

- [架构设计](#架构设计)
- [核心概念](#核心概念)
- [代码结构](#代码结构)
- [中间件详解](#中间件详解)
- [扩展指南](#扩展指南)
- [性能优化](#性能优化)
- [安全最佳实践](#安全最佳实践)
- [故障排查](#故障排查)

## 架构设计

### 整体架构

```
┌─────────────┐
│   客户端    │
└──────┬──────┘
       │ HTTP Request
       ↓
┌─────────────────────────────────┐
│      Express 应用层              │
│  ┌──────────────────────────┐  │
│  │  认证中间件 (JWT)         │  │
│  └────────┬─────────────────┘  │
│           ↓                     │
│  ┌──────────────────────────┐  │
│  │  权限中间件 (OpenFGA)     │  │
│  └────────┬─────────────────┘  │
│           ↓                     │
│  ┌──────────────────────────┐  │
│  │  业务逻辑层               │  │
│  └────────┬─────────────────┘  │
└───────────┼─────────────────────┘
            │
    ┌───────┴────────┐
    ↓                ↓
┌─────────┐    ┌──────────┐
│ 数据库  │    │ OpenFGA  │
└─────────┘    └──────────┘
```

### 请求处理流程

```
1. 客户端发送请求
   ↓
2. Express 接收请求
   ↓
3. 日志中间件记录请求
   ↓
4. 认证中间件验证 JWT
   ↓
5. 权限中间件检查 OpenFGA
   ↓
6. 路由处理器执行业务逻辑
   ↓
7. 返回响应
```

## 核心概念

### 1. 认证 vs 授权

- **认证 (Authentication)**: 验证用户身份
  - 使用 JWT token
  - 在 `authenticateToken` 中间件中实现
  - 回答："你是谁？"

- **授权 (Authorization)**: 验证用户权限
  - 使用 OpenFGA
  - 在 `checkPermission` 中间件中实现
  - 回答："你能做什么？"

### 2. 中间件链

Express 中间件按顺序执行：

```typescript
app.use(middleware1);  // 先执行
app.use(middleware2);  // 后执行
app.use(middleware3);  // 最后执行
```

对于路由：

```typescript
router.get('/path',
  middleware1,  // 1. 认证
  middleware2,  // 2. 授权
  handler       // 3. 业务逻辑
);
```

### 3. OpenFGA 关系模型

```
user:alice ──owner──> document:doc1
                         ↓
                      editor (继承)
                         ↓
                      viewer (继承)
```

## 代码结构

### 目录组织

```
src/
├── app.ts              # 应用入口
├── config/             # 配置文件
│   └── openfga.ts     # OpenFGA 客户端
├── middleware/         # 中间件
│   ├── auth.ts        # JWT 认证
│   └── permissions.ts # OpenFGA 权限
├── routes/            # 路由
│   ├── auth.ts        # 认证路由
│   └── documents.ts   # 文档路由
└── types/             # 类型定义
    └── index.ts       # TypeScript 接口
```

### 模块职责

| 模块 | 职责 | 依赖 |
|------|------|------|
| app.ts | 应用初始化、中间件注册 | 所有路由 |
| config/openfga.ts | OpenFGA 客户端管理 | @openfga/sdk |
| middleware/auth.ts | JWT 验证 | jsonwebtoken |
| middleware/permissions.ts | 权限检查 | OpenFGA 客户端 |
| routes/*.ts | 业务逻辑 | 中间件 |

## 中间件详解

### 1. 认证中间件 (authenticateToken)

**功能**: 验证 JWT token 并提取用户信息

**实现**:

```typescript
export const authenticateToken = (
  req: AuthRequest,
  res: Response,
  next: NextFunction
): void => {
  // 1. 提取 token
  const authHeader = req.headers.authorization;
  const token = authHeader?.split(' ')[1];

  if (!token) {
    res.status(401).json({ error: 'Missing token' });
    return;
  }

  // 2. 验证 token
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
};
```

**使用场景**:
- 所有需要认证的路由
- 必须在权限检查之前

### 2. 权限中间件 (checkPermission)

**功能**: 检查用户是否有特定权限

**实现**:

```typescript
export const checkPermission = (relation: string) => {
  return async (req: AuthRequest, res: Response, next: NextFunction) => {
    // 1. 获取用户和资源
    const userId = req.user!.userId;
    const resourceId = req.params.id;

    // 2. 调用 OpenFGA
    const { allowed } = await fgaClient.check({
      user: userId,
      relation: relation,
      object: `document:${resourceId}`,
    });

    // 3. 判断权限
    if (!allowed) {
      res.status(403).json({ error: 'Forbidden' });
      return;
    }

    next();
  };
};
```

**使用场景**:
- 需要特定权限的路由
- 必须在认证之后

### 3. 错误处理中间件

**功能**: 统一处理所有错误

**实现**:

```typescript
app.use((err: any, req: Request, res: Response, next: NextFunction) => {
  console.error(err);

  const statusCode = err.statusCode || 500;
  const message = err.message || 'Internal Server Error';

  res.status(statusCode).json({
    error: message,
    ...(NODE_ENV === 'development' && { stack: err.stack }),
  });
});
```

**注意事项**:
- 必须有 4 个参数
- 必须放在所有路由之后

## 扩展指南

### 1. 添加新的资源类型

假设要添加 `project` 资源：

#### 步骤 1: 更新授权模型

```fga
type project
  relations
    define owner: [user]
    define member: [user] or owner
    define viewer: [user] or member
```

#### 步骤 2: 创建路由

```typescript
// src/routes/projects.ts
import { Router } from 'express';
import { authenticateToken } from '../middleware/auth';
import { checkPermission } from '../middleware/permissions';

const router = Router();

router.post('/', authenticateToken, createProject);
router.get('/:id', authenticateToken, checkPermission('viewer'), getProject);
router.put('/:id', authenticateToken, checkPermission('member'), updateProject);
router.delete('/:id', authenticateToken, checkPermission('owner'), deleteProject);

export default router;
```

#### 步骤 3: 注册路由

```typescript
// src/app.ts
import projectRoutes from './routes/projects';
app.use('/projects', projectRoutes);
```

### 2. 添加自定义权限检查

创建更复杂的权限检查逻辑：

```typescript
// src/middleware/permissions.ts
export const checkMultiplePermissions = (
  relations: string[]
) => {
  return async (req: AuthRequest, res: Response, next: NextFunction) => {
    const userId = req.user!.userId;
    const resourceId = req.params.id;

    // 并行检查多个权限
    const checks = await Promise.all(
      relations.map(relation =>
        fgaClient.check({
          user: userId,
          relation: relation,
          object: `document:${resourceId}`,
        })
      )
    );

    // 只要有一个权限满足即可
    const hasPermission = checks.some(check => check.allowed);

    if (!hasPermission) {
      res.status(403).json({ error: 'Forbidden' });
      return;
    }

    next();
  };
};
```

使用：

```typescript
router.put('/:id',
  authenticateToken,
  checkMultiplePermissions(['owner', 'admin']),
  updateDocument
);
```

### 3. 添加数据库集成

使用 Prisma 或 TypeORM：

```typescript
// src/config/database.ts
import { PrismaClient } from '@prisma/client';

export const prisma = new PrismaClient();

// src/routes/documents.ts
import { prisma } from '../config/database';

router.post('/', authenticateToken, async (req, res) => {
  const document = await prisma.document.create({
    data: {
      title: req.body.title,
      content: req.body.content,
      ownerId: req.user!.userId,
    },
  });

  // 写入 OpenFGA
  await fgaClient.write({
    writes: [{
      user: req.user!.userId,
      relation: 'owner',
      object: `document:${document.id}`,
    }],
  });

  res.json(document);
});
```

## 性能优化

### 1. OpenFGA 客户端复用

```typescript
// ✅ 正确：单例模式
const fgaClient = new OpenFgaClient({ /* ... */ });
export { fgaClient };

// ❌ 错误：每次创建新实例
function getClient() {
  return new OpenFgaClient({ /* ... */ });
}
```

### 2. 批量权限检查

```typescript
// 并行检查多个资源
const checks = await Promise.all(
  documentIds.map(id =>
    fgaClient.check({
      user: userId,
      relation: 'viewer',
      object: `document:${id}`,
    })
  )
);
```

### 3. 缓存权限结果

```typescript
import NodeCache from 'node-cache';

const permissionCache = new NodeCache({ stdTTL: 60 }); // 60 秒

export const checkPermissionWithCache = (relation: string) => {
  return async (req: AuthRequest, res: Response, next: NextFunction) => {
    const cacheKey = `${req.user!.userId}:${relation}:${req.params.id}`;

    // 检查缓存
    const cached = permissionCache.get(cacheKey);
    if (cached !== undefined) {
      if (!cached) {
        res.status(403).json({ error: 'Forbidden' });
        return;
      }
      return next();
    }

    // 调用 OpenFGA
    const { allowed } = await fgaClient.check({
      user: req.user!.userId,
      relation: relation,
      object: `document:${req.params.id}`,
    });

    // 缓存结果
    permissionCache.set(cacheKey, allowed);

    if (!allowed) {
      res.status(403).json({ error: 'Forbidden' });
      return;
    }

    next();
  };
};
```

### 4. 使用连接池

```typescript
// OpenFGA SDK 内部已经使用了连接池
// 确保只创建一个客户端实例即可
```

## 安全最佳实践

### 1. JWT 安全

```typescript
// ✅ 使用强密钥
JWT_SECRET=at-least-32-characters-long-random-string

// ✅ 设置合理的过期时间
JWT_EXPIRES_IN=1h  // 生产环境建议短一些

// ✅ 使用 HTTPS
// 在生产环境中始终使用 HTTPS

// ✅ 实现 token 刷新机制
router.post('/refresh', authenticateToken, refreshToken);
```

### 2. 输入验证

```typescript
import { body, validationResult } from 'express-validator';

router.post('/documents',
  authenticateToken,
  body('title').isString().trim().isLength({ min: 1, max: 200 }),
  body('content').isString().trim().isLength({ min: 1, max: 10000 }),
  (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }
    // 处理请求
  }
);
```

### 3. 速率限制

```typescript
import rateLimit from 'express-rate-limit';

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 分钟
  max: 100, // 限制 100 个请求
  message: '请求过于频繁，请稍后再试',
});

app.use('/auth/login', limiter);
```

### 4. CORS 配置

```typescript
import cors from 'cors';

app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || 'http://localhost:3000',
  credentials: true,
}));
```

## 故障排查

### 常见问题

#### 1. OpenFGA 连接失败

**症状**: `Error: connect ECONNREFUSED`

**解决方案**:
```bash
# 检查 OpenFGA 是否运行
docker ps | grep openfga

# 检查端口
curl http://localhost:8080/healthz

# 查看日志
docker logs openfga
```

#### 2. JWT 验证失败

**症状**: `401 Unauthorized`

**解决方案**:
```typescript
// 检查 JWT_SECRET 是否一致
console.log('JWT_SECRET:', process.env.JWT_SECRET);

// 检查 token 格式
console.log('Token:', req.headers.authorization);

// 检查 token 是否过期
const decoded = jwt.decode(token);
console.log('Expires:', new Date(decoded.exp * 1000));
```

#### 3. 权限检查失败

**症状**: `403 Forbidden`

**解决方案**:
```bash
# 检查关系元组是否存在
curl -X POST http://localhost:8080/stores/$STORE_ID/read \
  -H "Content-Type: application/json" \
  -d '{
    "tuple_key": {
      "user": "user:alice",
      "relation": "viewer",
      "object": "document:doc1"
    }
  }'

# 检查授权模型
curl http://localhost:8080/stores/$STORE_ID/authorization-models/$MODEL_ID
```

#### 4. TypeScript 编译错误

**症状**: 类型错误

**解决方案**:
```bash
# 清理构建缓存
rm -rf dist/
rm -rf node_modules/
npm install

# 重新构建
npm run build
```

### 调试技巧

#### 1. 启用详细日志

```typescript
// src/app.ts
import morgan from 'morgan';

if (process.env.NODE_ENV === 'development') {
  app.use(morgan('dev'));
}
```

#### 2. 添加请求 ID

```typescript
import { v4 as uuidv4 } from 'uuid';

app.use((req, res, next) => {
  req.id = uuidv4();
  console.log(`[${req.id}] ${req.method} ${req.url}`);
  next();
});
```

#### 3. 使用调试器

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "node",
      "request": "launch",
      "name": "Debug Express",
      "runtimeExecutable": "npm",
      "runtimeArgs": ["run", "dev"],
      "console": "integratedTerminal"
    }
  ]
}
```

## 总结

本开发指南涵盖了：

- ✅ 架构设计和请求流程
- ✅ 核心概念和代码结构
- ✅ 中间件实现细节
- ✅ 扩展和定制方法
- ✅ 性能优化技巧
- ✅ 安全最佳实践
- ✅ 故障排查指南

继续学习：
- 阅读 [Express 官方文档](https://expressjs.com/)
- 阅读 [OpenFGA 文档](https://openfga.dev/docs)
- 查看示例代码
- 实践和实验
