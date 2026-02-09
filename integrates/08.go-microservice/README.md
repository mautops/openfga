# Go + OpenFGA 微服务集成示例

这是一个完整的 Go 微服务项目，展示了如何集成 OpenFGA 实现细粒度的权限控制。项目使用 Gin 框架构建 RESTful API，并通过 OpenFGA 管理文档的访问权限。

## 项目特性

- **RESTful API**: 使用 Gin 框架构建高性能 HTTP 服务
- **JWT 认证**: 基于 JWT 的用户身份认证
- **细粒度权限控制**: 通过 OpenFGA 实现基于关系的授权（ReBAC）
- **中间件模式**: 可复用的认证和权限检查中间件
- **优雅关闭**: 支持服务的优雅关闭和资源清理
- **健康检查**: 提供健康检查端点
- **Docker 支持**: 包含 Dockerfile 和 docker-compose 配置
- **结构化日志**: 使用 zap 实现高性能结构化日志

## 项目结构

```
08.go-microservice/
├── main.go                          # 主程序入口
├── go.mod                           # Go 模块定义
├── go.sum                           # 依赖版本锁定
├── Dockerfile                       # Docker 镜像构建文件
├── Makefile                         # 构建脚本
├── .env.example                     # 环境变量示例
├── authorization_model.fga          # OpenFGA 授权模型
├── README.md                        # 项目文档
├── internal/                        # 内部包
│   ├── openfga/
│   │   └── client.go               # OpenFGA 客户端封装
│   ├── middleware/
│   │   ├── auth.go                 # JWT 认证中间件
│   │   └── permissions.go          # 权限检查中间件
│   ├── handlers/
│   │   └── documents.go            # 文档处理器
│   └── models/
│       └── document.go             # 数据模型
└── pkg/                            # 公共包
    └── config/
        └── config.go               # 配置管理
```

## 授权模型

项目使用以下 OpenFGA 授权模型：

```
type user

type organization
  relations
    define member: [user]
    define admin: [user]

type document
  relations
    define organization: [organization]
    define owner: [user]
    define editor: [user] or owner
    define viewer: [user] or editor or member from organization
    define can_view: viewer
    define can_edit: editor
    define can_delete: owner
```

### 权限说明

- **owner**: 文档所有者，拥有所有权限
- **editor**: 编辑者，可以查看和编辑文档
- **viewer**: 查看者，只能查看文档
- **organization member**: 组织成员自动获得文档的查看权限

## 快速开始

### 前置要求

- Go 1.22 或更高版本
- OpenFGA 服务（本地或远程）
- Docker（可选）

### 1. 启动 OpenFGA 服务

使用 Docker 启动 OpenFGA：

```bash
docker run -d \
  --name openfga \
  -p 8080:8080 \
  -p 8081:8081 \
  -p 3000:3000 \
  openfga/openfga run
```

### 2. 创建 Store 和 Model

使用 OpenFGA CLI 或 API 创建 Store 和授权模型：

```bash
# 安装 OpenFGA CLI
brew install openfga/tap/fga

# 创建 Store
fga store create --name "document-service"

# 写入授权模型
fga model write --store-id <store-id> --file authorization_model.fga
```

### 3. 配置环境变量

复制 `.env.example` 到 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 服务配置
SERVER_PORT=8080
GIN_MODE=debug

# OpenFGA 配置
FGA_API_URL=http://localhost:8080
FGA_STORE_ID=your_store_id_here
FGA_MODEL_ID=your_model_id_here

# JWT 配置
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
```

### 4. 安装依赖

```bash
go mod download
```

### 5. 运行服务

```bash
# 使用 go run
go run main.go

# 或使用 make
make run

# 或编译后运行
make build
./bin/main
```

服务将在 `http://localhost:8080` 启动。

## API 端点

### 健康检查

```bash
GET /health
```

### 文档管理

所有文档 API 都需要 JWT 认证，在请求头中添加：

```
Authorization: Bearer <your-jwt-token>
```

#### 1. 创建文档

```bash
POST /api/documents
Content-Type: application/json

{
  "title": "项目计划书",
  "content": "这是项目计划的详细内容...",
  "organization_id": "org123"
}
```

**权限要求**: 已认证用户

**响应**:
```json
{
  "id": "doc-uuid",
  "title": "项目计划书",
  "content": "这是项目计划的详细内容...",
  "organization_id": "org123",
  "owner_id": "user123",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### 2. 查看文档

```bash
GET /api/documents/:id
```

**权限要求**: `can_view` (viewer 或更高权限)

#### 3. 编辑文档

```bash
PUT /api/documents/:id
Content-Type: application/json

