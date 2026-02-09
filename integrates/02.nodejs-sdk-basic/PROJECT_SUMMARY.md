# Node.js/TypeScript SDK 集成示例 - 项目总结

## 项目概述

本项目是一个完整的 OpenFGA Node.js/TypeScript SDK 集成示例，展示了如何在 Node.js 应用中实现细粒度的权限管理。

## 创建的文件清单

### 核心代码文件 (3 个)

1. **`src/client.ts`** (432 行)
   - OpenFGA 客户端封装类
   - 提供简化的 API 接口
   - 完整的 TypeScript 类型定义
   - 全面的错误处理

2. **`src/examples.ts`** (381 行)
   - 基础使用示例
   - 10 个完整的示例场景
   - 详细的中文注释

3. **`src/advanced-examples.ts`** (513 行)
   - 高级使用场景
   - 4 个实用类：多租户、组织、文件夹、审计
   - 实际应用案例

### 配置文件 (4 个)

4. **`package.json`**
   - 项目依赖配置
   - 6 个 npm 脚本
   - 开发和生产依赖

5. **`tsconfig.json`**
   - TypeScript 编译配置
   - 严格模式启用
   - 声明文件生成

6. **`.env.example`**
   - 环境变量模板
   - 3 个配置项

7. **`authorization_model.fga`**
   - OpenFGA 授权模型定义
   - 4 种类型，多种关系
   - 权限继承规则

### 文档文件 (4 个)

8. **`README.md`** (513 行)
   - 完整的项目文档
   - 安装和使用指南
   - API 参考
   - 最佳实践和故障排查

9. **`PROJECT_OVERVIEW.md`** (326 行)
   - 所有文件的详细说明
   - 文件依赖关系
   - 开发流程指南
   - 扩展建议

10. **`QUICK_REFERENCE.md`** (约 300 行)
    - 快速参考卡片
    - 常用命令和 API
    - 代码片段
    - 故障排查表

### 辅助文件 (2 个)

11. **`.gitignore`**
    - Git 忽略规则
    - 保护敏感信息

12. **`setup.sh`**
    - 快速启动脚本
    - 自动化安装流程

## 功能特性

### ✅ 已实现的功能

1. **客户端管理**
   - 客户端初始化和配置
   - Store 和模型管理
   - 配置动态更新

2. **关系元组操作**
   - 写入关系元组
   - 删除关系元组
   - 读取关系元组
   - 事务模式（同时写入和删除）

3. **权限检查**
   - 单个权限检查
   - 批量权限检查（支持 OpenFGA v1.8.0+）
   - 上下文元组支持

4. **查询功能**
   - 列出用户可访问的对象
   - 列出可访问对象的用户
   - 支持过滤和上下文

5. **高级场景**
   - 多租户文档管理系统
   - 组织层级权限管理
   - 文件夹层级权限
   - 权限审计和报告

6. **开发体验**
   - 完整的 TypeScript 支持
   - 详细的中文注释
   - 全面的错误处理
   - 开发和生产模式

## 技术栈

- **运行时**: Node.js 18+
- **语言**: TypeScript 5.3+
- **包管理**: pnpm
- **核心依赖**: @openfga/sdk 0.7.0
- **工具**: ts-node, dotenv

## 代码统计

```
总行数: 2,264 行

TypeScript 代码: 1,326 行
  - client.ts: 432 行
  - examples.ts: 381 行
  - advanced-examples.ts: 513 行

配置文件: 72 行
  - package.json: 32 行
  - tsconfig.json: 20 行

文档: 839+ 行
  - README.md: 513 行
  - PROJECT_OVERVIEW.md: 326 行
  - QUICK_REFERENCE.md: 300+ 行
```

## 项目结构

```
02.nodejs-sdk-basic/
├── src/                          # 源代码目录
│   ├── client.ts                 # 客户端封装
│   ├── examples.ts               # 基础示例
│   └── advanced-examples.ts      # 高级示例
├── authorization_model.fga       # 授权模型
├── package.json                  # 项目配置
├── tsconfig.json                 # TS 配置
├── .env.example                  # 环境变量模板
├── .gitignore                    # Git 忽略
├── setup.sh                      # 启动脚本
├── README.md                     # 主文档
├── PROJECT_OVERVIEW.md           # 项目概览
└── QUICK_REFERENCE.md            # 快速参考
```

## 使用方法

### 快速开始

```bash
# 1. 安装依赖
pnpm install

# 2. 配置环境
cp .env.example .env
# 编辑 .env 文件

# 3. 运行示例
pnpm run dev
```

### 可用命令

