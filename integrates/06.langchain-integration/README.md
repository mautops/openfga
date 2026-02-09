# LangChain + OpenFGA 集成示例

这个示例展示了如何将 OpenFGA 集成到 LangChain 应用中，实现 AI Agent 的细粒度权限控制。

## 功能特性

### 1. 权限控制
- **Agent 权限检查**: 检查 Agent 是否有权限执行工具
- **工具调用授权**: 每个工具调用前检查权限
- **用户代理模式**: Agent 代表用户执行操作
- **权限继承**: Agent 继承用户权限

### 2. 工具类型
- **文档查询工具**: 需要 viewer 权限
- **文档编辑工具**: 需要 editor 权限
- **数据库查询工具**: 需要 db_reader 权限
- **敏感操作工具**: 需要 admin 权限

### 3. 安全特性
- **默认拒绝**: 没有明确授权则拒绝访问
- **SQL 注入防护**: 只允许 SELECT 查询
- **审计日志**: 记录所有权限检查和操作
- **错误处理**: 完整的异常处理和错误提示

## 文件结构

```
06.langchain-integration/
├── agent_permissions.py      # OpenFGA 权限检查封装
├── tools.py                   # 带权限检查的工具定义
├── example_agent.py           # 完整的 Agent 示例
├── authorization_model.fga    # OpenFGA 授权模型
├── .env.example               # 环境变量示例
├── requirements.txt           # Python 依赖
└── README.md                  # 本文件
```

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 启动 OpenFGA

```bash
# 使用 Docker 启动 OpenFGA
docker run -d \
  --name openfga \
  -p 8080:8080 \
  openfga/openfga run
```

### 3. 创建 Store 和 Model

```bash
# 创建 Store
curl -X POST http://localhost:8080/stores \
  -H "Content-Type: application/json" \
  -d '{"name": "langchain-demo"}'

# 记录返回的 store_id

# 上传授权模型
curl -X POST http://localhost:8080/stores/{store_id}/authorization-models \
  -H "Content-Type: application/json" \
  -d @authorization_model.json

# 记录返回的 authorization_model_id
```

### 4. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，填入实际的配置
# OPENFGA_STORE_ID=你的store_id
# OPENFGA_MODEL_ID=你的model_id
# OPENAI_API_KEY=你的openai_api_key
```

### 5. 运行示例

```bash
python example_agent.py
```

## 授权模型说明

### 类型定义

#### 1. User（用户）
基础用户类型，代表系统中的真实用户。

#### 2. Agent（AI Agent）
```fga
type agent
  relations
    define owner: [user]           # Agent 的所有者
    define can_act_as: owner       # Agent 可以代表用户行动
```

#### 3. Document（文档）
```fga
type document
  relations
    define owner: [user]                    # 文档所有者
    define viewer: [user, agent] or owner   # 查看者（用户或 Agent）
    define editor: [user] or owner          # 编辑者（只能是用户）
    define can_read: viewer                 # 读取权限
    define can_write: editor                # 写入权限
```

#### 4. Database（数据库）
```fga
type database
  relations
    define owner: [user]                    # 数据库所有者
    define reader: [user, agent] or owner   # 读取者
    define admin: [user] or owner           # 管理员
    define can_query: reader                # 查询权限
    define can_manage: admin                # 管理权限
```

#### 5. Sensitive Operation（敏感操作）
```fga
type sensitive_operation
  relations
    define owner: [user]              # 操作所有者
    define approver: [user]           # 审批者
    define can_execute: approver      # 执行权限（需要审批）
```

## 使用示例

### 场景 1：读取文档

```python
# Agent 读取有权限的文档
result = await agent_executor.ainvoke({
    "input": "请读取文档 doc1 的内容"
})
# 输出: ✅ 文档内容: 这是一份关于 AI 的技术文档。

# Agent 尝试读取无权限的文档
result = await agent_executor.ainvoke({
    "input": "请读取文档 doc3 的内容"
})
# 输出: ❌ 权限被拒绝: Agent assistant 无权读取文档 doc3
```

### 场景 2：编辑文档

```python
# Agent 编辑有权限的文档
result = await agent_executor.ainvoke({
    "input": "请将文档 doc1 的内容更新为 '新内容'"
})
# 输出: ✅ 文档 doc1 已更新

# Agent 尝试编辑无权限的文档
result = await agent_executor.ainvoke({
    "input": "请将文档 doc2 的内容更新为 '新内容'"
})
# 输出: ❌ 权限被拒绝: Agent assistant 无权编辑文档 doc2
```

### 场景 3：查询数据库

```python
# Agent 查询数据库
result = await agent_executor.ainvoke({
    "input": "请查询数据库 main，执行 SQL: SELECT * FROM users"
})
# 输出: ✅ 查询结果: [数据列表]

