# Flask + OAuth + OpenFGA 快速入门

这是一个 5 分钟快速入门指南，帮助你快速运行示例。

## 前置要求

- Python 3.9+
- Docker（用于运行 OpenFGA）
- Google 或 GitHub 账号（用于 OAuth 登录）

## 快速开始

### 1. 启动 OpenFGA

```bash
# 使用 Docker 启动 OpenFGA
docker run -d \
  --name openfga \
  -p 8080:8080 \
  -p 3000:3000 \
  openfga/openfga run

# 验证 OpenFGA 运行
curl http://localhost:8080/healthz
```

### 2. 创建 Store 和授权模型

```bash
# 创建 Store
STORE_RESPONSE=$(curl -X POST http://localhost:8080/stores \
  -H "Content-Type: application/json" \
  -d '{"name": "flask-oauth-demo"}')

# 提取 Store ID
STORE_ID=$(echo $STORE_RESPONSE | jq -r '.id')
echo "Store ID: $STORE_ID"

# 上传授权模型
MODEL_RESPONSE=$(curl -X POST "http://localhost:8080/stores/$STORE_ID/authorization-models" \
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
            "union": {
              "child": [
                {"this": {}},
                {"computedUserset": {"relation": "owner"}}
              ]
            }
          },
          "viewer": {
            "union": {
              "child": [
                {"this": {}},
                {"computedUserset": {"relation": "editor"}}
              ]
            }
          }
        }
      }
    ]
  }')

# 提取 Model ID
MODEL_ID=$(echo $MODEL_RESPONSE | jq -r '.authorization_model_id')
echo "Model ID: $MODEL_ID"
```

### 3. 配置 OAuth

#### 选项 A: Google OAuth

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建项目或选择现有项目
3. 启用 Google+ API
4. 创建 OAuth 2.0 凭据：
   - 应用类型：Web 应用
   - 授权重定向 URI：`http://localhost:5000/auth/callback`
5. 复制 Client ID 和 Client Secret

#### 选项 B: GitHub OAuth

1. 访问 [GitHub Settings > Developer settings > OAuth Apps](https://github.com/settings/developers)
2. 点击 "New OAuth App"
3. 填写信息：
   - Application name: Flask OAuth Demo
   - Homepage URL: `http://localhost:5000`
   - Authorization callback URL: `http://localhost:5000/auth/callback`
4. 复制 Client ID 和 Client Secret

### 4. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
nano .env
```

填写以下配置：

```env
# 生成随机密钥
SECRET_KEY=<运行: python -c "import secrets; print(secrets.token_hex(32))">

# OpenFGA 配置
OPENFGA_STORE_ID=<步骤2中的 Store ID>
OPENFGA_MODEL_ID=<步骤2中的 Model ID>

# Google OAuth（如果使用 Google）
GOOGLE_CLIENT_ID=<你的 Google Client ID>
GOOGLE_CLIENT_SECRET=<你的 Google Client Secret>

# GitHub OAuth（如果使用 GitHub）
GITHUB_CLIENT_ID=<你的 GitHub Client ID>
GITHUB_CLIENT_SECRET=<你的 GitHub Client Secret>
```

### 5. 安装依赖并启动

```bash
# 使用启动脚本（推荐）
./start.sh

# 或手动启动
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

应用将在 `http://localhost:5000` 启动。

## 测试功能

### 1. 登录

访问：`http://localhost:5000/auth/login?provider=google`

或：`http://localhost:5000/auth/login?provider=github`

### 2. 创建文档

```bash
# 登录后，使用浏览器的 cookies
curl -X POST http://localhost:5000/api/documents \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "title": "我的第一个文档",
    "content": "这是文档内容"
  }'
```

### 3. 查看文档列表

```bash
curl http://localhost:5000/api/documents \
  -b cookies.txt
```

### 4. 分享文档

```bash
curl -X POST http://localhost:5000/api/documents/<document-id>/share \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "user_id": "another-user-id",
    "permission": "viewer"
  }'
```

## 使用 Docker Compose

如果你想使用 Docker Compose 一键启动所有服务：

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f flask-app

# 停止服务
docker-compose down
```

## 常见问题

### Q: OAuth 回调失败

**A:** 检查以下几点：
1. 回调 URL 是否正确配置为 `http://localhost:5000/auth/callback`
2. Client ID 和 Secret 是否正确
3. OAuth 应用是否已启用

### Q: 权限检查失败

**A:** 确认：
1. OpenFGA 正在运行
2. Store ID 和 Model ID 正确
3. 授权模型已正确上传

### Q: 无法创建文档

**A:** 检查：
1. 是否已登录（session 中有 user_id）
2. OpenFGA 连接是否正常
3. 查看应用日志中的错误信息

## 下一步

- 查看 [README.md](README.md) 了解完整文档
- 查看 [第13章](../../chapters/第13章-系统集成实践.md) 了解集成最佳实践
- 修改代码以适应你的业务需求

## 获取帮助

如果遇到问题：
1. 查看应用日志
2. 检查 OpenFGA 日志：`docker logs openfga`
3. 参考 [OpenFGA 文档](https://openfga.dev/docs)
4. 提交 Issue

祝你使用愉快！
