# Express + OpenFGA 快速开始指南

本指南将帮助您在 5 分钟内运行 Express + OpenFGA 集成示例。

## 前置要求

- Node.js 18+
- Docker（用于运行 OpenFGA）
- curl 和 jq（用于测试）

## 步骤 1: 启动 OpenFGA

```bash
# 启动 OpenFGA 服务
docker run -d \
  --name openfga \
  -p 8080:8080 \
  openfga/openfga run

# 验证服务运行
curl http://localhost:8080/healthz
```

## 步骤 2: 创建 Store 和授权模型

```bash
# 创建 Store
STORE_RESPONSE=$(curl -s -X POST http://localhost:8080/stores \
  -H "Content-Type: application/json" \
  -d '{"name": "express-demo"}')

STORE_ID=$(echo $STORE_RESPONSE | jq -r '.id')
echo "Store ID: $STORE_ID"

# 创建授权模型
MODEL_RESPONSE=$(curl -s -X POST http://localhost:8080/stores/$STORE_ID/authorization-models \
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
        },
        "metadata": {
          "relations": {
            "owner": {"directly_related_user_types": [{"type": "user"}]},
            "editor": {"directly_related_user_types": [{"type": "user"}]},
            "viewer": {"directly_related_user_types": [{"type": "user"}]}
          }
        }
      }
    ]
  }')

MODEL_ID=$(echo $MODEL_RESPONSE | jq -r '.authorization_model_id')
echo "Model ID: $MODEL_ID"
```

## 步骤 3: 配置环境变量

```bash
# 创建 .env 文件
cat > .env << EOF
PORT=3000
NODE_ENV=development

JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_EXPIRES_IN=24h

FGA_API_URL=http://localhost:8080
FGA_STORE_ID=$STORE_ID
FGA_AUTHORIZATION_MODEL_ID=$MODEL_ID

LOG_LEVEL=info
EOF
```

## 步骤 4: 安装依赖并启动服务

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

服务将在 http://localhost:3000 启动。

## 步骤 5: 测试 API

### 方式 1: 使用测试脚本（推荐）

```bash
./test.sh
```

### 方式 2: 手动测试

```bash
# 1. 登录获取 token
TOKEN=$(curl -s -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"password123"}' \
  | jq -r '.token')

echo "Token: $TOKEN"

# 2. 创建文档
DOC_RESPONSE=$(curl -s -X POST http://localhost:3000/documents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"我的第一个文档","content":"这是文档内容"}')

DOC_ID=$(echo $DOC_RESPONSE | jq -r '.document.id')
echo "Document ID: $DOC_ID"

# 3. 查看文档
curl -X GET http://localhost:3000/documents/$DOC_ID \
  -H "Authorization: Bearer $TOKEN" | jq

# 4. 更新文档
curl -X PUT http://localhost:3000/documents/$DOC_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"更新后的标题","content":"更新后的内容"}' | jq

# 5. 分享文档给 Bob
curl -X POST http://localhost:3000/documents/$DOC_ID/share \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"userId":"user:bob","relation":"viewer"}' | jq

# 6. Bob 登录并查看文档
BOB_TOKEN=$(curl -s -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@example.com","password":"password123"}' \
  | jq -r '.token')

curl -X GET http://localhost:3000/documents/$DOC_ID \
  -H "Authorization: Bearer $BOB_TOKEN" | jq
```

## 测试用户

系统预置了以下测试用户：

| 邮箱 | 密码 | 用户 ID |
|------|------|---------|
| alice@example.com | password123 | user:alice |
| bob@example.com | password123 | user:bob |
| charlie@example.com | password123 | user:charlie |

## 权限测试场景

### 场景 1: 文档所有者的完整权限

```bash
# Alice 创建文档后自动成为 owner
# owner 可以：查看、编辑、删除、分享
```

### 场景 2: 查看者权限

```bash
# Alice 分享文档给 Bob（viewer 权限）
# Bob 可以：查看
# Bob 不能：编辑、删除
```

### 场景 3: 编辑者权限

```bash
# Alice 分享文档给 Bob（editor 权限）
curl -X POST http://localhost:3000/documents/$DOC_ID/share \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"userId":"user:bob","relation":"editor"}'

# Bob 可以：查看、编辑
# Bob 不能：删除
```

## 常见问题

### Q: OpenFGA 连接失败

```bash
# 检查 OpenFGA 是否运行
docker ps | grep openfga

# 查看 OpenFGA 日志
docker logs openfga

# 重启 OpenFGA
docker restart openfga
```

### Q: JWT token 无效

确保 `.env` 文件中的 `JWT_SECRET` 已设置。

### Q: 权限检查失败

1. 确认 Store ID 和 Model ID 正确
2. 检查关系元组是否已写入
3. 查看 Express 服务日志

```bash
# 查看所有关系元组
curl -X POST http://localhost:8080/stores/$STORE_ID/read \
  -H "Content-Type: application/json" \
  -d '{}' | jq
```

## 下一步

- 阅读完整的 [README.md](./README.md)
- 查看源代码了解实现细节
- 自定义授权模型
- 集成到您的应用中

## 清理

```bash
# 停止 Express 服务
# Ctrl+C

# 停止并删除 OpenFGA 容器
docker stop openfga
docker rm openfga
```
