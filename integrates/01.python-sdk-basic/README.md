# OpenFGA Python SDK 基础集成示例

这是一个完整的 OpenFGA Python SDK 集成示例，展示了如何在 Python 应用中使用 OpenFGA 进行细粒度的授权管理。

## 功能特性

本示例包含以下功能：

### 核心功能
- ✅ 客户端初始化（支持 API Token 和 Client Credentials 两种认证方式）
- ✅ 写入关系元组（创建用户与资源的关系）
- ✅ 删除关系元组（移除已有关系）
- ✅ 事务模式（同时写入和删除）
- ✅ 权限检查（验证用户是否有权限访问资源）
- ✅ 批量权限检查（一次检查多个权限，提高性能）
- ✅ 列出对象（查询用户可访问的所有对象）
- ✅ 列出用户（查询有权限访问对象的所有用户）

### 高级功能
- ✅ 上下文元组（临时授权，不持久化到数据库）
- ✅ 条件关系（基于上下文数据的动态权限）
- ✅ 完整的错误处理
- ✅ 异步编程支持
- ✅ 类型提示

## 文件结构

```
01.python-sdk-basic/
├── client.py           # OpenFGA 客户端封装
├── examples.py         # 完整的使用示例
├── requirements.txt    # Python 依赖
├── .env.example        # 环境变量示例
└── README.md          # 本文件
```

## 安装步骤

### 1. 安装依赖

使用 uv（推荐）:
```bash
cd /Users/zhangsan/books/openfga/integrates/01.python-sdk-basic
uv venv
source .venv/bin/activate  # Mac/Linux
uv pip install -r requirements.txt
```

或使用 pip:
```bash
cd /Users/zhangsan/books/openfga/integrates/01.python-sdk-basic
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

### 2. 配置环境变量

复制环境变量示例文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的配置：

#### 方式 1: 使用 API Token（推荐用于开发环境）
```bash
FGA_API_URL=http://localhost:8080
FGA_STORE_ID=your_store_id_here
FGA_MODEL_ID=your_model_id_here
FGA_API_TOKEN=your_api_token_here
FGA_AUTH_METHOD=api_token
```

#### 方式 2: 使用 Client Credentials（推荐用于生产环境）
```bash
FGA_API_URL=https://api.fga.example
FGA_STORE_ID=your_store_id_here
FGA_MODEL_ID=your_model_id_here
FGA_API_TOKEN_ISSUER=https://your-auth-server.com
FGA_API_AUDIENCE=https://api.fga.example
FGA_CLIENT_ID=your_client_id
FGA_CLIENT_SECRET=your_client_secret
FGA_AUTH_METHOD=client_credentials
```

### 3. 启动 OpenFGA 服务器（如果使用本地开发）

使用 Docker:
```bash
docker run -p 8080:8080 openfga/openfga run
```

或使用 Docker Compose:
```bash
docker-compose up -d
```

## 使用说明

### 快速开始

运行所有示例：
```bash
python examples.py
```

### 基础用法

#### 1. 初始化客户端

```python
from client import create_client

# 使用环境变量配置
async with create_client() as client:
    # 执行操作
    pass

# 或者手动指定配置
async with create_client(
    api_url="http://localhost:8080",
    store_id="your_store_id",
    model_id="your_model_id",
    auth_method="api_token",
    api_token="your_token"
) as client:
    # 执行操作
    pass
```

#### 2. 写入关系元组

```python
from openfga_sdk.client.models import ClientTuple

async with create_client() as client:
    writes = [
        ClientTuple(
            user="user:anne",
            relation="viewer",
            object="document:budget"
        ),
    ]

    result = await client.write_tuples(writes=writes)
    if result['success']:
        print("写入成功")
```

#### 3. 检查权限

```python
async with create_client() as client:
    result = await client.check_permission(
        user="user:anne",
        relation="viewer",
        object="document:budget"
    )

    if result['success']:
        if result['allowed']:
            print("用户有权限")
        else:
            print("用户无权限")
