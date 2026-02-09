# OpenFGA Node.js SDK 快速参考

## 快速开始

```bash
# 1. 安装依赖
pnpm install

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 3. 运行示例
pnpm run dev
```

## 常用命令

```bash
# 开发模式运行基础示例
pnpm run dev

# 开发模式运行高级示例
pnpm run dev:advanced

# 编译 TypeScript
pnpm run build

# 运行编译后的代码
pnpm start

# 清理编译输出
pnpm run clean
```

## 客户端初始化

```typescript
import { OpenFGAClient } from './client';

const client = new OpenFGAClient({
  apiUrl: 'http://localhost:8080',
  storeId: 'your-store-id',
  authorizationModelId: 'your-model-id',
});
```

## 核心 API

### 写入关系元组

```typescript
await client.writeTuples([
  {
    user: 'user:alice',
    relation: 'viewer',
    object: 'document:roadmap',
  },
]);
```

### 删除关系元组

```typescript
await client.deleteTuples([
  {
    user: 'user:bob',
    relation: 'viewer',
    object: 'document:roadmap',
  },
]);
```

### 权限检查

```typescript
const canView = await client.check(
  'user:alice',
  'viewer',
  'document:roadmap'
);
// 返回: true 或 false
```

### 批量权限检查

```typescript
const result = await client.batchCheck([
  {
    user: 'user:alice',
    relation: 'viewer',
    object: 'document:roadmap',
  },
  {
    user: 'user:bob',
    relation: 'editor',
    object: 'document:roadmap',
  },
]);
```

### 列出对象

```typescript
const documents = await client.listObjects(
  'user:alice',
  'viewer',
  'document'
);
// 返回: ['document:roadmap', 'document:budget', ...]
```

### 列出用户

```typescript
const users = await client.listUsers(
  'document',
  'roadmap',
  'viewer',
  [{ type: 'user' }]
);
```

### 读取关系元组

```typescript
const tuples = await client.readTuples({
  user: 'user:alice',
});
```

## 高级场景类

### 多租户文档管理

```typescript
import { MultiTenantDocumentSystem } from './advanced-examples';

const docSystem = new MultiTenantDocumentSystem(client);

// 创建文档
await docSystem.createDocument(
  'tenant-1',
  'doc-1',
  'alice',
  ['bob'],      // viewers
  ['charlie']   // editors
);

// 检查权限
const canAccess = await docSystem.canAccessDocument(
  'alice',
  'doc-1',
  'viewer'
);

// 获取用户文档
const docs = await docSystem.getUserDocuments('alice', 'viewer');

// 转移所有权
await docSystem.transferOwnership('doc-1', 'alice', 'bob');

// 共享文档
await docSystem.shareDocument('doc-1', ['charlie'], 'viewer');
```

### 组织层级管理

```typescript
import { OrganizationHierarchy } from './advanced-examples';

const orgHierarchy = new OrganizationHierarchy(client);

// 创建组织
await orgHierarchy.createOrganization(
  'acme',
  ['alice'],           // admins
  ['bob', 'charlie']   // members
);

// 添加成员
await orgHierarchy.addMember('acme', 'david', 'member');

// 检查身份
const isAdmin = await orgHierarchy.isAdmin('acme', 'alice');
const isMember = await orgHierarchy.isMember('acme', 'bob');
```

### 文件夹层级

```typescript
import { FolderHierarchy } from './advanced-examples';

const folderHierarchy = new FolderHierarchy(client);

// 创建文件夹
await folderHierarchy.createFolder('root', 'alice');
await folderHierarchy.createFolder('sub', 'alice', 'root');

// 添加文档到文件夹
await folderHierarchy.addDocumentToFolder('doc-1', 'sub');

// 检查权限
const canAccess = await folderHierarchy.canAccessFolder(
  'alice',
  'sub',
  'viewer'
);
```

### 权限审计

