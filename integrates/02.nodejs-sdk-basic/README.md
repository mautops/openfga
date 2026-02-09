# OpenFGA Node.js/TypeScript SDK 基础集成示例

本示例展示了如何在 Node.js/TypeScript 项目中集成和使用 OpenFGA SDK，实现细粒度的权限管理。

## 目录结构

```
02.nodejs-sdk-basic/
├── src/
│   ├── client.ts          # OpenFGA 客户端封装
│   └── examples.ts        # 完整使用示例
├── authorization_model.fga # 授权模型定义
├── package.json           # 项目依赖配置
├── tsconfig.json          # TypeScript 配置
├── .env.example           # 环境变量示例
└── README.md              # 本文档
```

## 功能特性

- ✅ **客户端封装**: 提供简化的 API 接口
- ✅ **关系元组管理**: 写入、删除、读取关系元组
- ✅ **权限检查**: 单个和批量权限检查
- ✅ **对象列表**: 列出用户可访问的对象
- ✅ **用户列表**: 列出可访问对象的用户
- ✅ **TypeScript 支持**: 完整的类型定义
- ✅ **错误处理**: 完善的异常处理机制
- ✅ **异步编程**: 使用 async/await 模式

## 前置要求

1. **Node.js**: 版本 18.x 或更高
2. **pnpm**: 包管理器
3. **OpenFGA 服务器**: 运行在本地或远程

### 启动 OpenFGA 服务器

使用 Docker 快速启动：

```bash
docker run -d \
  --name openfga \
  -p 8080:8080 \
  -p 8081:8081 \
  -p 3000:3000 \
  openfga/openfga run
```

## 安装步骤

### 1. 安装依赖

```bash
cd 02.nodejs-sdk-basic
pnpm install
```

### 2. 配置环境变量

复制环境变量示例文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# OpenFGA 服务器配置
FGA_API_URL=http://localhost:8080

# Store ID (可选，如果已创建 store)
FGA_STORE_ID=

# Authorization Model ID (可选，如果已创建模型)
FGA_MODEL_ID=
```

### 3. 创建 Store 和授权模型

如果还没有创建 Store 和授权模型，可以使用 OpenFGA CLI：

```bash
# 安装 OpenFGA CLI
brew install openfga/tap/fga

# 创建 Store
fga store create --name "demo-store"

# 写入授权模型
fga model write --store-id <your-store-id> --file authorization_model.fga

# 获取模型 ID
fga model list --store-id <your-store-id>
```

将获取到的 Store ID 和 Model ID 填入 `.env` 文件。

## 使用方法

### 编译 TypeScript

```bash
pnpm run build
```

### 运行示例

```bash
# 使用 ts-node 直接运行（开发模式）
pnpm run dev

# 或者先编译再运行
pnpm run build
pnpm start
```

## 代码示例

### 1. 初始化客户端

```typescript
import { OpenFGAClient } from './client';

const client = new OpenFGAClient({
  apiUrl: 'http://localhost:8080',
  storeId: 'your-store-id',
  authorizationModelId: 'your-model-id',
});
```

### 2. 写入关系元组

```typescript
// 创建用户和文档的关系
await client.writeTuples([
  {
    user: 'user:alice',
    relation: 'owner',
    object: 'document:roadmap',
  },
  {
    user: 'user:bob',
    relation: 'viewer',
    object: 'document:roadmap',
  },
]);
```

### 3. 权限检查

```typescript
// 检查 Alice 是否可以查看文档
const canView = await client.check(
  'user:alice',
  'viewer',
  'document:roadmap'
);

console.log(`Alice 可以查看文档: ${canView}`);
```

### 4. 批量权限检查

```typescript
import { randomUUID } from 'crypto';

const batchResult = await client.batchCheck([
  {
    user: 'user:alice',
    relation: 'viewer',
    object: 'document:roadmap',
    correlationId: randomUUID(),
  },
  {
    user: 'user:bob',
    relation: 'editor',
    object: 'document:roadmap',
  },
]);

