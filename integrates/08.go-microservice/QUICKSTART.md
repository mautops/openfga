# 快速启动指南

本指南将帮助您在 5 分钟内启动并测试 OpenFGA Go 微服务。

## 前置要求

- Docker 和 Docker Compose
- Go 1.22+ （用于生成 JWT Token）
- curl（用于测试 API）

## 步骤 1: 启动 OpenFGA 服务

```bash
# 启动 OpenFGA
docker run -d \
  --name openfga \
  -p 8080:8080 \
  -p 8081:8081 \
  -p 3000:3000 \
  openfga/openfga run

# 等待服务启动（约 5 秒）
sleep 5

# 验证服务状态
curl http://localhost:8080/healthz
```

## 步骤 2: 创建 Store 和授权模型

### 方法 1: 使用 OpenFGA CLI（推荐）

```bash
# 安装 CLI（macOS）
brew install openfga/tap/fga

# 创建 Store
fga store create --name "document-service"

# 记录返回的 Store ID
# 输出示例: Created store 'document-service' with id: 01HQXYZ...

# 写入授权模型
fga model write --store-id <your-store-id> --file authorization_model.fga

# 记录返回的 Model ID
# 输出示例: Authorization model ID: 01HQXYZ...
```

### 方法 2: 使用 API

```bash
# 创建 Store
STORE_RESPONSE=$(curl -X POST http://localhost:8080/stores \
  -H "Content-Type: application/json" \
  -d '{"name": "document-service"}')

echo $STORE_RESPONSE

# 提取 Store ID
STORE_ID=$(echo $STORE_RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
echo "Store ID: $STORE_ID"

# 写入授权模型（需要先转换 .fga 文件为 JSON 格式）
# 这里简化处理，建议使用 CLI
```

## 步骤 3: 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入实际的值
# 使用你喜欢的编辑器，例如：
nano .env

# 或者直接使用命令行设置
cat > .env << EOF
SERVER_PORT=8080
GIN_MODE=debug
FGA_API_URL=http://localhost:8080
FGA_STORE_ID=<your-store-id>
FGA_MODEL_ID=<your-model-id>
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
EOF
```

## 步骤 4: 启动 Go 服务

```bash
# 下载依赖
go mod download

# 运行服务
go run main.go

# 或者使用 make
make run
```

服务将在 `http://localhost:8080` 启动。

## 步骤 5: 生成测试 Token

在新的终端窗口中：

```bash
# 生成 Alice 的 Token
cd tools
go run generate_token.go \
  -user "user:alice" \
  -email "alice@example.com" \
  -org "org:acme" \
  -secret "your-super-secret-jwt-key-change-this-in-production"

# 复制输出的 Token
export ALICE_TOKEN="<复制的token>"

# 生成 Bob 的 Token
go run generate_token.go \
  -user "user:bob" \
  -email "bob@example.com" \
  -org "org:other" \
  -secret "your-super-secret-jwt-key-change-this-in-production"

export BOB_TOKEN="<复制的token>"

cd ..
```

## 步骤 6: 测试 API

### 测试 1: 健康检查

```bash
curl http://localhost:8080/health
```

### 测试 2: 创建文档（Alice）

```bash
curl -X POST http://localhost:8080/api/documents \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "项目计划书",
    "content": "这是项目计划的详细内容",
    "organization_id": "org:acme"
  }'

# 记录返回的文档 ID
export DOC_ID="<返回的文档ID>"
```

### 测试 3: 查看文档（Alice - 应该成功）

```bash
curl -X GET http://localhost:8080/api/documents/$DOC_ID \
  -H "Authorization: Bearer $ALICE_TOKEN"
```

### 测试 4: 查看文档（Bob - 应该失败）

```bash
curl -X GET http://localhost:8080/api/documents/$DOC_ID \
  -H "Authorization: Bearer $BOB_TOKEN"

# 应该返回 403 Forbidden
```

### 测试 5: 编辑文档（Alice - 应该成功）

