# 项目文件说明

## 核心文件

### 1. `src/client.ts`
OpenFGA 客户端封装类，提供简化的 API 接口。

**主要功能：**
- 客户端初始化和配置管理
- 关系元组的写入、删除、读取
- 单个和批量权限检查
- 列出对象和用户
- Store 和授权模型管理

**核心类：**
- `OpenFGAClient`: 主客户端类

**导出类型：**
- `OpenFGAClientConfig`: 客户端配置接口
- `RelationshipTuple`: 关系元组接口
- `BatchCheckItem`: 批量检查项接口
- 以及所有 SDK 原生类型

### 2. `src/examples.ts`
基础使用示例，展示常见操作。

**示例内容：**
1. 客户端初始化
2. 写入关系元组
3. 权限检查
4. 批量权限检查
5. 列出对象
6. 列出用户
7. 读取关系元组
8. 同时写入和删除（事务模式）
9. 删除关系元组
10. 错误处理

**运行方式：**
```bash
pnpm run dev          # 开发模式
pnpm run build && pnpm start  # 生产模式
```

### 3. `src/advanced-examples.ts`
高级使用场景示例，展示实际应用。

**场景包括：**
1. **多租户文档管理系统** (`MultiTenantDocumentSystem`)
   - 创建文档并设置权限
   - 检查访问权限
   - 获取用户文档列表
   - 转移文档所有权
   - 共享和取消共享文档

2. **组织层级权限管理** (`OrganizationHierarchy`)
   - 创建组织
   - 添加/移除成员
   - 检查成员和管理员身份

3. **文件夹层级权限** (`FolderHierarchy`)
   - 创建文件夹
   - 建立父子关系
   - 将文档放入文件夹
   - 检查文件夹访问权限

4. **权限审计** (`PermissionAuditor`)
   - 获取用户的所有权限
   - 获取对象的所有访问者
   - 批量检查权限
   - 生成权限报告

**运行方式：**
```bash
pnpm run dev:advanced          # 开发模式
pnpm run build && pnpm start:advanced  # 生产模式
```

## 配置文件

### 4. `package.json`
项目依赖和脚本配置。

**主要依赖：**
- `@openfga/sdk`: OpenFGA 官方 SDK
- `dotenv`: 环境变量管理

**开发依赖：**
- `typescript`: TypeScript 编译器
- `ts-node`: TypeScript 运行时
- `@types/node`: Node.js 类型定义

**可用脚本：**
- `pnpm run build`: 编译 TypeScript
- `pnpm run dev`: 运行基础示例（开发模式）
- `pnpm run dev:advanced`: 运行高级示例（开发模式）
- `pnpm start`: 运行基础示例（生产模式）
- `pnpm start:advanced`: 运行高级示例（生产模式）
- `pnpm run clean`: 清理编译输出

### 5. `tsconfig.json`
TypeScript 编译器配置。

**主要配置：**
- 目标: ES2020
- 模块: CommonJS
- 严格模式: 启用
- 输出目录: `./dist`
- 源码目录: `./src`
- 生成声明文件和 Source Map

### 6. `.env.example`
环境变量示例文件。

**配置项：**
- `FGA_API_URL`: OpenFGA 服务器地址
- `FGA_STORE_ID`: Store ID（可选）
- `FGA_MODEL_ID`: 授权模型 ID（可选）

**使用方法：**
```bash
cp .env.example .env
# 编辑 .env 文件填入实际值
```

### 7. `authorization_model.fga`
OpenFGA 授权模型定义（DSL 格式）。

**定义的类型：**
- `user`: 用户
- `organization`: 组织
  - 关系: member, admin
- `folder`: 文件夹
  - 关系: owner, parent, viewer, editor
- `document`: 文档
  - 关系: owner, parent, viewer, editor, deleter

**权限继承规则：**
- 文档的 viewer 可以是：所有者、编辑者、或父文件夹的 viewer
- 文档的 editor 可以是：所有者、或父文件夹的 editor
- 组织成员可以查看组织内的文档

**使用方法：**
```bash
# 使用 OpenFGA CLI 导入模型
fga model write --store-id <store-id> --file authorization_model.fga
```

## 辅助文件

