# 项目概览

## FastAPI + OpenFGA 集成示例

这是一个完整的生产级 FastAPI + OpenFGA 集成示例，展示了如何在现代 Python Web 应用中实现细粒度的权限控制。

## 核心特性

### 1. 认证系统
- **JWT Token 认证**: 使用 python-jose 实现标准 JWT 认证
- **Bearer Token**: 支持标准的 HTTP Bearer 认证方案
- **Token 生成工具**: 提供测试 token 生成脚本

### 2. 权限控制
- **装饰器模式**: 使用 FastAPI 依赖注入实现权限检查
- **细粒度权限**: 支持 viewer、editor、owner 三级权限
- **动态权限检查**: 根据 HTTP 方法自动选择权限类型
- **批量权限查询**: 使用 OpenFGA ListObjects API 优化性能

### 3. API 设计
- **RESTful API**: 遵循 REST 设计原则
- **异步处理**: 全面使用 async/await 提升性能
- **自动文档**: 集成 Swagger UI 和 ReDoc
- **错误处理**: 统一的异常处理机制

### 4. 代码质量
- **类型注解**: 完整的 Python 类型提示
- **Pydantic 验证**: 自动的请求/响应验证
- **详细注释**: 中文注释，易于理解
- **最佳实践**: 遵循 FastAPI 和 OpenFGA 最佳实践

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 编程语言 |
| FastAPI | 0.109+ | Web 框架 |
| Pydantic | 2.5+ | 数据验证 |
| OpenFGA SDK | 0.5+ | 权限管理 |
| python-jose | 3.3+ | JWT 处理 |
| uvicorn | 0.27+ | ASGI 服务器 |

## 项目结构

```
03.fastapi-integration/
├── main.py                    # 主应用文件（400+ 行）
│   ├── 健康检查端点
│   ├── 用户管理 API
│   ├── 文档 CRUD API
│   └── 权限管理 API
│
├── auth.py                    # 认证模块（200+ 行）
│   ├── JWT Token 生成
│   ├── Token 验证
│   └── 用户提取依赖
│
├── permissions.py             # 权限模块（300+ 行）
│   ├── 权限检查装饰器
│   ├── 多权限检查
│   ├── 直接权限检查
│   └── 批量权限过滤
│
├── openfga_client.py         # OpenFGA 客户端（300+ 行）
│   ├── 权限检查
│   ├── 写入/删除元组
│   ├── 列出对象
│   └── 读取/展开权限树
│
├── models.py                  # 数据模型（200+ 行）
│   ├── 用户模型
│   ├── 文档模型
│   ├── 权限模型
│   └── 响应模型
│
├── config.py                  # 配置管理（100+ 行）
│   ├── 环境变量管理
│   ├── 配置验证
│   └── 默认值设置
│
├── test_api.py               # 测试脚本（300+ 行）
│   ├── 完整的 API 测试
│   ├── 权限场景测试
│   └── 自动化测试流程
│
├── authorization_model.json  # OpenFGA 授权模型
├── requirements.txt          # Python 依赖
├── .env.example             # 环境变量示例
├── start.sh                 # 快速启动脚本
├── docker-compose.yml       # Docker Compose 配置
├── Dockerfile               # Docker 镜像定义
├── README.md                # 完整文档
└── QUICKSTART.md            # 快速参考
```

## 代码统计

```
文件数量: 13 个
代码行数: ~2000 行
注释行数: ~500 行
文档行数: ~800 行
```

## API 端点

### 健康检查
- `GET /health` - 应用健康检查

### 用户管理
- `POST /api/users` - 创建用户
- `GET /api/users/me` - 获取当前用户信息

### 文档管理
- `POST /api/documents` - 创建文档（需要认证）
- `GET /api/documents/{id}` - 获取文档（需要 viewer 权限）
- `PUT /api/documents/{id}` - 更新文档（需要 editor 权限）
- `DELETE /api/documents/{id}` - 删除文档（需要 owner 权限）
- `GET /api/documents` - 列出可访问的文档

