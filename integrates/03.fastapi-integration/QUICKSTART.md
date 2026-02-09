# FastAPI + OpenFGA 快速参考

## 文件说明

| 文件 | 说明 |
|------|------|
| `main.py` | FastAPI 应用主文件，包含所有 API 路由 |
| `auth.py` | JWT 认证中间件，处理用户认证 |
| `permissions.py` | OpenFGA 权限检查装饰器 |
| `models.py` | Pydantic 数据模型定义 |
| `config.py` | 应用配置管理 |
| `openfga_client.py` | OpenFGA 客户端封装 |
| `requirements.txt` | Python 依赖列表 |
| `.env.example` | 环境变量示例 |
| `authorization_model.json` | OpenFGA 授权模型定义 |
| `test_api.py` | API 测试脚本 |
| `start.sh` | 快速启动脚本 |
| `docker-compose.yml` | Docker Compose 配置 |
| `Dockerfile` | Docker 镜像构建文件 |

## 快速启动

### 方式 1: 使用启动脚本（推荐）

```bash
./start.sh
```

### 方式 2: 手动启动

```bash
# 1. 启动 OpenFGA
docker run -d --name openfga -p 8080:8080 openfga/openfga run

# 2. 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，填写 OPENFGA_STORE_ID

# 4. 启动应用
uvicorn main:app --reload
```

### 方式 3: 使用 Docker Compose

```bash
# 先配置 .env 文件
cp .env.example .env

# 启动所有服务
docker-compose up -d
```

## 初始化 OpenFGA

### 1. 创建 Store

```bash
curl -X POST http://localhost:8080/stores \
  -H "Content-Type: application/json" \
  -d '{"name": "fastapi-demo"}'
```

记录返回的 `store_id`。

### 2. 创建授权模型

```bash
curl -X POST http://localhost:8080/stores/{store_id}/authorization-models \
  -H "Content-Type: application/json" \
  -d @authorization_model.json
```

### 3. 配置环境变量

编辑 `.env` 文件，填写 `OPENFGA_STORE_ID`。

## API 端点

### 健康检查

```bash
GET /health
```

### 用户管理

```bash
# 创建用户
POST /api/users
{
  "email": "alice@example.com",
  "name": "Alice"
}

# 获取当前用户信息
GET /api/users/me
Authorization: Bearer <token>
```

### 文档管理

```bash
# 创建文档
POST /api/documents
Authorization: Bearer <token>
{
  "title": "我的文档",
  "content": "文档内容"
}

# 获取文档
GET /api/documents/{document_id}
Authorization: Bearer <token>

# 更新文档
PUT /api/documents/{document_id}
Authorization: Bearer <token>
{
  "title": "新标题",
  "content": "新内容"
}

# 删除文档
DELETE /api/documents/{document_id}
Authorization: Bearer <token>

# 列出可访问的文档
GET /api/documents
Authorization: Bearer <token>
```

### 权限管理

```bash
# 分享文档
POST /api/documents/{document_id}/share?target_user_id=user_2&relation=viewer
Authorization: Bearer <token>

# 撤销权限
DELETE /api/documents/{document_id}/share?target_user_id=user_2&relation=viewer
Authorization: Bearer <token>
```

## 生成测试 Token

```bash
python auth.py
```

会输出测试用户的 token。

## 运行测试

```bash
# 确保应用已启动
python test_api.py
```

## 权限关系

- `owner`: 所有者，拥有所有权限
- `editor`: 编辑者，可以查看和编辑
- `viewer`: 查看者，只能查看

## 常用命令

```bash
# 查看 OpenFGA 日志
docker logs openfga

# 停止 OpenFGA
docker stop openfga

# 重启 OpenFGA
docker restart openfga

# 查看应用日志
# 如果使用 uvicorn --reload，日志会直接输出到终端

# 检查 OpenFGA 健康状态
curl http://localhost:8080/healthz
```

## 故障排查

### OpenFGA 连接失败

```bash
# 检查 OpenFGA 是否运行
docker ps | grep openfga

# 检查端口是否被占用
lsof -i :8080
```

### Token 验证失败

- 检查 JWT_SECRET_KEY 是否一致
- 检查 token 是否过期
- 检查 Authorization header 格式: `Bearer <token>`

### 权限检查失败

- 检查 OPENFGA_STORE_ID 是否正确
- 检查授权模型是否已创建
- 检查权限关系是否已写入

## 开发建议

1. 使用 Swagger UI 测试 API: http://localhost:8000/docs
2. 查看 ReDoc 文档: http://localhost:8000/redoc
3. 使用 `python auth.py` 生成测试 token
4. 使用 `python test_api.py` 运行完整测试
5. 修改代码后，uvicorn 会自动重载

## 生产环境部署

1. 修改 `.env` 中的 `JWT_SECRET_KEY`
2. 设置 `DEBUG=false`
3. 限制 `CORS_ORIGINS` 为具体域名
4. 使用 Gunicorn 或 Docker 部署
5. 配置 HTTPS
6. 使用生产级数据库（PostgreSQL）
7. 配置日志收集和监控

## 扩展功能

- 添加用户组支持
- 添加 Redis 缓存
- 添加审计日志
- 添加速率限制
- 添加 WebSocket 支持
- 集成真实数据库（PostgreSQL/MySQL）