### 8. `.gitignore`
Git 忽略文件配置。

**忽略内容：**
- `node_modules/`: 依赖包
- `dist/`: 编译输出
- `.env`: 环境变量（包含敏感信息）
- 日志文件
- 编辑器配置
- 临时文件

### 9. `setup.sh`
快速启动脚本。

**功能：**
1. 检查 pnpm 是否安装
2. 检查 Docker 是否运行
3. 安装项目依赖
4. 创建 .env 文件
5. 编译 TypeScript

**使用方法：**
```bash
chmod +x setup.sh
./setup.sh
```

### 10. `README.md`
项目文档。

**内容包括：**
- 项目介绍
- 功能特性
- 安装步骤
- 使用方法
- 代码示例
- 授权模型说明
- API 参考
- 最佳实践
- 性能优化
- 故障排查
- 相关资源

## 文件依赖关系

```
.env.example
    ↓
.env (用户创建)
    ↓
src/client.ts (读取环境变量)
    ↓
    ├─→ src/examples.ts (基础示例)
    └─→ src/advanced-examples.ts (高级示例)

authorization_model.fga
    ↓
OpenFGA Server (导入模型)
    ↓
src/client.ts (使用模型)
```

## 开发流程

### 初次使用
1. 运行 `./setup.sh` 或手动安装依赖
2. 启动 OpenFGA 服务器
3. 创建 Store 和导入授权模型
4. 配置 `.env` 文件
5. 运行示例代码

### 日常开发
1. 修改 TypeScript 代码
2. 使用 `pnpm run dev` 测试
3. 使用 `pnpm run build` 编译
4. 使用 `pnpm start` 运行生产版本

### 集成到项目
1. 复制 `src/client.ts` 到你的项目
2. 安装依赖: `pnpm add @openfga/sdk dotenv`
3. 导入并使用: `import { OpenFGAClient } from './client'`
4. 根据需要修改授权模型

## 最佳实践

### 1. 客户端管理
- 在应用启动时初始化一次客户端
- 在整个应用中重用同一个客户端实例
- 不要为每个请求创建新的客户端

### 2. 错误处理
- 始终使用 try-catch 包裹 OpenFGA 调用
- 记录错误日志用于调试
- 为用户提供友好的错误信息

### 3. 性能优化
- 使用批量 API 减少网络请求
- 考虑添加缓存层
- 合理设置超时时间

### 4. 安全性
- 不要在代码中硬编码敏感信息
- 使用环境变量管理配置
- 定期审计权限设置

### 5. 测试
- 为权限检查编写单元测试
- 测试边界情况和错误场景
- 使用模拟数据进行集成测试

## 扩展建议

### 添加缓存
```typescript
import { LRUCache } from 'lru-cache';

const cache = new LRUCache<string, boolean>({
  max: 1000,
  ttl: 1000 * 60 * 5, // 5 分钟
});
```

### 添加日志
```typescript
import winston from 'winston';

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'openfga.log' }),
  ],
});
```

### 添加监控
```typescript
import { Counter, Histogram } from 'prom-client';

const checkCounter = new Counter({
  name: 'openfga_check_total',
  help: 'Total number of permission checks',
});

const checkDuration = new Histogram({
  name: 'openfga_check_duration_seconds',
  help: 'Duration of permission checks',
});
```

## 故障排查

### 常见问题

1. **连接失败**
   - 检查 OpenFGA 服务器是否运行
   - 验证 `FGA_API_URL` 配置

2. **Store ID 未设置**
   - 创建 Store 并配置环境变量
   - 或在代码中调用 `createStore()`

3. **授权模型未找到**
   - 导入授权模型文件
   - 或不设置 `FGA_MODEL_ID` 使用最新模型

4. **TypeScript 编译错误**
   - 运行 `pnpm run clean`
   - 重新安装依赖: `rm -rf node_modules && pnpm install`

## 相关资源

- [OpenFGA 官方文档](https://openfga.dev/docs)
- [Node.js SDK GitHub](https://github.com/openfga/js-sdk)
- [授权模型语言参考](https://openfga.dev/docs/modeling/language)
- [OpenFGA Playground](https://play.fga.dev/)
