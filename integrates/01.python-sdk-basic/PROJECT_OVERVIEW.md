# OpenFGA Python SDK 基础集成 - 项目概览

## 项目结构

```
01.python-sdk-basic/
├── client.py                      # OpenFGA 客户端封装类
├── examples.py                    # 14 个完整的使用示例
├── quick_test.py                  # 快速测试脚本
├── setup.py                       # 环境设置脚本
├── requirements.txt               # Python 依赖
├── authorization_model.json       # 示例授权模型
├── .env.example                   # 环境变量模板
├── .gitignore                     # Git 忽略文件
├── README.md                      # 详细使用文档
└── PROJECT_OVERVIEW.md           # 本文件
```

## 文件说明

### 核心文件

#### 1. `client.py` (14KB)
OpenFGA 客户端封装类，提供了便捷的 API 接口。

**主要功能:**
- `OpenFGAClientWrapper` 类：封装了所有 OpenFGA 操作
- 支持两种认证方式：API Token 和 Client Credentials
- 异步上下文管理器支持
- 完整的错误处理
- 类型提示

**主要方法:**
- `write_tuples()` - 写入/删除关系元组
- `check_permission()` - 检查权限
- `batch_check()` - 批量检查权限
- `list_objects()` - 列出可访问对象
- `list_users()` - 列出有权限的用户
- `read_authorization_models()` - 读取授权模型

#### 2. `examples.py` (17KB)
包含 14 个完整的使用示例，涵盖所有常见场景。

**示例列表:**
1. 写入关系元组
2. 写入带条件的关系元组
3. 删除关系元组
4. 事务模式（同时写入和删除）
5. 检查权限
6. 使用上下文元组检查权限
7. 使用上下文数据检查权限
8. 批量检查权限
9. 批量检查权限（带上下文元组）
10. 列出用户可访问的对象
11. 列出对象（带上下文元组）
12. 列出有权限访问对象的用户
13. 读取授权模型
14. 错误处理

**运行方式:**
```bash
# 运行所有示例
python examples.py

# 运行单个示例
python -c "import asyncio; from examples import example_5_check_permission; asyncio.run(example_5_check_permission())"
```

### 工具脚本

#### 3. `quick_test.py` (5.2KB)
快速测试脚本，用于验证环境配置是否正确。

**测试内容:**
- 连接测试
- 读取授权模型
- 写入和检查权限
- 自动清理测试数据

**运行方式:**
```bash
python quick_test.py
```

#### 4. `setup.py` (7.8KB)
自动化环境设置脚本，帮助快速初始化 OpenFGA 环境。

**功能:**
- 检查服务器连接
- 创建 Store
- 上传授权模型
- 生成 .env 配置文件

**运行方式:**
```bash
# 使用默认配置
python setup.py

# 自定义配置
python setup.py --api-url http://localhost:8080 --store-name my-app
```

### 配置文件

#### 5. `requirements.txt` (160B)
Python 依赖列表。

**依赖包:**
- `openfga-sdk>=0.7.0` - OpenFGA Python SDK
- `python-dotenv>=1.0.0` - 环境变量管理
- `aiohttp>=3.9.0` - 异步 HTTP 客户端
- `mypy>=1.8.0` - 类型检查（开发依赖）

**安装方式:**
```bash
# 使用 uv（推荐）
uv pip install -r requirements.txt

# 使用 pip
pip install -r requirements.txt
```

#### 6. `.env.example` (532B)
环境变量模板文件。

**配置项:**
- `FGA_API_URL` - OpenFGA API 地址
- `FGA_STORE_ID` - Store ID
- `FGA_MODEL_ID` - Authorization Model ID
- `FGA_API_TOKEN` - API Token（可选）
- `FGA_AUTH_METHOD` - 认证方式

**使用方式:**
```bash
cp .env.example .env
# 编辑 .env 文件，填入实际配置
```

#### 7. `authorization_model.json` (1.3KB)
示例授权模型，定义了文档的权限结构。

**模型结构:**
- `user` 类型：表示用户
- `document` 类型：表示文档
  - `owner` 关系：文档所有者
  - `editor` 关系：文档编辑者
  - `viewer` 关系：文档查看者（包括 editor 和 owner）

**权限继承:**
```
owner → editor → viewer
```

### 文档文件

#### 8. `README.md` (12KB)
详细的使用文档。