```bash
curl -X PUT http://localhost:8080/api/documents/$DOC_ID \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "更新后的项目计划书",
    "content": "这是更新后的内容"
  }'
```

### 测试 6: 删除文档（Alice - 应该成功）

```bash
curl -X DELETE http://localhost:8080/api/documents/$DOC_ID \
  -H "Authorization: Bearer $ALICE_TOKEN"

# 应该返回 204 No Content
```

## 步骤 7: 运行自动化测试脚本

```bash
# 运行完整的测试套件
./test_api.sh
```

## 使用 Docker Compose 一键启动

如果您已经创建了 Store 和 Model，可以使用 Docker Compose 一键启动：

```bash
# 设置环境变量
export FGA_STORE_ID=<your-store-id>
export FGA_MODEL_ID=<your-model-id>
export JWT_SECRET=your-super-secret-jwt-key-change-this-in-production

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f app

# 停止服务
docker-compose down
```

## 权限测试场景

### 场景 1: 分享文档给其他用户

```bash
# Alice 创建文档后，使用 OpenFGA CLI 分享给 Bob

# 给 Bob viewer 权限
fga tuple write \
  --store-id $STORE_ID \
  user:bob viewer document:$DOC_ID

# 现在 Bob 可以查看文档
curl -X GET http://localhost:8080/api/documents/$DOC_ID \
  -H "Authorization: Bearer $BOB_TOKEN"
```

### 场景 2: 组织成员自动获得权限

```bash
# 将 Bob 添加为组织成员
fga tuple write \
  --store-id $STORE_ID \
  user:bob member organization:acme

# 现在 Bob 可以查看该组织的所有文档
curl -X GET http://localhost:8080/api/documents \
  -H "Authorization: Bearer $BOB_TOKEN"
```

### 场景 3: 升级权限

```bash
# 给 Bob editor 权限
fga tuple write \
  --store-id $STORE_ID \
  user:bob editor document:$DOC_ID

# 现在 Bob 可以编辑文档
curl -X PUT http://localhost:8080/api/documents/$DOC_ID \
  -H "Authorization: Bearer $BOB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Bob 编辑的标题",
    "content": "Bob 编辑的内容"
  }'
```

## 故障排查

### 问题 1: OpenFGA 连接失败

```bash
# 检查 OpenFGA 是否运行
docker ps | grep openfga

# 检查端口是否被占用
lsof -i :8080

# 查看 OpenFGA 日志
docker logs openfga
```

### 问题 2: 权限检查失败

```bash
# 验证 Store ID 和 Model ID
echo "Store ID: $FGA_STORE_ID"
echo "Model ID: $FGA_MODEL_ID"

# 查看所有关系元组
fga tuple read --store-id $STORE_ID

# 测试权限检查
fga query check \
  --store-id $STORE_ID \
  user:alice can_view document:$DOC_ID
```

### 问题 3: JWT 验证失败

```bash
# 验证 JWT Secret 是否一致
echo $JWT_SECRET

# 重新生成 Token
cd tools
go run generate_token.go -user "user:alice" -email "alice@example.com" -org "org:acme"
```

## 下一步

- 阅读完整的 [README.md](README.md) 了解更多功能
- 查看 [授权模型](authorization_model.fga) 了解权限设计
- 探索 OpenFGA Playground: http://localhost:3000
- 自定义授权模型以适应您的业务需求

## 清理环境

```bash
# 停止 Go 服务（Ctrl+C）

# 停止并删除 OpenFGA 容器
docker stop openfga
docker rm openfga

# 或使用 Docker Compose
docker-compose down -v
```

## 常用命令

```bash
# 查看所有文档
curl -X GET http://localhost:8080/api/documents \
  -H "Authorization: Bearer $ALICE_TOKEN"

# 查看服务日志
tail -f logs/app.log

# 重新编译
make build

# 运行测试
make test

# 格式化代码
make fmt
```

## 获取帮助

如果遇到问题，请：

1. 查看服务日志
2. 检查 OpenFGA 日志
3. 验证环境变量配置
4. 参考 [README.md](README.md) 中的故障排查部分