```

#### 4. 批量检查权限

```python
from openfga_sdk.client.models import ClientCheckRequest

async with create_client() as client:
    checks = [
        ClientCheckRequest(
            user="user:anne",
            relation="viewer",
            object="document:budget"
        ),
        ClientCheckRequest(
            user="user:bob",
            relation="editor",
            object="document:budget"
        ),
    ]

    result = await client.batch_check(checks)
    if result['success']:
        for item in result['results']:
            print(f"{item['user']} -> {item['relation']} -> {item['object']}: {item['allowed']}")
```

#### 5. 列出对象

```python
async with create_client() as client:
    result = await client.list_objects(
        user="user:anne",
        relation="viewer",
        type="document"
    )

    if result['success']:
        print(f"用户可访问的文档: {result['objects']}")
```

#### 6. 列出用户

```python
async with create_client() as client:
    result = await client.list_users(
        object="document:budget",
        relation="viewer",
        user_filters=[{"type": "user"}]
    )

    if result['success']:
        print(f"可访问该文档的用户: {result['users']}")
```

### 高级用法

#### 1. 使用上下文元组（临时授权）

```python
from openfga_sdk.client.models import ClientTuple

async with create_client() as client:
    # 临时授予权限进行检查，不写入数据库
    contextual_tuples = [
        ClientTuple(
            user="user:temp",
            relation="editor",
            object="document:budget"
        ),
    ]

    result = await client.check_permission(
        user="user:temp",
        relation="editor",
        object="document:budget",
        contextual_tuples=contextual_tuples
    )
```

#### 2. 使用条件关系

```python
from openfga_sdk.client.models import ClientTuple
from openfga_sdk.models import RelationshipCondition

async with create_client() as client:
    # 写入带条件的关系
    writes = [
        ClientTuple(
            user="user:anne",
            relation="viewer",
            object="document:budget",
            condition=RelationshipCondition(
                name='ViewCountLessThan200',
                context={
                    'Name': 'Budget',
                    'Type': 'Document',
                }
            )
        ),
    ]

    await client.write_tuples(writes=writes)

    # 检查时传递上下文数据
    result = await client.check_permission(
        user="user:anne",
        relation="viewer",
        object="document:budget",
        context={'ViewCount': 150}  # 满足条件
    )
```

#### 3. 事务模式（同时写入和删除）

```python
async with create_client() as client:
    writes = [
        ClientTuple(
            user="user:anne",
            relation="editor",
            object="document:budget"
        ),
    ]

    deletes = [
        ClientTuple(
            user="user:anne",
            relation="viewer",
            object="document:budget"
        ),
    ]

    # 在一个事务中执行，要么全部成功，要么全部失败
    result = await client.write_tuples(writes=writes, deletes=deletes)
```

#### 4. 错误处理

```python
async with create_client() as client:
    result = await client.check_permission(
        user="user:anne",
        relation="viewer",
        object="document:budget"
    )

    if result['success']:
        print(f"检查成功: {result['allowed']}")
    else:
        print(f"检查失败: {result['error']}")
        print(f"HTTP 状态码: {result.get('status')}")
        print(f"响应体: {result.get('body')}")
```

## 示例说明

`examples.py` 文件包含 14 个完整的示例：

1. **示例 1**: 写入关系元组
2. **示例 2**: 写入带条件的关系元组
3. **示例 3**: 删除关系元组
4. **示例 4**: 事务模式 - 同时写入和删除
5. **示例 5**: 检查权限
6. **示例 6**: 使用上下文元组检查权限
7. **示例 7**: 使用上下文数据检查权限
8. **示例 8**: 批量检查权限
9. **示例 9**: 批量检查权限（带上下文元组）
10. **示例 10**: 列出用户可访问的对象
11. **示例 11**: 列出对象（带上下文元组）
12. **示例 12**: 列出有权限访问对象的用户
13. **示例 13**: 读取授权模型
14. **示例 14**: 错误处理

运行特定示例：
```python
import asyncio
from examples import example_5_check_permission