**内容包括:**
- 功能特性
- 安装步骤
- 配置说明
- 使用示例
- API 参考
- 常见问题
- 最佳实践
- 相关资源

#### 9. `.gitignore` (428B)
Git 忽略文件配置。

**忽略内容:**
- Python 缓存文件
- 虚拟环境
- 环境变量文件
- IDE 配置
- 日志文件

## 快速开始

### 1. 安装依赖

```bash
cd /Users/zhangsan/books/openfga/integrates/01.python-sdk-basic
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 2. 启动 OpenFGA 服务器

```bash
docker run -p 8080:8080 openfga/openfga run
```

### 3. 设置环境

```bash
# 自动设置（推荐）
python setup.py

# 或手动设置
cp .env.example .env
# 编辑 .env 文件
```

### 4. 运行测试

```bash
python quick_test.py
```

### 5. 运行示例

```bash
python examples.py
```

## 使用场景

### 场景 1: 简单权限检查

```python
from client import create_client

async with create_client() as client:
    result = await client.check_permission(
        user="user:anne",
        relation="viewer",
        object="document:budget"
    )
    print(result['allowed'])
```

### 场景 2: 批量权限检查

```python
from client import create_client
from openfga_sdk.client.models import ClientCheckRequest

async with create_client() as client:
    checks = [
        ClientCheckRequest(user="user:anne", relation="viewer", object="document:budget"),
        ClientCheckRequest(user="user:bob", relation="editor", object="document:budget"),
    ]
    result = await client.batch_check(checks)
    for item in result['results']:
        print(f"{item['user']}: {item['allowed']}")
```

### 场景 3: 列出用户可访问的资源

```python
from client import create_client

async with create_client() as client:
    result = await client.list_objects(
        user="user:anne",
        relation="viewer",
        type="document"
    )
    print(result['objects'])
```

## 技术特点

### 1. 异步编程
- 使用 `async/await` 语法
- 支持高并发场景
- 异步上下文管理器

### 2. 类型安全
- 完整的类型提示
- 支持 MyPy 类型检查
- IDE 智能提示

### 3. 错误处理
- 统一的错误处理机制
- 详细的错误信息
- HTTP 状态码和响应体

### 4. 灵活配置
- 环境变量配置
- 代码配置
- 支持多种认证方式

### 5. 最佳实践
- 遵循 Python PEP 8 规范
- 详细的中文注释
- 完整的文档

## 性能优化建议

### 1. 使用批量操作
```python
# 好的做法
await client.batch_check(checks)

# 避免
for check in checks:
    await client.check_permission(...)
```

### 2. 指定 Model ID
```python
# 提高性能
await client.check_permission(..., model_id="specific_model_id")
```

### 3. 使用上下文元组
```python
# 临时授权，不写入数据库
await client.check_permission(..., contextual_tuples=[...])
```

### 4. 缓存结果
```python
# 对于不常变化的权限，可以在应用层缓存
cache = {}
key = f"{user}:{relation}:{object}"
if key not in cache:
    result = await client.check_permission(...)
    cache[key] = result['allowed']
```

## 常见问题

### Q1: 如何获取 Store ID 和 Model ID？
A: 运行 `python setup.py` 自动创建，或使用 OpenFGA API 手动创建。

### Q2: 本地开发需要认证吗？
A: 默认的 OpenFGA 服务器不需要认证，可以注释掉 `.env` 中的认证配置。

### Q3: 如何调试？
A: 启用日志：`logging.basicConfig(level=logging.DEBUG)`

### Q4: 支持哪些 Python 版本？
A: Python 3.8+

### Q5: 如何在生产环境使用？
A: 使用 Client Credentials 认证，配置 HTTPS，启用日志监控。

## 下一步

1. **学习授权模型设计**: 阅读 [OpenFGA 建模指南](https://openfga.dev/docs/modeling)
2. **集成到应用**: 参考 `03.fastapi-integration` 示例
3. **性能优化**: 使用批量操作和缓存
4. **监控和日志**: 添加日志和指标收集
5. **测试**: 编写单元测试和集成测试

## 相关资源

- [OpenFGA 官方文档](https://openfga.dev/)
- [Python SDK GitHub](https://github.com/openfga/python-sdk)
- [OpenFGA Playground](https://play.fga.dev/)
- [社区讨论](https://github.com/openfga/openfga/discussions)

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
