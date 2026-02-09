# FastAPI + OpenFGA 集成示例

这是一个完整的 FastAPI + OpenFGA 集成示例，展示了如何在 FastAPI 应用中实现基于 OpenFGA 的细粒度权限控制。

## 功能特性

- ✅ JWT 认证中间件
- ✅ OpenFGA 权限检查装饰器
- ✅ 文档 CRUD API（带权限检查）
- ✅ 用户管理 API
- ✅ 健康检查端点
- ✅ 完整的错误处理
- ✅ 详细的中文注释
- ✅ 异步 API 设计

## 权限场景

本示例实现了以下权限场景：

- **创建文档**：需要认证，创建者自动成为 owner
- **查看文档**：需要 `viewer` 权限
- **编辑文档**：需要 `editor` 权限
- **删除文档**：需要 `owner` 权限
- **分享文档**：owner 可以授予其他用户 viewer 或 editor 权限

## 目录结构

```
03.fastapi-integration/
├── main.py              # FastAPI 应用主文件
├── auth.py              # JWT 认证中间件
├── permissions.py       # OpenFGA 权限检查装饰器
├── models.py            # Pydantic 数据模型
├── config.py            # 应用配置
├── openfga_client.py    # OpenFGA 客户端封装
├── requirements.txt     # Python 依赖
├── .env.example         # 环境变量示例
└── README.md            # 本文件
```

## 快速开始

### 1. 安装依赖

使用 uv（推荐）:

```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate  # Windows

# 安装依赖
uv pip install -r requirements.txt
```

或使用 pip:

```bash
pip install -r requirements.txt
```

### 2. 启动 OpenFGA 服务

使用 Docker 启动 OpenFGA:

```bash
docker run -d \
  --name openfga \
  -p 8080:8080 \
  -p 3000:3000 \
  openfga/openfga run
```

### 3. 创建 Store 和授权模型

```bash
# 创建 Store
curl -X POST http://localhost:8080/stores \
  -H "Content-Type: application/json" \
  -d '{"name": "fastapi-demo"}'

# 记录返回的 store_id，例如: 01HQXYZ...

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
            "this": {}
          },
          "viewer": {
            "this": {}
          }
        },
        "metadata": {
          "relations": {
            "owner": {
              "directly_related_user_types": [
                {"type": "user"}
              ]
            },
            "editor": {
              "directly_related_user_types": [
                {"type": "user"}
              ]
            },
            "viewer": {
              "directly_related_user_types": [
                {"type": "user"}
              ]
            }
          }
        }
      }
    ]
  }'
```

### 4. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置:

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写 `OPENFGA_STORE_ID`:

```env
OPENFGA_STORE_ID=01HQXYZ...  # 替换为你的 Store ID
```

### 5. 启动应用

```bash
# 开发模式（自动重载）
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 或直接运行
python main.py
```

应用将在 http://localhost:8000 启动。

### 6. 访问 API 文档

打开浏览器访问:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 使用示例

### 1. 生成测试 Token

```bash
# 运行 auth.py 生成测试 token
python auth.py
```

会输出类似:

```
用户: user_1 (alice@example.com)
Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 2. 创建用户

```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "name": "Alice"
  }'
```

### 3. 创建文档

```bash
# 使用 Alice 的 token
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST http://localhost:8000/api/documents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "我的第一个文档",
    "content": "这是文档内容..."
  }'
```

### 4. 查看文档

```bash
curl -X GET http://localhost:8000/api/documents/doc_1 \
  -H "Authorization: Bearer $TOKEN"
```

### 5. 分享文档

```bash
# Alice 将文档分享给 Bob（授予 viewer 权限）
curl -X POST http://localhost:8000/api/documents/doc_1/share \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target_user_id": "user_2",
    "relation": "viewer"
  }'
```

### 6. 列出可访问的文档

```bash
curl -X GET http://localhost:8000/api/documents \
  -H "Authorization: Bearer $TOKEN"
```

## 权限模型说明

本示例使用的 OpenFGA 授权模型:

```
type user

type document
  relations
    define owner: [user]
    define editor: [user]
    define viewer: [user]