batchResult.result?.forEach((item) => {
  console.log(
    `${item.request?.user} ${item.allowed ? '可以' : '不可以'} ${item.request?.relation} ${item.request?.object}`
  );
});
```

### 5. 列出对象

```typescript
// 列出用户可以访问的所有文档
const documents = await client.listObjects(
  'user:alice',
  'viewer',
  'document'
);

console.log(`Alice 可以查看的文档: ${documents.join(', ')}`);
```

### 6. 列出用户

```typescript
// 列出可以访问文档的所有用户
const users = await client.listUsers(
  'document',
  'roadmap',
  'viewer',
  [{ type: 'user' }]
);

users.users?.forEach((user) => {
  if (user.object) {
    console.log(`${user.object.type}:${user.object.id}`);
  }
});
```

### 7. 删除关系元组

```typescript
// 删除用户的查看权限
await client.deleteTuples([
  {
    user: 'user:bob',
    relation: 'viewer',
    object: 'document:roadmap',
  },
]);
```

### 8. 同时写入和删除（事务模式）

```typescript
// 将用户从 viewer 升级为 editor
await client.writeAndDeleteTuples(
  [
    {
      user: 'user:bob',
      relation: 'editor',
      object: 'document:roadmap',
    },
  ],
  [
    {
      user: 'user:bob',
      relation: 'viewer',
      object: 'document:roadmap',
    },
  ]
);
```

## 授权模型说明

本示例使用的授权模型支持以下场景：

### 类型定义

- **user**: 用户
- **organization**: 组织
- **folder**: 文件夹
- **document**: 文档

### 关系定义

#### Organization（组织）
- `member`: 组织成员
- `admin`: 组织管理员

#### Folder（文件夹）
- `owner`: 文件夹所有者
- `parent`: 父文件夹
- `viewer`: 可以查看（继承自所有者和父文件夹）
- `editor`: 可以编辑（继承自所有者）

#### Document（文档）
- `owner`: 文档所有者
- `parent`: 所属文件夹
- `viewer`: 可以查看（继承自所有者、编辑者和父文件夹）
- `editor`: 可以编辑（继承自所有者和父文件夹）
- `deleter`: 可以删除（仅所有者）

### 权限继承示例

```
组织成员 → 可以查看组织内的文档
文件夹所有者 → 可以查看文件夹内的文档
文档所有者 → 拥有文档的所有权限
```

## API 参考

### OpenFGAClient 类

#### 构造函数

```typescript
constructor(config?: Partial<OpenFGAClientConfig>)
```

#### 方法

| 方法 | 描述 | 返回值 |
|------|------|--------|
| `writeTuples(tuples, modelId?)` | 写入关系元组 | `Promise<void>` |
| `deleteTuples(tuples, modelId?)` | 删除关系元组 | `Promise<void>` |
| `writeAndDeleteTuples(writes, deletes, modelId?)` | 同时写入和删除 | `Promise<void>` |
| `check(user, relation, object, modelId?)` | 检查权限 | `Promise<boolean>` |
| `batchCheck(checks, modelId?)` | 批量检查权限 | `Promise<BatchCheckResponse>` |
| `listObjects(user, relation, type, contextualTuples?, modelId?)` | 列出对象 | `Promise<string[]>` |
| `listUsers(objectType, objectId, relation, userFilters, contextualTuples?, context?, modelId?)` | 列出用户 | `Promise<ListUsersResponse>` |
| `readTuples(filter)` | 读取关系元组 | `Promise<ReadResponse>` |
| `createStore(name)` | 创建 Store | `Promise<string>` |
| `listStores()` | 列出所有 Stores | `Promise<any>` |
| `getClient()` | 获取原始客户端 | `OpenFgaClient` |
| `getConfig()` | 获取当前配置 | `OpenFGAClientConfig` |
| `setStoreId(storeId)` | 更新 Store ID | `void` |
| `setAuthorizationModelId(modelId)` | 更新模型 ID | `void` |

## 错误处理

所有方法都包含完善的错误处理：

```typescript
try {
  await client.check('user:alice', 'viewer', 'document:test');
} catch (error) {
  console.error('权限检查失败:', error);
  // 处理错误
}
```

## 最佳实践

### 1. 客户端单例

在应用程序中只初始化一次客户端并重复使用：

```typescript
// app.ts
export const fgaClient = new OpenFGAClient({
  apiUrl: process.env.FGA_API_URL,
  storeId: process.env.FGA_STORE_ID,
  authorizationModelId: process.env.FGA_MODEL_ID,
});