```bash
pnpm run dev              # 运行基础示例（开发模式）
pnpm run dev:advanced     # 运行高级示例（开发模式）
pnpm run build            # 编译 TypeScript
pnpm start                # 运行基础示例（生产模式）
pnpm start:advanced       # 运行高级示例（生产模式）
pnpm run clean            # 清理编译输出
```

## 核心 API 示例

### 客户端初始化

```typescript
import { OpenFGAClient } from './client';

const client = new OpenFGAClient({
  apiUrl: 'http://localhost:8080',
  storeId: 'your-store-id',
  authorizationModelId: 'your-model-id',
});
```

### 权限检查

```typescript
const canView = await client.check(
  'user:alice',
  'viewer',
  'document:roadmap'
);
```

### 批量检查

```typescript
const result = await client.batchCheck([
  { user: 'user:alice', relation: 'viewer', object: 'document:1' },
  { user: 'user:bob', relation: 'editor', object: 'document:2' },
]);
```

### 列出对象

```typescript
const documents = await client.listObjects(
  'user:alice',
  'viewer',
  'document'
);
```

## 授权模型

### 支持的类型

- **user**: 用户
- **organization**: 组织（成员、管理员）
- **folder**: 文件夹（所有者、查看者、编辑者）
- **document**: 文档（所有者、查看者、编辑者、删除者）

### 权限继承

- 文档继承父文件夹的权限
- 组织成员可以访问组织内的资源
- 所有者拥有所有权限

## 最佳实践

1. **客户端单例**: 在应用中只初始化一次客户端
2. **环境变量**: 使用环境变量管理配置
3. **批量操作**: 使用批量 API 提高性能
4. **错误处理**: 始终使用 try-catch 处理错误
5. **类型安全**: 充分利用 TypeScript 类型系统

## 性能优化

- 客户端重用和连接池
- 批量 API 减少网络请求
- 可选的缓存层
- 合理的超时设置

## 安全考虑

- 环境变量管理敏感信息
- 不在代码中硬编码配置
- 定期审计权限设置
- 最小权限原则

## 扩展性

### 可以添加的功能

1. **缓存层**: 使用 LRU 缓存提高性能
2. **日志系统**: 集成 Winston 或 Pino
3. **监控指标**: 使用 Prometheus 监控
4. **单元测试**: 使用 Jest 编写测试
5. **API 中间件**: 集成到 Express/Fastify

### 集成建议

```typescript
// 在 Express 中使用
app.use(async (req, res, next) => {
  const canAccess = await fgaClient.check(
    req.user.id,
    'viewer',
    req.params.resourceId
  );

  if (!canAccess) {
    return res.status(403).json({ error: 'Forbidden' });
  }

  next();
});
```

## 故障排查

| 问题 | 解决方案 |
|------|---------|
| 连接失败 | 检查 OpenFGA 服务器状态 |
| Store ID 未设置 | 创建 Store 并配置环境变量 |
| 模型未找到 | 导入授权模型文件 |
| 编译错误 | 清理并重新编译 |

## 相关资源

- [OpenFGA 官方文档](https://openfga.dev/docs)
- [Node.js SDK GitHub](https://github.com/openfga/js-sdk)
- [授权模型语言参考](https://openfga.dev/docs/modeling/language)
- [OpenFGA Playground](https://play.fga.dev/)

## 项目亮点

1. ✅ **完整性**: 涵盖所有核心功能和高级场景
2. ✅ **实用性**: 提供可直接使用的代码和类
3. ✅ **文档化**: 详细的中文文档和注释
4. ✅ **类型安全**: 完整的 TypeScript 类型定义
5. ✅ **最佳实践**: 遵循 Node.js 和 OpenFGA 最佳实践
6. ✅ **易用性**: 简化的 API 和快速启动脚本
7. ✅ **可扩展**: 模块化设计，易于扩展

## 适用场景

- 多租户 SaaS 应用
- 文档管理系统
- 企业协作平台
- 内容管理系统
- API 权限控制
- 微服务权限管理

## 学习路径

1. **初学者**: 阅读 README.md，运行 examples.ts
2. **进阶者**: 学习 advanced-examples.ts 中的实用类
3. **高级用户**: 阅读 client.ts 源码，理解封装原理
4. **集成者**: 参考 PROJECT_OVERVIEW.md 集成到项目

## 维护和更新

- 定期更新依赖包
- 关注 OpenFGA SDK 新版本
- 根据反馈改进文档
- 添加更多实用场景

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

---

**项目创建时间**: 2026-02-05
**OpenFGA SDK 版本**: 0.7.0
**TypeScript 版本**: 5.3.3
**Node.js 版本**: 18+
