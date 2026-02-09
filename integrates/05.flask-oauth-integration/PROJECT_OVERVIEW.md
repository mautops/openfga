# Flask + OAuth + OpenFGA 集成示例 - 项目概览

## 项目信息

- **项目名称**: Flask + OAuth + OpenFGA 集成示例
- **创建日期**: 2026-02-05
- **技术栈**: Flask, OAuth 2.0, OpenFGA, SQLite
- **参考章节**: 第13章 - 系统集成实践

## 项目结构

```
05.flask-oauth-integration/
├── app.py                      # Flask 应用主文件
├── auth.py                     # OAuth 认证处理模块
├── permissions.py              # OpenFGA 权限检查装饰器
├── models.py                   # 数据模型（SQLite）
├── views.py                    # API 视图函数
├── authorization_model.fga     # OpenFGA 授权模型定义
├── requirements.txt            # Python 依赖列表
├── .env.example               # 环境变量示例
├── .gitignore                 # Git 忽略文件
├── Dockerfile                 # Docker 镜像定义
├── docker-compose.yml         # Docker Compose 配置
├── start.sh                   # 启动脚本
├── test_api.py                # API 测试脚本
├── README.md                  # 完整文档
├── QUICKSTART.md              # 快速入门指南
└── PROJECT_OVERVIEW.md        # 本文件
```

## 核心功能

### 1. 认证功能（auth.py）

- **OAuth 2.0 集成**
  - 支持 Google OAuth
  - 支持 GitHub OAuth
  - 支持自定义 OAuth 服务器

- **Token 管理**
  - JWT Token 生成
  - JWT Token 验证
  - Session 管理

- **装饰器**
  - `@require_auth`: 要求用户已登录
  - `get_current_user()`: 获取当前用户信息

### 2. 权限管理（permissions.py）

- **OpenFGA 集成**
  - 同步权限检查
  - 异步权限检查
  - 批量权限操作

- **权限装饰器**
  - `@require_permission(relation, object_type)`: 单一权限检查
  - `@require_any_permission(relations, object_type)`: 多权限检查

- **权限操作**
  - `grant_permission()`: 授予权限
  - `revoke_permission()`: 撤销权限
  - `list_user_objects()`: 列出用户可访问的对象

### 3. 数据模型（models.py）

- **Document 模型**
  - 创建文档
  - 获取文档
  - 更新文档
  - 删除文档
  - 批量查询

- **Share 模型**
  - 创建分享记录
  - 查询分享记录
  - 删除分享记录

### 4. API 端点（views.py）

#### 文档管理
- `GET /api/documents` - 列出可访问的文档
- `POST /api/documents` - 创建文档
- `GET /api/documents/<id>` - 获取文档详情
- `PUT /api/documents/<id>` - 更新文档
- `DELETE /api/documents/<id>` - 删除文档

#### 分享管理
- `POST /api/documents/<id>/share` - 分享文档
- `DELETE /api/documents/<id>/share/<user_id>` - 取消分享
- `GET /api/documents/<id>/shares` - 列出分享记录

## 权限模型

### 权限层级

```
owner (所有者)
  ↓ 继承
editor (编辑者)
  ↓ 继承
viewer (查看者)
```

### 权限说明

| 权限 | 查看 | 编辑 | 删除 | 分享 |
|------|------|------|------|------|
| viewer | ✓ | ✗ | ✗ | ✗ |
| editor | ✓ | ✓ | ✗ | ✗ |
| owner | ✓ | ✓ | ✓ | ✓ |

### OpenFGA 模型定义

```fga
type document
  relations
    define owner: [user]
    define editor: [user] or owner
    define viewer: [user] or editor
```

## 技术特点

### 1. 认证与授权分离

- **认证**: OAuth 2.0 处理用户身份验证
- **授权**: OpenFGA 处理细粒度权限控制
- **优势**: 职责清晰，易于维护和扩展

### 2. 装饰器模式

```python
@app.route('/documents/<document_id>')
@require_auth
@require_permission('viewer', 'document', 'document_id')
def get_document(document_id):
    # 业务逻辑
    pass
```