```

权限层级:
- `owner`: 拥有所有权限（查看、编辑、删除、分享）
- `editor`: 可以查看和编辑文档
- `viewer`: 只能查看文档

## 代码结构说明

### main.py

主应用文件，包含:
- FastAPI 应用初始化
- 路由定义
- 业务逻辑实现

### auth.py

JWT 认证模块，提供:
- `create_access_token()`: 创建 JWT token
- `verify_token()`: 验证 JWT token
- `get_current_user()`: FastAPI 依赖，提取当前用户

### permissions.py

权限检查模块，提供:
- `require_permission()`: 权限检查装饰器
- `require_any_permission()`: 多权限检查
- `check_permission_direct()`: 直接权限检查

### openfga_client.py

OpenFGA 客户端封装，提供:
- `check_permission()`: 检查权限
- `write_tuples()`: 写入权限关系
- `delete_tuples()`: 删除权限关系
- `list_objects()`: 列出可访问对象

### models.py

Pydantic 数据模型，定义:
- 请求模型（Create, Update）
- 响应模型（User, Document）
- 通用模型（Error, Health）

### config.py

应用配置，使用 Pydantic Settings 管理环境变量。

## 测试

### 手动测试

1. 启动应用和 OpenFGA
2. 使用 `python auth.py` 生成测试 token
3. 使用 curl 或 Postman 测试 API

### 使用 Swagger UI 测试

1. 访问 http://localhost:8000/docs
2. 点击右上角 "Authorize" 按钮
3. 输入 token（格式：`Bearer <token>`）
4. 测试各个 API 端点

## 生产环境部署

### 1. 修改配置

生产环境需要修改以下配置:

```env
# 使用强密钥
JWT_SECRET_KEY=<使用 openssl rand -hex 32 生成>

# 关闭调试模式
DEBUG=false

# 限制 CORS 来源
CORS_ORIGINS=https://yourdomain.com

# 使用生产环境的 OpenFGA
OPENFGA_API_URL=https://openfga.yourdomain.com
```

### 2. 使用 Gunicorn

```bash
# 安装 gunicorn
pip install gunicorn

# 启动应用（4 个 worker）
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### 3. 使用 Docker

创建 `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

构建和运行:

```bash
docker build -t fastapi-openfga .
docker run -d -p 8000:8000 --env-file .env fastapi-openfga
```

## 常见问题

### Q: OpenFGA 连接失败

**A:** 检查:
1. OpenFGA 服务是否启动: `docker ps | grep openfga`
2. 端口是否正确: 默认 8080
3. Store ID 是否正确配置

### Q: Token 验证失败

**A:** 检查:
1. Token 是否过期
2. JWT_SECRET_KEY 是否一致
3. Authorization header 格式: `Bearer <token>`

### Q: 权限检查失败

**A:** 检查:
1. 权限关系是否已写入 OpenFGA
2. 用户 ID 和对象 ID 格式是否正确
3. 授权模型是否正确配置

### Q: 如何添加新的对象类型？

**A:**
1. 在 OpenFGA 授权模型中添加新类型
2. 在 `models.py` 中添加对应的 Pydantic 模型
3. 在 `main.py` 中添加 CRUD 路由
4. 使用 `require_permission()` 装饰器保护路由

## 扩展建议

### 1. 添加数据库

使用 SQLAlchemy 或 Tortoise ORM 替换内存数据库:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
```

### 2. 添加缓存

使用 Redis 缓存权限检查结果:

```python
import redis

redis_client = redis.Redis(host='localhost', port=6379)

async def check_permission_cached(user, relation, object_id):
    cache_key = f"perm:{user}:{relation}:{object_id}"
    cached = redis_client.get(cache_key)

    if cached:
        return json.loads(cached)

    allowed = await openfga_service.check_permission(...)
    redis_client.setex(cache_key, 300, json.dumps(allowed))

    return allowed
```

### 3. 添加用户组

在授权模型中添加 group 类型:

```json
{
  "type": "group",
  "relations": {
    "member": {
      "this": {}
    }
  }
}
```

### 4. 添加审计日志

记录所有权限变更:

```python
async def write_tuples_with_audit(tuples):
    await openfga_service.write_tuples(tuples)

    for t in tuples:
        await audit_log.create({
            "action": "grant_permission",
            "user": t["user"],
            "relation": t["relation"],
            "object": t["object"],
            "timestamp": datetime.utcnow()
        })
```

## 参考资料

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [OpenFGA 官方文档](https://openfga.dev/docs)
- [OpenFGA Python SDK](https://github.com/openfga/python-sdk)
- [JWT 介绍](https://jwt.io/)

## 许可证

MIT License

## 作者

本示例基于《OpenFGA 权威指南》第 13 章内容编写。
