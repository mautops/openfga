# Flask + OAuth + OpenFGA 集成示例

这是一个完整的 Flask 应用示例，展示了如何将 OAuth 2.0 认证和 OpenFGA 授权集成在一起。

## 功能特性

### 认证功能
- ✅ OAuth 2.0 登录（支持 Google、GitHub、自定义提供商）
- ✅ JWT Token 生成和验证
- ✅ Session 管理
- ✅ 用户信息提取

### 授权功能
- ✅ OpenFGA 权限检查装饰器
- ✅ 细粒度权限控制（viewer、editor、owner）
- ✅ 权限继承（owner → editor → viewer）
- ✅ 批量权限查询优化

### 业务功能
- ✅ 文档 CRUD 操作
- ✅ 文档分享功能
- ✅ 权限管理
- ✅ 用户可访问资源列表

## 项目结构

```
05.flask-oauth-integration/
├── app.py                      # Flask 应用主文件
├── auth.py                     # OAuth 认证处理
├── permissions.py              # OpenFGA 权限检查装饰器
├── models.py                   # 数据模型（SQLite）
├── views.py                    # API 视图函数
├── authorization_model.fga     # OpenFGA 授权模型
├── requirements.txt            # Python 依赖
├── .env.example               # 环境变量示例
└── README.md                  # 本文件
```

## 快速开始

### 1. 安装依赖

```bash
# 使用 uv（推荐）
uv pip install -r requirements.txt

# 或使用 pip
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# Flask 配置
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=True
PORT=5000

# OpenFGA 配置
OPENFGA_API_URL=http://localhost:8080
OPENFGA_STORE_ID=your-store-id
OPENFGA_MODEL_ID=your-model-id

# Google OAuth（可选）
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# GitHub OAuth（可选）
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# 前端 URL
FRONTEND_URL=http://localhost:3000
```

### 3. 启动 OpenFGA

```bash
# 使用 Docker
docker run -d \
  --name openfga \
  -p 8080:8080 \
  -p 3000:3000 \
  openfga/openfga run

# 创建 Store
curl -X POST http://localhost:8080/stores \
  -H "Content-Type: application/json" \
  -d '{"name": "flask-oauth-demo"}'

# 记录返回的 store_id，填入 .env 文件
```

### 4. 上传授权模型

```bash
# 使用 OpenFGA CLI
fga model write --store-id=<your-store-id> --file=authorization_model.fga

# 或使用 curl
curl -X POST http://localhost:8080/stores/<store-id>/authorization-models \
  -H "Content-Type: application/json" \
  -d @authorization_model.json

# 记录返回的 authorization_model_id，填入 .env 文件
```

### 5. 运行应用

```bash
python app.py
```

应用将在 `http://localhost:5000` 启动。

## API 文档

### 认证端点

#### 登录
```http
GET /auth/login?provider=google
```

重定向到 OAuth 提供商的登录页面。

**查询参数：**
- `provider`: OAuth 提供商（`google`、`github`、`custom`）

#### 回调
```http
GET /auth/callback
```

OAuth 回调端点，由 OAuth 提供商调用。

#### 登出
```http
GET /auth/logout
```

清除用户 session。

#### 获取当前用户
```http
GET /auth/user
```

返回当前登录用户的信息。

**需要认证**

**响应示例：**
```json
{
  "user_id": "google|123456",
  "email": "user@example.com",
  "name": "John Doe",
  "picture": "https://...",
  "provider": "google"
}
```

### 文档端点

#### 列出文档
```http
GET /api/documents
```

列出当前用户可访问的所有文档。

**需要认证**

**响应示例：**
```json
{
  "documents": [
    {
      "id": "doc-123",
      "title": "我的文档",
      "content": "文档内容",
      "owner_id": "user-456",
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ],
  "total": 1
}
```

#### 创建文档
```http
POST /api/documents
Content-Type: application/json

{
  "title": "新文档",
  "content": "文档内容"
}
```

创建新文档，创建者自动成为所有者。

**需要认证**

**响应示例：**
```json
{
  "message": "Document created successfully",
  "document": {
    "id": "doc-789",
    "title": "新文档",
    "content": "文档内容",
    "owner_id": "user-456",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

#### 获取文档
```http
GET /api/documents/{document_id}
```

获取文档详情。

**需要认证和 viewer 权限**

#### 更新文档
```http
PUT /api/documents/{document_id}
Content-Type: application/json

{
  "title": "更新的标题",
  "content": "更新的内容"
}
```

更新文档。

**需要认证和 editor 权限**

#### 删除文档
```http
DELETE /api/documents/{document_id}
```

删除文档。

**需要认证和 owner 权限**

#### 分享文档
```http
POST /api/documents/{document_id}/share
Content-Type: application/json

{
  "user_id": "target-user-id",
  "permission": "viewer"
}
```

将文档分享给其他用户。

**需要认证和 owner 权限**

**权限类型：**
- `viewer`: 只读权限
- `editor`: 编辑权限（包含查看权限）

#### 取消分享
```http
DELETE /api/documents/{document_id}/share/{user_id}
```

取消对特定用户的分享。

**需要认证和 owner 权限**

#### 列出分享记录
```http
GET /api/documents/{document_id}/shares
```

列出文档的所有分享记录。

**需要认证和 owner 权限**

## 权限模型说明

### 权限层级

```
owner (所有者)
  ↓ 继承