- 代码简洁
- 易于理解
- 可复用

### 3. 权限继承

- owner 自动拥有 editor 和 viewer 权限
- editor 自动拥有 viewer 权限
- 减少权限关系数量，提高性能

### 4. 批量查询优化

使用 `list_user_objects()` 一次性获取用户可访问的所有对象，避免 N+1 查询问题。

## 配置说明

### 必需配置

```env
# Flask 密钥
SECRET_KEY=<随机生成的密钥>

# OpenFGA 配置
OPENFGA_API_URL=http://localhost:8080
OPENFGA_STORE_ID=<Store ID>
OPENFGA_MODEL_ID=<Model ID>
```

### OAuth 配置（至少配置一个）

```env
# Google OAuth
GOOGLE_CLIENT_ID=<Client ID>
GOOGLE_CLIENT_SECRET=<Client Secret>

# 或 GitHub OAuth
GITHUB_CLIENT_ID=<Client ID>
GITHUB_CLIENT_SECRET=<Client Secret>
```

## 部署方式

### 1. 本地开发

```bash
./start.sh
```

### 2. Docker

```bash
docker build -t flask-oauth-openfga .
docker run -p 5000:5000 --env-file .env flask-oauth-openfga
```

### 3. Docker Compose

```bash
docker-compose up -d
```

## 测试

### 自动化测试

```bash
python test_api.py
```

### 手动测试

1. 访问 `http://localhost:5000/auth/login?provider=google`
2. 完成 OAuth 登录
3. 使用 API 创建和管理文档

## 安全考虑

### 1. Session 安全

- 使用 HTTPS（生产环境）
- 设置 `SESSION_COOKIE_SECURE=True`
- 设置 `SESSION_COOKIE_HTTPONLY=True`

### 2. 密钥管理

- 使用强随机密钥
- 不要将密钥提交到版本控制
- 定期轮换密钥

### 3. OAuth 安全

- 验证回调 URL
- 使用 state 参数防止 CSRF
- 安全存储 Client Secret

### 4. 权限检查

- 所有敏感操作都进行权限检查
- 使用装饰器确保不遗漏
- 记录权限检查日志

## 性能优化

### 1. 权限检查缓存

可以添加缓存层减少 OpenFGA 调用：

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def check_permission_cached(user_id, relation, object_id):
    return check_permission_sync(user_id, relation, object_id)
```

### 2. 批量查询

使用 `list_user_objects()` 代替逐个检查权限。

### 3. 数据库优化

- 添加索引
- 使用连接池
- 考虑使用 PostgreSQL 替代 SQLite

## 扩展建议

### 1. 添加更多 OAuth 提供商

- Microsoft
- Apple
- 企业 SSO（SAML）

### 2. 增强权限模型

```fga
type folder
  relations
    define owner: [user]
    define viewer: [user] or owner

type document
  relations
    define parent: [folder]
    define owner: [user]
    define viewer: [user] or owner or viewer from parent
```

### 3. 添加审计日志

记录所有权限变更和敏感操作。

### 4. 实现权限缓存

使用 Redis 缓存权限检查结果。

## 常见问题

### Q: 如何添加新的资源类型？

1. 在 `authorization_model.fga` 中定义新类型
2. 在 `models.py` 中创建数据模型
3. 在 `views.py` 中添加 API 端点
4. 使用 `@require_permission` 装饰器保护端点

### Q: 如何支持团队/组织？

在授权模型中添加 `group` 类型：

```fga
type group
  relations
    define member: [user]

type document
  relations
    define owner: [user, group#member]
    define viewer: [user, group#member] or owner
```

### Q: 如何处理权限继承？

OpenFGA 的 `or` 和 `from` 关键字支持权限继承。

## 参考资料

- [Flask 文档](https://flask.palletsprojects.com/)
- [Authlib 文档](https://docs.authlib.org/)
- [OpenFGA 文档](https://openfga.dev/docs)
- [第13章 - 系统集成实践](../../chapters/第13章-系统集成实践.md)

## 维护者

本示例基于《OpenFGA 权限管理实战》第13章内容创建。

## 许可证

MIT License