{
  "title": "更新后的标题",
  "content": "更新后的内容"
}
```

**权限要求**: `can_edit` (editor 或 owner)

#### 4. 删除文档

```bash
DELETE /api/documents/:id
```

**权限要求**: `can_delete` (仅 owner)

#### 5. 列出可访问的文档

```bash
GET /api/documents
```

**权限要求**: 已认证用户（返回用户有权限访问的所有文档）

## JWT Token 生成

为了测试 API，您需要生成 JWT Token。以下是一个示例 Go 程序：

```go
package main

import (
	"fmt"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

type Claims struct {
	UserID         string `json:"user_id"`
	Email          string `json:"email"`
	OrganizationID string `json:"organization_id"`
	jwt.RegisteredClaims
}

func main() {
	// 创建 Claims
	claims := &Claims{
		UserID:         "user:alice",
		Email:          "alice@example.com",
		OrganizationID: "org:acme",
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(24 * time.Hour)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			Issuer:    "openfga-microservice",
		},
	}

	// 创建 Token
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)

	// 签名（使用与 .env 中相同的密钥）
	tokenString, err := token.SignedString([]byte("your-super-secret-jwt-key-change-this-in-production"))
	if err != nil {
		panic(err)
	}

	fmt.Println("JWT Token:")
	fmt.Println(tokenString)
}
```

## 使用示例

### 1. 创建文档并设置权限

```bash
# 1. 生成 JWT Token（使用上面的程序）
export TOKEN="your-jwt-token"

# 2. 创建文档
curl -X POST http://localhost:8080/api/documents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Q1 财务报告",
    "content": "2024年第一季度财务数据...",
    "organization_id": "org:acme"
  }'

# 响应会返回文档 ID，例如: doc-123
```

### 2. 查看文档

```bash
curl -X GET http://localhost:8080/api/documents/doc-123 \
  -H "Authorization: Bearer $TOKEN"
```

### 3. 分享文档给其他用户

```bash
# 使用 OpenFGA CLI 或 API 添加权限
fga tuple write \
  --store-id <store-id> \
  user:bob viewer document:doc-123
```

### 4. 编辑文档

```bash
curl -X PUT http://localhost:8080/api/documents/doc-123 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Q1 财务报告（已审核）",
    "content": "更新后的内容..."
  }'
```

### 5. 删除文档

```bash
curl -X DELETE http://localhost:8080/api/documents/doc-123 \
  -H "Authorization: Bearer $TOKEN"
```

## Docker 部署

### 构建镜像

```bash
make docker-build
```

### 运行容器

```bash
docker run -d \
  -p 8080:8080 \
  --env-file .env \
  --name openfga-go-service \
  openfga-go-microservice:latest
```

### 使用 Docker Compose

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  openfga:
    image: openfga/openfga:latest
    ports:
      - "8080:8080"
      - "8081:8081"
      - "3000:3000"
    command: run

  app:
    build: .
    ports:
      - "8090:8080"
    environment:
      - FGA_API_URL=http://openfga:8080
      - FGA_STORE_ID=${FGA_STORE_ID}
      - FGA_MODEL_ID=${FGA_MODEL_ID}
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - openfga
```

启动服务：

```bash
docker-compose up -d
```

## 开发指南

### 代码结构说明

#### 1. OpenFGA 客户端封装 (`internal/openfga/client.go`)

提供了对 OpenFGA SDK 的封装，包括：

- `Check()`: 检查单个权限
- `BatchCheck()`: 批量检查权限
- `WriteTuples()`: 批量写入关系元组
- `DeleteTuples()`: 批量删除关系元组
- `ListObjects()`: 列出用户有权限的对象
- `HealthCheck()`: 健康检查

#### 2. 认证中间件 (`internal/middleware/auth.go`)

- 验证 JWT Token
- 提取用户信息并存储到上下文
- 提供辅助函数获取用户信息

#### 3. 权限中间件 (`internal/middleware/permissions.go`)

- `PermissionMiddleware()`: 通用权限检查中间件
- `RequirePermission()`: 特定权限检查中间件工厂

#### 4. 文档处理器 (`internal/handlers/documents.go`)

实现了文档的 CRUD 操作，每个操作都会：

1. 验证请求参数
2. 执行业务逻辑
3. 更新 OpenFGA 权限关系
4. 返回响应

### 添加新的资源类型

