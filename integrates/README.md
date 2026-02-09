# OpenFGA 集成示例

本目录包含 OpenFGA 与各种技术栈的集成示例代码，涵盖不同编程语言、框架和应用场景。

## 📊 统计信息

- **集成示例总数**: 9 个
- **编程语言**: Python, JavaScript/TypeScript, Go
- **框架覆盖**: FastAPI, Flask, Express.js, React, LangChain, AgentScope
- **应用场景**: Web API, 前端应用, 微服务, AI Agent 系统

## 🗺️ 快速导航

| 编号 | 名称 | 语言 | 框架 | 场景 | 难度 |
|------|------|------|------|------|------|
| 01 | [Python SDK 基础](./01.python-sdk-basic/) | Python | - | 基础学习 | ⭐ |
| 02 | [Node.js SDK 基础](./02.nodejs-sdk-basic/) | TypeScript | - | 基础学习 | ⭐ |
| 03 | [FastAPI 集成](./03.fastapi-integration/) | Python | FastAPI | Web API | ⭐⭐ |
| 04 | [Express.js 集成](./04.express-integration/) | TypeScript | Express | Web API | ⭐⭐ |
| 05 | [Flask OAuth 集成](./05.flask-oauth-integration/) | Python | Flask | OAuth 认证 | ⭐⭐⭐ |
| 06 | [LangChain 集成](./06.langchain-integration/) | Python | LangChain | AI Agent | ⭐⭐⭐ |
| 07 | [React 前端集成](./07.react-frontend/) | TypeScript | React | 前端应用 | ⭐⭐ |
| 08 | [Go 微服务集成](./08.go-microservice/) | Go | Gin | 微服务 | ⭐⭐⭐ |
| 09 | [AgentScope MCP 集成](./09.agentscope-mcp-integration/) | Python | AgentScope | 多智能体 | ⭐⭐⭐⭐ |

## 📁 目录结构

```
integrates/
├── 01.python-sdk-basic/          # Python SDK 基础用法
├── 02.nodejs-sdk-basic/           # Node.js SDK 基础用法
├── 03.fastapi-integration/        # FastAPI 框架集成
├── 04.express-integration/        # Express.js 框架集成
├── 05.flask-oauth-integration/    # Flask + OAuth 集成
├── 06.langchain-integration/      # LangChain AI 框架集成
├── 07.react-frontend/             # React 前端集成
├── 08.go-microservice/            # Go 微服务集成
├── 09.agentscope-mcp-integration/ # AgentScope + MCP 集成
└── test_integrations.py           # 集成测试脚本
```

## 🚀 快速开始

### 环境准备

1. **安装 Python 依赖**（使用 uv）：
   ```bash
   cd /path/to/openfga
   uv pip install openfga-sdk fastapi uvicorn python-jose python-dotenv
   ```

2. **启动 OpenFGA 服务**：
   ```bash
   docker run -p 8080:8080 -p 8081:8081 openfga/openfga run
   ```

3. **配置环境变量**：
   ```bash
   cp integrates/01.python-sdk-basic/.env.example .env
   # 编辑 .env 文件，设置 FGA_STORE_ID 等参数
   ```

### 运行示例

#### 1. Python SDK 基础示例

```bash
cd integrates/01.python-sdk-basic
python examples.py
```

#### 2. FastAPI 集成示例

```bash
cd integrates/03.fastapi-integration
uvicorn main:app --reload
```

访问 http://localhost:8000/docs 查看 API 文档。

#### 4. AgentScope MCP 集成示例

```bash
# 启动 MCP 服务器
cd integrates/09.agentscope-mcp-integration
python mcp_server/openfga_mcp_server.py

# 在另一个终端运行示例
python examples/01_document_permissions.py
```

#### 5. 运行集成测试

```bash
cd integrates
python test_integrations.py
```

## 📚 集成示例说明

### 01. Python SDK 基础用法

**目录**: `01.python-sdk-basic/`

**功能**:
- OpenFGA 客户端初始化
- 写入/删除关系元组
- 权限检查
- 批量检查
- 列出对象和用户

**适用场景**:
- Python 后端应用
- 数据处理脚本
- AI 应用集成

**文件**:
- `client.py` - 客户端封装
- `examples.py` - 使用示例
- `README.md` - 详细文档

### 02. Node.js SDK 基础用法

**目录**: `02.nodejs-sdk-basic/`