editor (编辑者)
  ↓ 继承
viewer (查看者)
```

### 权限说明

- **owner**: 拥有所有权限，可以删除文档、分享文档
- **editor**: 可以编辑文档，自动拥有查看权限
- **viewer**: 只能查看文档

### 授权模型

```fga
type document
  relations
    define owner: [user]
    define editor: [user] or owner
    define viewer: [user] or editor
```

## 使用示例

### 1. 用户登录

```bash
# 访问登录页面
curl http://localhost:5000/auth/login?provider=google

# 浏览器会重定向到 Google 登录页面
# 登录成功后，会重定向回应用并设置 session
```

### 2. 创建文档

```bash
# 使用 session cookie
curl -X POST http://localhost:5000/api/documents \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "title": "我的第一个文档",
    "content": "这是文档内容"
  }'
```

### 3. 分享文档

```bash
# 分享给其他用户（viewer 权限）
curl -X POST http://localhost:5000/api/documents/doc-123/share \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "user_id": "google|789",
    "permission": "viewer"
  }'
```

### 4. 查看文档

```bash
# 其他用户查看文档
curl http://localhost:5000/api/documents/doc-123 \
  -b cookies.txt
```

## 配置 OAuth 提供商

### Google OAuth

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建项目
3. 启用 Google+ API
4. 创建 OAuth 2.0 凭据
5. 添加授权重定向 URI: `http://localhost:5000/auth/callback`
6. 复制 Client ID 和 Client Secret 到 `.env`

### GitHub OAuth

1. 访问 [GitHub Settings](https://github.com/settings/developers)
2. 创建 OAuth App
3. 设置 Authorization callback URL: `http://localhost:5000/auth/callback`
4. 复制 Client ID 和 Client Secret 到 `.env`

## 开发指南

### 添加新的权限检查

```python
from permissions import require_permission

@app.route('/documents/<document_id>/special')
@require_permission('owner', 'document', 'document_id')
def special_action(document_id):
    # 只有 owner 可以访问
    return jsonify({'message': 'Success'})
```

### 添加多权限检查

```python
from permissions import require_any_permission

@app.route('/documents/<document_id>/action')
@require_any_permission(['editor', 'owner'], 'document', 'document_id')
def some_action(document_id):
    # editor 或 owner 都可以访问
    return jsonify({'message': 'Success'})
```

### 手动检查权限

```python
from permissions import check_permission_sync

def my_function(user_id, document_id):
    has_permission = check_permission_sync(
        user_id=user_id,
        relation='viewer',
        object_id=f'document:{document_id}'
    )

    if has_permission:
        # 执行操作
        pass
```

## 测试

### 健康检查

```bash
curl http://localhost:5000/health
```

### 测试权限检查

```bash
# 1. 登录并保存 cookies
curl -c cookies.txt http://localhost:5000/auth/login?provider=google

# 2. 创建文档
curl -X POST http://localhost:5000/api/documents \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"title": "Test Doc", "content": "Content"}'

# 3. 获取文档（应该成功）
curl http://localhost:5000/api/documents/doc-id \
  -b cookies.txt

# 4. 使用另一个用户的 cookies（应该失败 403）
curl http://localhost:5000/api/documents/doc-id \
  -b other-cookies.txt
```

## 生产部署建议

### 安全配置

1. **使用 HTTPS**
   ```python
   app.config['SESSION_COOKIE_SECURE'] = True
   ```

2. **设置强密钥**
   ```bash
   # 生成随机密钥
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **配置 CORS**
   ```python
   CORS(app, origins=['https://your-frontend.com'])
   ```

### 性能优化

1. **使用 Redis 存储 Session**
   ```python
   app.config['SESSION_TYPE'] = 'redis'
   app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')
   ```

2. **添加权限检查缓存**
   ```python
   # 在 permissions.py 中添加缓存层
   from functools import lru_cache

   @lru_cache(maxsize=1000)
   def check_permission_cached(user_id, relation, object_id):
       return check_permission_sync(user_id, relation, object_id)
   ```

3. **使用生产级 WSGI 服务器**
   ```bash
   # 安装 gunicorn
   pip install gunicorn

   # 运行
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

## 故障排查

### OpenFGA 连接失败

```bash
# 检查 OpenFGA 是否运行
curl http://localhost:8080/healthz

# 检查 Store ID 是否正确
curl http://localhost:8080/stores/<store-id>
```

### OAuth 回调失败

1. 检查回调 URL 是否正确配置
2. 确认 Client ID 和 Secret 正确
3. 查看浏览器控制台的错误信息

### 权限检查失败

```bash
# 检查授权模型是否正确上传
curl http://localhost:8080/stores/<store-id>/authorization-models/<model-id>

# 检查权限关系是否存在
curl -X POST http://localhost:8080/stores/<store-id>/check \
  -H "Content-Type: application/json" \
  -d '{
    "tuple_key": {
      "user": "user:alice",
      "relation": "viewer",
      "object": "document:123"
    }
  }'
```

## 参考资料

- [Flask 文档](https://flask.palletsprojects.com/)
- [Authlib 文档](https://docs.authlib.org/)
- [OpenFGA 文档](https://openfga.dev/docs)
- [OAuth 2.0 规范](https://oauth.net/2/)

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