// 在其他文件中导入使用
import { fgaClient } from './app';
```

### 2. 环境变量管理

使用环境变量管理配置，不要硬编码：

```typescript
// ✅ 推荐
const client = new OpenFGAClient({
  apiUrl: process.env.FGA_API_URL,
});

// ❌ 不推荐
const client = new OpenFGAClient({
  apiUrl: 'http://localhost:8080',
});
```

### 3. 类型安全

充分利用 TypeScript 的类型系统：

```typescript
import type { RelationshipTuple } from './client';

const tuples: RelationshipTuple[] = [
  {
    user: 'user:alice',
    relation: 'viewer',
    object: 'document:test',
  },
];

await client.writeTuples(tuples);
```

### 4. 批量操作

对于多个权限检查，使用批量 API 提高性能：

```typescript
// ✅ 推荐：批量检查
const results = await client.batchCheck([
  { user: 'user:alice', relation: 'viewer', object: 'document:1' },
  { user: 'user:alice', relation: 'viewer', object: 'document:2' },
  { user: 'user:alice', relation: 'viewer', object: 'document:3' },
]);

// ❌ 不推荐：多次单独检查
const result1 = await client.check('user:alice', 'viewer', 'document:1');
const result2 = await client.check('user:alice', 'viewer', 'document:2');
const result3 = await client.check('user:alice', 'viewer', 'document:3');
```

### 5. 错误处理

始终处理可能的错误：

```typescript
try {
  const canView = await client.check(user, relation, object);
  if (canView) {
    // 允许访问
  } else {
    // 拒绝访问
  }
} catch (error) {
  // 处理错误（如网络问题、服务器错误等）
  console.error('权限检查失败:', error);
  // 默认拒绝访问
}
```

## 性能优化

### 1. 连接池

SDK 内部使用连接池，重用客户端实例可以提高性能。

### 2. 批量操作

使用批量 API 减少网络往返次数。

### 3. 缓存

对于不经常变化的权限检查结果，可以考虑添加缓存层：

```typescript
import { LRUCache } from 'lru-cache';

const cache = new LRUCache<string, boolean>({
  max: 1000,
  ttl: 1000 * 60 * 5, // 5 分钟
});

async function checkWithCache(
  user: string,
  relation: string,
  object: string
): Promise<boolean> {
  const key = `${user}:${relation}:${object}`;

  const cached = cache.get(key);
  if (cached !== undefined) {
    return cached;
  }

  const result = await client.check(user, relation, object);
  cache.set(key, result);
  return result;
}
```

## 故障排查

### 问题 1: 连接失败

**错误**: `Error: connect ECONNREFUSED 127.0.0.1:8080`

**解决方案**:
- 确认 OpenFGA 服务器正在运行
- 检查 `FGA_API_URL` 配置是否正确

### 问题 2: Store ID 未设置

**错误**: `Error: Store ID is required`

**解决方案**:
- 创建 Store 并设置 `FGA_STORE_ID` 环境变量
- 或在代码中调用 `createStore()` 方法

### 问题 3: 授权模型未找到

**错误**: `Error: Authorization model not found`

**解决方案**:
- 确认已创建授权模型
- 检查 `FGA_MODEL_ID` 是否正确
- 或者不设置 `FGA_MODEL_ID`，使用最新的模型

### 问题 4: TypeScript 编译错误

**解决方案**:
```bash
# 清理并重新编译
pnpm run clean
pnpm run build
```

## 相关资源

- [OpenFGA 官方文档](https://openfga.dev/docs)
- [OpenFGA Node.js SDK](https://github.com/openfga/js-sdk)
- [OpenFGA Playground](https://play.fga.dev/)
- [授权模型语言参考](https://openfga.dev/docs/modeling/language)

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