**功能**:
- TypeScript 类型支持
- 异步操作
- 错误处理

**适用场景**:
- Node.js 后端
- Serverless 函数
- 微服务

### 03. FastAPI 集成

**目录**: `03.fastapi-integration/`

**功能**:
- JWT 认证中间件
- 权限检查装饰器
- RESTful API 示例
- 文档 CRUD 操作

**适用场景**:
- Python Web API
- 微服务架构
- 现代 Web 应用

**API 端点**:
- `POST /auth/login` - 用户登录
- `GET /documents` - 列出文档
- `POST /documents` - 创建文档
- `GET /documents/{id}` - 查看文档
- `PUT /documents/{id}` - 编辑文档
- `DELETE /documents/{id}` - 删除文档

### 04. Express.js 集成

**目录**: `04.express-integration/`

**功能**:
- Express 中间件
- 路由级权限控制
- Session 管理

**适用场景**:
- Node.js Web 应用
- 传统 MVC 架构

### 05. Flask + OAuth 集成

**目录**: `05.flask-oauth-integration/`

**功能**:
- OAuth 2.0 认证
- OpenFGA 授权
- 认证授权分离

**适用场景**:
- Python Web 应用
- 企业级系统集成

### 06. LangChain 集成

**目录**: `06.langchain-integration/`

**功能**:
- AI Agent 权限控制
- 工具调用授权
- 上下文权限检查

**适用场景**:
- AI 应用
- LangChain 项目
- Agent 系统

### 07. React 前端集成

**目录**: `07.react-frontend/`

**功能**:
- 前端权限检查
- UI 元素控制
- 权限缓存

**适用场景**:
- React 单页应用
- 前后端分离架构

### 08. Go 微服务集成

**目录**: `08.go-microservice/`

**功能**:
- gRPC 集成
- 高性能权限检查
- 中间件实现

**适用场景**:
- Go 微服务
- 云原生应用
- 高并发场景

### 09. AgentScope + MCP 集成

**目录**: `09.agentscope-mcp-integration/`

**功能**:
- MCP (Model Context Protocol) 服务器
- AgentScope 多智能体框架集成
- 权限管理 Agent
- 多智能体协作示例

**适用场景**:
- AI Agent 系统
- 多智能体协作
- LLM 应用权限控制
- 企业级 AI 应用

**核心组件**:
- `mcp_server/` - OpenFGA MCP 服务器（FastMCP）
- `agentscope_client/` - 权限管理 Agent
- `examples/` - 文档权限管理、多智能体协作示例
- `tests/` - 集成测试

**MCP 工具**:
- `check_permission` - 检查用户权限
- `write_tuples` - 写入关系元组
- `delete_tuples` - 删除关系元组
- `list_objects` - 列出有权限的对象
- `batch_check` - 批量检查权限

## 🔧 开发指南

### 添加新的集成示例

1. 创建新目录：
   ```bash
   mkdir integrates/09.your-integration
   ```

2. 添加必要文件：
   - `README.md` - 说明文档
   - 源代码文件
   - `.env.example` - 环境变量示例
   - 测试文件

3. 更新本 README 文件

### 代码规范

- **Python**: 遵循 PEP 8，使用类型提示
- **JavaScript/TypeScript**: 使用 ESLint + Prettier
- **Go**: 使用 gofmt + golint

### 测试要求

每个集成示例应包含：
- 单元测试
- 集成测试
- 使用示例

## 📖 相关文档

### OpenFGA 官方文档
- [OpenFGA 官方文档](https://openfga.dev/docs)
- [Python SDK 文档](https://github.com/openfga/python-sdk)
- [Node.js SDK 文档](https://github.com/openfga/js-sdk)
- [Go SDK 文档](https://github.com/openfga/go-sdk)

### AI 框架文档
- [LangChain 文档](https://python.langchain.com/)
- [AgentScope 文档](https://doc.agentscope.io/)
- [MCP 协议规范](https://modelcontextprotocol.io/)

### Web 框架文档
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Flask 文档](https://flask.palletsprojects.com/)
- [Express.js 文档](https://expressjs.com/)
- [React 文档](https://react.dev/)

## 🤝 贡献

欢迎贡献新的集成示例！请确保：
1. 代码质量高，有完整注释
2. 包含详细的 README
3. 提供可运行的示例
4. 遵循项目代码规范

## 📝 许可

本项目采用 MIT 许可证。