### 权限管理
- `POST /api/documents/{id}/share` - 分享文档（需要 owner 权限）
- `DELETE /api/documents/{id}/share` - 撤销权限（需要 owner 权限）

## 权限模型

```
用户 (user)
  └─ 可以拥有对文档的权限

文档 (document)
  ├─ owner: 所有者
  │   └─ 可以查看、编辑、删除、分享
  ├─ editor: 编辑者
  │   └─ 可以查看、编辑
  └─ viewer: 查看者
      └─ 只能查看

个人资料 (profile)
  └─ owner: 所有者
```

## 使用场景

### 场景 1: 文档协作
1. Alice 创建文档，自动成为 owner
2. Alice 将 viewer 权限分享给 Bob
3. Bob 可以查看文档，但不能编辑
4. Alice 将 editor 权限授予 Bob
5. Bob 现在可以编辑文档

### 场景 2: 权限继承
1. 创建用户时，自动获得对自己 profile 的 owner 权限
2. 创建文档时，创建者自动成为 owner
3. Owner 可以授予其他用户权限

### 场景 3: 权限撤销
1. Owner 可以随时撤销其他用户的权限
2. 撤销后，用户立即失去访问权限
3. 支持精确的权限控制（viewer/editor/owner）

## 性能优化

### 1. 异步处理
- 所有 I/O 操作使用 async/await
- 并发处理多个请求
- 非阻塞的权限检查

### 2. 批量查询
- 使用 ListObjects API 代替逐个 Check
- 减少网络往返次数
- 提升列表查询性能

### 3. 缓存策略（可扩展）
- 权限检查结果缓存
- Redis 集成支持
- 缓存失效机制

## 安全特性

### 1. 认证安全
- JWT Token 签名验证
- Token 过期时间控制
- Bearer Token 标准

### 2. 权限安全
- 细粒度权限控制
- 最小权限原则
- 权限检查前置

### 3. 数据安全
- 请求数据验证（Pydantic）
- SQL 注入防护（使用 ORM）
- CORS 配置

## 测试覆盖

### 自动化测试
- 健康检查测试
- 用户创建测试
- 文档 CRUD 测试
- 权限检查测试
- 分享/撤销测试

### 测试场景
- 正常流程测试
- 权限拒绝测试
- 错误处理测试
- 边界条件测试

## 部署选项

### 1. 本地开发
```bash
./start.sh
```

### 2. Docker 部署
```bash
docker-compose up -d
```

### 3. 生产部署
- Gunicorn + Uvicorn Workers
- Nginx 反向代理
- HTTPS 配置
- 日志收集
- 监控告警

## 扩展方向

### 1. 功能扩展
- [ ] 用户组支持
- [ ] 文件夹层级
- [ ] 标签系统
- [ ] 搜索功能
- [ ] 版本控制

### 2. 性能优化
- [ ] Redis 缓存
- [ ] 数据库连接池
- [ ] 查询优化
- [ ] CDN 集成

### 3. 安全增强
- [ ] 速率限制
- [ ] IP 白名单
- [ ] 审计日志
- [ ] 敏感数据加密

### 4. 运维支持
- [ ] 健康检查增强
- [ ] Prometheus 指标
- [ ] 分布式追踪
- [ ] 日志聚合

## 学习价值

### 适合学习的内容
1. **FastAPI 最佳实践**: 依赖注入、中间件、异常处理
2. **OpenFGA 集成**: 权限模型设计、API 使用
3. **JWT 认证**: Token 生成、验证、刷新
4. **异步编程**: async/await、并发处理
5. **API 设计**: RESTful、版本控制、文档生成
6. **Docker 部署**: 容器化、编排、环境管理

### 代码亮点
- 清晰的代码结构
- 完整的类型注解
- 详细的中文注释
- 实用的工具函数
- 完善的错误处理

## 参考资料

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [OpenFGA 官方文档](https://openfga.dev/docs)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [JWT 标准](https://jwt.io/)

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