1. 在 `authorization_model.fga` 中定义新类型
2. 创建对应的 model 结构
3. 创建 handler 处理业务逻辑
4. 在 `main.go` 中注册路由

### 自定义权限检查

```go
// 在 handler 中自定义权限检查
func (h *Handler) CustomAction(c *gin.Context) {
    userID, _ := c.Get("user_id")
    resourceID := c.Param("id")

    // 检查自定义权限
    allowed, err := h.fgaClient.Check(
        c.Request.Context(),
        "user:"+userID.(string),
        "custom_permission",
        "resource:"+resourceID,
    )

    if err != nil || !allowed {
        c.JSON(http.StatusForbidden, gin.H{"error": "无权限"})
        return
    }

    // 执行操作...
}
```

## 性能优化

### 1. 权限检查缓存

可以使用 Redis 缓存权限检查结果：

```go
// 伪代码
func (c *Client) CheckWithCache(ctx context.Context, user, relation, object string) (bool, error) {
    // 1. 检查缓存
    cacheKey := fmt.Sprintf("perm:%s:%s:%s", user, relation, object)
    if cached, err := redis.Get(cacheKey); err == nil {
        return cached == "true", nil
    }

    // 2. 调用 OpenFGA
    allowed, err := c.Check(ctx, user, relation, object)
    if err != nil {
        return false, err
    }

    // 3. 写入缓存（短期缓存，如 5 分钟）
    redis.Set(cacheKey, allowed, 5*time.Minute)

    return allowed, nil
}
```

### 2. 批量权限检查

对于列表操作，使用批量检查：

```go
// 批量检查多个文档的权限
checks := make([]openfga.CheckRequest, len(documents))
for i, doc := range documents {
    checks[i] = openfga.CheckRequest{
        User:     "user:" + userID,
        Relation: "can_view",
        Object:   "document:" + doc.ID,
    }
}

results, err := fgaClient.BatchCheck(ctx, checks)
```

### 3. 连接池配置

OpenFGA Go SDK 内部使用 HTTP 客户端，可以配置连接池：

```go
// 在创建客户端时配置
httpClient := &http.Client{
    Transport: &http.Transport{
        MaxIdleConns:        100,
        MaxIdleConnsPerHost: 10,
        IdleConnTimeout:     90 * time.Second,
    },
    Timeout: 10 * time.Second,
}
```

## 测试

### 单元测试

```bash
go test ./...
```

### 集成测试

```bash
# 启动测试环境
docker-compose -f docker-compose.test.yml up -d

# 运行集成测试
go test -tags=integration ./...

# 清理测试环境
docker-compose -f docker-compose.test.yml down
```

## 故障排查

### 1. OpenFGA 连接失败

检查：
- OpenFGA 服务是否运行
- `FGA_API_URL` 配置是否正确
- 网络连接是否正常

```bash
# 测试 OpenFGA 连接
curl http://localhost:8080/healthz
```

### 2. 权限检查失败

检查：
- Store ID 和 Model ID 是否正确
- 授权模型是否正确写入
- 关系元组是否正确创建

```bash
# 查看关系元组
fga tuple read --store-id <store-id>
```

### 3. JWT 验证失败

检查：
- JWT_SECRET 配置是否正确
- Token 是否过期
- Token 格式是否正确

## 最佳实践

1. **环境变量管理**: 生产环境使用密钥管理服务（如 AWS Secrets Manager）
2. **日志记录**: 记录所有权限检查和拒绝事件
3. **错误处理**: 提供清晰的错误信息，但不泄露敏感信息
4. **监控**: 监控权限检查延迟和失败率
5. **审计**: 记录所有权限变更操作
6. **测试**: 为每个权限场景编写测试用例

## 常见问题

### Q: 如何处理权限继承？

A: 在授权模型中使用 `from` 关键字定义继承关系：

```
define viewer: [user] or editor or member from organization
```

### Q: 如何实现临时权限？

A: 使用 OpenFGA 的条件（Conditions）功能，在元组中添加时间条件。

### Q: 如何批量授权？

A: 使用 `WriteTuples()` 方法批量写入关系元组。

### Q: 权限检查的性能如何？

A: OpenFGA 的权限检查通常在 10-50ms 内完成。对于高并发场景，建议使用缓存。

## 相关资源

- [OpenFGA 官方文档](https://openfga.dev/docs)
- [OpenFGA Go SDK](https://github.com/openfga/go-sdk)
- [Gin 框架文档](https://gin-gonic.com/docs/)
- [JWT 规范](https://jwt.io/)

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