```typescript
import { PermissionAuditor } from './advanced-examples';

const auditor = new PermissionAuditor(client);

// 获取用户权限
const permissions = await auditor.getUserPermissions('alice');
// 返回: { documents: [...], folders: [...], organizations: [...] }

// 获取对象访问者
const viewers = await auditor.getObjectViewers('document', 'roadmap');

// 批量检查
const checks = [
  { objectType: 'document', objectId: 'doc-1', relation: 'viewer' },
  { objectType: 'document', objectId: 'doc-2', relation: 'editor' },
];
const results = await auditor.batchCheckUserPermissions('alice', checks);

// 生成报告
await auditor.generatePermissionReport('alice');
```

## 授权模型

### 类型

- `user`: 用户
- `organization`: 组织
- `folder`: 文件夹
- `document`: 文档

### 关系

#### Organization
- `member`: 成员
- `admin`: 管理员

#### Folder
- `owner`: 所有者
- `parent`: 父文件夹
- `viewer`: 查看者
- `editor`: 编辑者

#### Document
- `owner`: 所有者
- `parent`: 所属文件夹
- `viewer`: 查看者
- `editor`: 编辑者
- `deleter`: 删除者

### 权限继承

```
文档的 viewer = owner OR editor OR viewer from parent
文档的 editor = owner OR editor from parent
文档的 deleter = owner
```

## 错误处理

```typescript
try {
  const canView = await client.check(user, relation, object);
  if (canView) {
    // 允许访问
  } else {
    // 拒绝访问
  }
} catch (error) {
  console.error('权限检查失败:', error);
  // 默认拒绝访问
}
```

## 环境变量

```env
FGA_API_URL=http://localhost:8080
FGA_STORE_ID=your-store-id
FGA_MODEL_ID=your-model-id
```

## OpenFGA CLI 命令

```bash
# 安装 CLI
brew install openfga/tap/fga

# 创建 Store
fga store create --name "demo-store"

# 导入授权模型
fga model write --store-id <store-id> --file authorization_model.fga

# 列出模型
fga model list --store-id <store-id>

# 写入元组
fga tuple write --store-id <store-id> \
  user:alice viewer document:roadmap

# 检查权限
fga tuple check --store-id <store-id> \
  user:alice viewer document:roadmap

# 读取元组
fga tuple read --store-id <store-id>
```

## Docker 命令

```bash
# 启动 OpenFGA 服务器
docker run -d \
  --name openfga \
  -p 8080:8080 \
  -p 8081:8081 \
  -p 3000:3000 \
  openfga/openfga run

# 查看日志
docker logs -f openfga

# 停止服务器
docker stop openfga

# 删除容器
docker rm openfga
```

## 最佳实践

### ✅ 推荐

```typescript
// 1. 客户端单例
export const fgaClient = new OpenFGAClient({...});

// 2. 使用环境变量
const apiUrl = process.env.FGA_API_URL;

// 3. 批量操作
await client.batchCheck([...]);

// 4. 错误处理
try {
  await client.check(...);
} catch (error) {
  // 处理错误
}

// 5. 类型安全
const tuples: RelationshipTuple[] = [...];
```

### ❌ 避免

```typescript
// 1. 多次创建客户端
const client1 = new OpenFGAClient({...});
const client2 = new OpenFGAClient({...});

// 2. 硬编码配置
const apiUrl = 'http://localhost:8080';

// 3. 多次单独检查
await client.check(...);
await client.check(...);
await client.check(...);

// 4. 忽略错误
await client.check(...); // 没有 try-catch

// 5. 缺少类型
const tuples = [...]; // 没有类型注解
```

## 性能优化

1. **重用客户端**: 只初始化一次
2. **批量操作**: 使用 `batchCheck` 而不是多次 `check`
3. **添加缓存**: 缓存不常变化的权限检查结果
4. **连接池**: SDK 内部自动管理

## 故障排查

| 问题 | 解决方案 |
|------|---------|
| 连接失败 | 检查 OpenFGA 服务器是否运行 |
| Store ID 未设置 | 创建 Store 并配置环境变量 |
| 模型未找到 | 导入授权模型或不设置 MODEL_ID |
| 编译错误 | 运行 `pnpm run clean && pnpm run build` |

## 相关链接

- [OpenFGA 官方文档](https://openfga.dev/docs)
- [Node.js SDK GitHub](https://github.com/openfga/js-sdk)
- [授权模型语言](https://openfga.dev/docs/modeling/language)
- [OpenFGA Playground](https://play.fga.dev/)
