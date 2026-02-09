# 项目概览

## 项目简介

这个项目展示了如何将 AgentScope 多智能体框架与 OpenFGA 权限管理系统通过 MCP (Model Context Protocol) 协议集成。

## 核心组件

### 1. MCP 服务器 (mcp_server/)

**文件**: `openfga_mcp_server.py`

使用 FastMCP 框架创建的 MCP 服务器，将 OpenFGA 的功能暴露为 MCP 工具。

**提供的工具**:
- `check_permission`: 检查用户权限
- `write_tuples`: 写入关系元组
- `delete_tuples`: 删除关系元组
- `list_objects`: 列出用户有权限的对象
- `batch_check`: 批量检查权限

**技术栈**:
- FastMCP: MCP 服务器框架
- OpenFGA SDK: OpenFGA Python 客户端
- asyncio: 异步编程

### 2. AgentScope 客户端 (agentscope_client/)

**文件**: `permission_agent.py`

封装了 MCP 客户端调用的 AgentScope Agent，提供高级权限管理功能。

**核心类**:
- `PermissionAgent`: 权限管理 Agent 基类
  - 初始化 MCP 客户端
  - 注册 MCP 工具到 Toolkit
  - 提供便捷的权限操作方法
  - 支持对话式交互

**技术栈**:
- AgentScope: 多智能体框架
- HttpStatelessClient: MCP HTTP 客户端
- Toolkit: 工具管理

### 3. 示例代码 (examples/)

#### 示例 1: 文档权限管理 (`01_document_permissions.py`)

展示基本的文档权限管理流程：
1. 创建文档并设置所有者
2. 分享文档给其他用户
3. 检查用户权限
4. 列出用户可访问的文档

**适用场景**:
- 协作文档系统
- 文件共享平台
- 内容管理系统

#### 示例 2: 多智能体协作 (`02_multi_agent_collaboration.py`)

展示多个 Agent 协作管理权限系统：
- **AdminAgent**: 管理员 Agent，负责创建和管理权限
- **AuditorAgent**: 审计 Agent，负责检查和报告权限状态
- **UserAgent**: 用户 Agent，代表用户请求权限

**适用场景**:
- 企业权限管理系统
- 多租户 SaaS 平台
- 复杂的权限审计需求

### 4. 测试代码 (tests/)

**文件**: `test_integration.py`

完整的集成测试套件，验证：
- MCP 连接
- 权限检查
- 元组写入
- 对象列表
- 批量检查

## 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                   AgentScope Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ AdminAgent   │  │ AuditorAgent │  │  UserAgent   │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                  │           │
│         └─────────────────┼──────────────────┘           │
│                           │                              │
│                  ┌────────▼────────┐                     │
│                  │ PermissionAgent │                     │
│                  └────────┬────────┘                     │
└───────────────────────────┼──────────────────────────────┘
                            │
                            │ MCP Protocol
                            │ (HTTP/SSE)
                            │
┌───────────────────────────▼──────────────────────────────┐
│                    MCP Server Layer                       │
│                  ┌────────────────┐                       │
│                  │  FastMCP       │                       │
│                  │  Server        │                       │
│                  └────────┬───────┘                       │
│                           │                               │
│         ┌─────────────────┼─────────────────┐            │
│         │                 │                 │            │
│    ┌────▼────┐      ┌────▼────┐      ┌────▼────┐       │
│    │ check_  │      │ write_  │      │ list_   │       │
│    │permission│      │ tuples  │      │ objects │       │
│    └────┬────┘      └────┬────┘      └────┬────┘       │
└─────────┼──────────────────┼──────────────┼─────────────┘
          │                  │              │
          │    OpenFGA SDK   │              │
          │                  │              │
┌─────────▼──────────────────▼──────────────▼─────────────┐
│                   OpenFGA Server                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Authorization│  │  Tuple Store │  │  Check API   │  │
│  │    Model     │  │              │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└──────────────────────────────────────────────────────────┘
```

## 数据流

### 权限检查流程

```
1. User Request
   └─> AgentScope Agent
       └─> PermissionAgent.check_permission()
           └─> MCP Client (HTTP Request)
               └─> MCP Server
                   └─> OpenFGA SDK
                       └─> OpenFGA Server
                           └─> Check API
                               └─> Return: {allowed: true/false}
```

### 权限写入流程

```
1. Admin Action
   └─> AdminAgent.grant_permission()
       └─> PermissionAgent.write_tuples()
           └─> MCP Client (HTTP Request)
               └─> MCP Server
                   └─> OpenFGA SDK
                       └─> OpenFGA Server
                           └─> Write API
                               └─> Store Tuples
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `OPENFGA_API_URL` | OpenFGA API 地址 | `http://localhost:8080` |
| `OPENFGA_STORE_ID` | OpenFGA Store ID | 必填 |
| `OPENFGA_MODEL_ID` | 授权模型 ID | 必填 |
| `MCP_SERVER_URL` | MCP 服务器地址 | `http://localhost:8000/mcp` |
| `OPENAI_API_KEY` | OpenAI API Key | 可选 |

### 授权模型

项目使用的文档权限模型：

```
type user

type document
  relations
    define owner: [user]
    define editor: [user] or owner
    define viewer: [user] or editor
```

**权限继承关系**:
- `owner` → 拥有所有权限
- `editor` → 继承 owner 权限 + 编辑权限
- `viewer` → 继承 editor 权限 + 查看权限

## 性能考虑

### MCP 客户端类型

1. **HttpStatelessClient** (推荐)
   - 无状态，每次调用独立
   - 适合高并发场景
   - 无需管理连接生命周期

2. **HttpStatefulClient**
   - 有状态，维护会话
   - 适合需要上下文的场景
   - 需要手动管理连接

### 批量操作

使用 `batch_check` 进行批量权限检查，减少网络往返：

```python
# ❌ 不推荐：多次单独检查
for user in users:
    await agent.check_permission(user, "viewer", "document", "doc1")

# ✅ 推荐：批量检查
await agent.batch_check([
    {"user": user, "relation": "viewer", "object": "document:doc1"}
    for user in users
])
```

## 扩展建议

### 1. 添加缓存

在 PermissionAgent 中添加权限检查缓存：

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
async def check_permission_cached(self, user, relation, object_type, object_id):
    return await self.check_permission(user, relation, object_type, object_id)
```

### 2. 添加更多工具

扩展 MCP 服务器，添加更多 OpenFGA 功能：
- `read_changes`: 读取变更历史
- `expand`: 展开权限关系
- `list_users`: 列出有权限的用户

### 3. 集成其他 Agent 框架

MCP 协议是通用的，可以集成到其他框架：
- LangChain
- AutoGPT
- CrewAI

## 故障排除

### 常见问题

1. **MCP 连接失败**
   - 检查 MCP 服务器是否运行
   - 验证 URL 配置是否正确

2. **OpenFGA 连接失败**
   - 检查 OpenFGA 服务是否运行
   - 验证 Store ID 和 Model ID

3. **权限检查返回 false**
   - 检查授权模型是否正确
   - 验证关系元组是否已写入

## 参考资源

- [AgentScope 文档](https://doc.agentscope.io/)
- [MCP 协议规范](https://modelcontextprotocol.io/)
- [OpenFGA 文档](https://openfga.dev/)
- [FastMCP GitHub](https://github.com/jlowin/fastmcp)