asyncio.run(example_5_check_permission())
```

## API 参考

### OpenFGAClientWrapper

主要方法：

- `write_tuples(writes, deletes, model_id)` - 写入或删除关系元组
- `check_permission(user, relation, object, contextual_tuples, context, model_id)` - 检查权限
- `batch_check(checks, model_id)` - 批量检查权限
- `list_objects(user, relation, type, contextual_tuples, context, model_id)` - 列出对象
- `list_users(object, relation, user_filters, contextual_tuples, context, model_id)` - 列出用户
- `read_authorization_models()` - 读取授权模型

所有方法都返回一个字典，包含：
- `success`: 布尔值，表示操作是否成功
- 成功时的数据字段（如 `allowed`, `objects`, `users` 等）
- 失败时的错误信息（`error`, `status`, `body`）

## 常见问题

### 1. 如何获取 Store ID 和 Model ID？

如果你使用的是本地 OpenFGA 服务器，可以通过 API 创建：

```bash
# 创建 Store
curl -X POST http://localhost:8080/stores \
  -H "Content-Type: application/json" \
  -d '{"name": "my-store"}'

# 创建授权模型
curl -X POST http://localhost:8080/stores/{store_id}/authorization-models \
  -H "Content-Type: application/json" \
  -d @model.json
```

### 2. 认证方式如何选择？

- **API Token**: 适用于开发环境和简单场景，配置简单
- **Client Credentials**: 适用于生产环境，更安全，支持 OAuth2 标准

### 3. 如何处理连接错误？

确保：
1. OpenFGA 服务器正在运行
2. API URL 配置正确
3. 网络连接正常
4. 认证信息正确

```python
async with create_client() as client:
    result = await client.check_permission(...)
    if not result['success']:
        if 'status' in result:
            if result['status'] == 401:
                print("认证失败，请检查 Token")
            elif result['status'] == 404:
                print("Store 或 Model 不存在")
            else:
                print(f"HTTP 错误: {result['status']}")
```

### 4. 如何提高性能？

1. **使用批量检查**: 一次检查多个权限，减少网络往返
2. **指定 Model ID**: 避免每次查询最新模型
3. **使用连接池**: SDK 内部已实现
4. **缓存结果**: 对于不常变化的权限，可以在应用层缓存

### 5. 上下文元组和普通元组的区别？

- **普通元组**: 持久化到数据库，永久有效
- **上下文元组**: 仅在当前请求中有效，不写入数据库，适用于：
  - 测试场景
  - 临时授权
  - "假设"场景（如果用户有某权限会怎样）

### 6. 如何调试？

启用详细日志：

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

查看完整的请求和响应：

```python
result = await client.check_permission(...)
print(f"完整响应: {result}")
```

## 最佳实践

1. **使用异步上下文管理器**: 确保客户端正确关闭
   ```python
   async with create_client() as client:
       # 操作
   ```

2. **错误处理**: 始终检查 `result['success']`
   ```python
   result = await client.check_permission(...)
   if not result['success']:
       # 处理错误
   ```

3. **批量操作**: 尽可能使用批量 API
   ```python
   # 好的做法
   await client.batch_check(checks)

   # 避免
   for check in checks:
       await client.check_permission(...)
   ```

4. **指定 Model ID**: 提高性能和一致性
   ```python
   await client.check_permission(..., model_id="specific_model_id")
   ```

5. **使用类型提示**: 提高代码可读性和 IDE 支持
   ```python
   from typing import List
   from openfga_sdk.client.models import ClientTuple

   writes: List[ClientTuple] = [...]
   ```

## 相关资源

- [OpenFGA 官方文档](https://openfga.dev/)
- [Python SDK GitHub](https://github.com/openfga/python-sdk)
- [OpenFGA Playground](https://play.fga.dev/)
- [授权模型示例](https://openfga.dev/docs/modeling)

## 许可证

本示例代码遵循 MIT 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request！
