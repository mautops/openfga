# AgentScope + MCP + OpenFGA 集成示例

这个示例展示如何在 AgentScope 中通过 MCP (Model Context Protocol) 协议调用 OpenFGA 权限管理服务。

## 🎯 核心特性

- **MCP 协议集成**: 使用 FastMCP 创建 OpenFGA MCP 服务器
- **AgentScope 客户端**: 通过 MCP 协议调用 OpenFGA 服务
- **多智能体协作**: 展示管理员、审计员、用户等多个 Agent 协作
- **完整权限管理**: 支持权限检查、关系管理、对象列表等功能

## 📁 项目结构

```
09.agentscope-mcp-integration/
├── mcp_server/              # MCP 服务器
│   └── openfga_mcp_server.py   # OpenFGA MCP 服务器实现
├── agentscope_client/       # AgentScope 客户端
│   └── permission_agent.py     # 权限管理 Agent
├── examples/                # 示例代码
│   ├── 01_document_permissions.py      # 文档权限管理
│   └── 02_multi_agent_collaboration.py # 多智能体协作
├── tests/                   # 测试代码
├── requirements.txt         # Python 依赖
├── .env.example            # 环境变量示例
└── README.md               # 本文件
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 使用 uv 安装依赖
cd 09.agentscope-mcp-integration
uv pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置 OpenFGA 和 OpenAI API
```

### 3. 启动 OpenFGA 服务

```bash
# 使用 Docker 启动 OpenFGA
docker run -d \
  --name openfga \
  -p 8080:8080 \
  -p 8081:8081 \
  -p 3000:3000 \
  openfga/openfga run
```

### 4. 创建 Store 和 Model

```bash
# 创建 Store
curl -X POST http://localhost:8080/stores \
  -H "Content-Type: application/json" \
  -d '{"name": "agentscope-demo"}'

# 记录返回的 store_id，并创建授权模型
# 参考 models/ 目录中的模型文件
```

### 5. 启动 MCP 服务器

```bash
# 方式 1: 使用 stdio 传输（用于本地开发）
python mcp_server/openfga_mcp_server.py

# 方式 2: 使用 HTTP 传输（用于远程访问）
# 需要配置 HTTP 服务器，如 uvicorn
```

### 6. 运行示例

```bash
# 示例 1: 文档权限管理
python examples/01_document_permissions.py

# 示例 2: 多智能体协作
python examples/02_multi_agent_collaboration.py
```

## 📚 核心概念

### MCP 服务器

MCP (Model Context Protocol) 是 Anthropic 提出的协议，用于让 LLM 与外部服务交互。

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("OpenFGA Permission Service")

@mcp.tool()
async def check_permission(user: str, relation: str, object_type: str, object_id: str):
    """检查用户权限"""
    # 实现权限检查逻辑
    pass
```

### AgentScope 客户端

AgentScope 通过 MCP 客户端调用远程服务：

```python
from agentscope.mcp import HttpStatelessClient
from agentscope.tools import Toolkit

# 创建 MCP 客户端
mcp_client = HttpStatelessClient(
    name="openfga_mcp",
    transport="streamable_http",
    url="http://localhost:8000/mcp"
)

# 注册工具
toolkit = Toolkit()
await toolkit.register_mcp_client(mcp_client)
```

### 权限管理 Agent

封装 MCP 调用，提供高级权限管理功能：

```python
agent = PermissionAgent(
    mcp_server_url="http://localhost:8000/mcp",
    agent_name="权限助手"
)

await agent.initialize()

# 检查权限
result = await agent.check_permission(
    user="user:alice",
    relation="viewer",
    object_type="document",
    object_id="doc1"
)
```

## 🔧 MCP 工具列表

| 工具名称 | 功能描述 | 参数 |
|---------|---------|------|
| `check_permission` | 检查用户权限 | user, relation, object_type, object_id |
| `write_tuples` | 写入关系元组 | tuples |
| `delete_tuples` | 删除关系元组 | tuples |
| `list_objects` | 列出有权限的对象 | user, relation, object_type |
| `batch_check` | 批量检查权限 | checks |

## 📖 使用场景

### 场景 1: 文档权限管理

```python
# 创建文档并设置所有者
await agent.write_tuples([
    {"user": "user:alice", "relation": "owner", "object": "document:doc1"}
])

# 分享给其他用户
await agent.write_tuples([
    {"user": "user:bob", "relation": "viewer", "object": "document:doc1"}
])

# 检查权限
result = await agent.check_permission(
    user="user:bob",
    relation="viewer",
    object_type="document",
    object_id="doc1"
)
```

### 场景 2: 多智能体协作

```python
# 管理员 Agent
admin = AdminAgent(base_agent)
await admin.create_document("project_plan", "user:alice")

# 审计 Agent
auditor = AuditorAgent(base_agent)
await auditor.audit_user_permissions("user:alice", "project_plan")

# 用户 Agent
alice = UserAgent(base_agent, "user:alice")
await alice.list_my_documents("owner")
```

## 🔍 技术架构

```
┌─────────────────┐
│  AgentScope     │
│  Multi-Agent    │
│  System         │
└────────┬────────┘
         │
         │ MCP Protocol
         │ (HTTP/SSE)
         │
┌────────▼────────┐
│  MCP Server     │
│  (FastMCP)      │
└────────┬────────┘
         │
         │ OpenFGA SDK
         │
┌────────▼────────┐
│  OpenFGA        │
│  Server         │
└─────────────────┘
```

## 🎓 学习资源

- [AgentScope 官方文档](https://doc.agentscope.io/)
- [MCP 协议规范](https://modelcontextprotocol.io/)
- [OpenFGA 文档](https://openfga.dev/)
- [FastMCP 文档](https://github.com/jlowin/fastmcp)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