# Agent 尝试执行危险操作
result = await agent_executor.ainvoke({
    "input": "请执行 SQL: DELETE FROM users"
})
# 输出: ❌ 只允许 SELECT 查询，不支持修改操作
```

### 场景 4：动态授予权限

```python
# 动态授予权限
await permission_checker.grant_permission(
    user="agent:assistant",
    relation="viewer",
    object="document:doc3"
)

# 现在可以读取 doc3
result = await agent_executor.ainvoke({
    "input": "请读取文档 doc3 的内容"
})
# 输出: ✅ 文档内容: 这是一份敏感的财务报告。

# 撤销权限
await permission_checker.revoke_permission(
    user="agent:assistant",
    relation="viewer",
    object="document:doc3"
)
```

## 核心组件说明

### 1. OpenFGAPermissionChecker

权限检查器，封装 OpenFGA 客户端。

**主要方法:**
- `check_permission()`: 检查权限
- `grant_permission()`: 授予权限
- `revoke_permission()`: 撤销权限
- `batch_check_permissions()`: 批量检查权限
- `get_audit_logs()`: 获取审计日志

### 2. Protected Tools

带权限检查的工具类。

**工具列表:**
- `ProtectedDocumentReadTool`: 文档读取工具
- `ProtectedDocumentWriteTool`: 文档编辑工具
- `ProtectedDatabaseQueryTool`: 数据库查询工具
- `ProtectedSensitiveOperationTool`: 敏感操作工具

**工具特性:**
- 继承 `BaseTool`
- 使用 Pydantic 模型验证输入
- 异步执行
- 完整的错误处理
- 审计日志记录

### 3. Agent Executor

LangChain Agent 执行器。

**配置:**
- 使用 OpenAI GPT-4 模型
- 集成带权限检查的工具
- 自定义 Prompt 模板
- 错误处理和重试机制

## 最佳实践

### 1. 最小权限原则

只授予 Agent 完成任务所需的最小权限。

```python
# ✅ 好的做法：只授予必需的权限
await permission_checker.grant_permission(
    user="agent:assistant",
    relation="viewer",
    object="document:doc1"
)

# ❌ 不好的做法：授予过大的权限
await permission_checker.grant_permission(
    user="agent:assistant",
    relation="owner",
    object="document:*"
)
```

### 2. 审计日志

记录所有权限检查和操作。

```python
# 启用审计日志
permission_checker = OpenFGAPermissionChecker(
    api_url="http://localhost:8080",
    store_id=store_id,
    model_id=model_id,
    enable_audit=True  # 启用审计
)

# 查看审计日志
logs = permission_checker.get_audit_logs(
    user="agent:assistant",
    limit=100
)
```

### 3. 错误处理

优雅地处理权限错误。

```python
try:
    result = await agent_executor.ainvoke({"input": "..."})
except PermissionDeniedError as e:
    logger.warning(f"权限被拒绝: {e}")
    # 向用户返回友好的错误信息
except Exception as e:
    logger.error(f"执行失败: {e}")
    # 处理其他错误
```

### 4. 性能优化

使用缓存和批量检查提升性能。

```python
# 批量检查权限
checks = [
    {"user": "agent:assistant", "relation": "viewer", "object": "document:doc1"},
    {"user": "agent:assistant", "relation": "viewer", "object": "document:doc2"},
    {"user": "agent:assistant", "relation": "viewer", "object": "document:doc3"}
]
results = await permission_checker.batch_check_permissions(checks)
```

## 常见问题

### Q1: 如何添加新的工具？

1. 创建新的工具类，继承 `BaseTool`
2. 定义输入模型（继承 `BaseModel`）
3. 实现 `_run()` 和 `_arun()` 方法
4. 在方法中添加权限检查
5. 将工具添加到 `create_protected_tools()` 函数

### Q2: 如何自定义权限模型？

1. 编辑 `authorization_model.fga` 文件
2. 添加新的类型和关系
3. 重新上传授权模型到 OpenFGA
4. 更新代码中的权限检查逻辑

### Q3: 如何处理权限继承？

在授权模型中使用 `from` 关键字：

```fga
type document
  relations
    define parent: [folder]
    define viewer: [user, agent] or viewer from parent
```

### Q4: 如何实现临时权限？

```python
# 授予临时权限
await permission_checker.grant_permission(
    user="agent:assistant",
    relation="viewer",
    object="document:doc3"
)

# 设置定时任务，在指定时间后撤销权限
await asyncio.sleep(3600)  # 1小时后
await permission_checker.revoke_permission(
    user="agent:assistant",
    relation="viewer",
    object="document:doc3"
)
```

## 参考资料

- [OpenFGA 官方文档](https://openfga.dev/docs)
- [LangChain 官方文档](https://python.langchain.com/docs/get_started/introduction)
- [第 15 章：AI 场景权限管理基础与框架集成](../chapters/第15章-AI场景权限管理基础与框架集成.md)
- [第 16 章：AI 应用实践案例与最佳实践](../chapters/第16章-AI应用实践案例与最佳实践.md)

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
