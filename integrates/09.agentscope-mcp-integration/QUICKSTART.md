# 快速开始指南

本指南将帮助你在 5 分钟内运行 AgentScope + MCP + OpenFGA 集成示例。

## 前置要求

- Python 3.10+
- Docker（用于运行 OpenFGA）
- uv 包管理器

## 步骤 1: 启动 OpenFGA

```bash
# 启动 OpenFGA 服务
docker run -d \
  --name openfga \
  -p 8080:8080 \
  -p 8081:8081 \
  -p 3000:3000 \
  openfga/openfga run

# 验证服务运行
curl http://localhost:8080/healthz
```

## 步骤 2: 创建 Store 和授权模型

```bash
# 创建 Store
STORE_RESPONSE=$(curl -s -X POST http://localhost:8080/stores \
  -H "Content-Type: application/json" \
  -d '{"name": "agentscope-demo"}')

# 提取 Store ID
STORE_ID=$(echo $STORE_RESPONSE | jq -r '.id')
echo "Store ID: $STORE_ID"

# 创建授权模型（文档权限模型）
MODEL_RESPONSE=$(curl -s -X POST "http://localhost:8080/stores/$STORE_ID/authorization-models" \
  -H "Content-Type: application/json" \
  -d '{
    "schema_version": "1.1",
    "type_definitions": [
      {
        "type": "user",
        "relations": {},
        "metadata": {
          "relations": {}
        }
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

# 提取 Model ID
MODEL_ID=$(echo $MODEL_RESPONSE | jq -r '.authorization_model_id')
echo "Model ID: $MODEL_ID"
```

## 步骤 3: 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入 Store ID 和 Model ID
cat > .env << EOF
OPENFGA_API_URL=http://localhost:8080
OPENFGA_STORE_ID=$STORE_ID
OPENFGA_MODEL_ID=$MODEL_ID
MCP_SERVER_URL=http://localhost:8000/mcp
MCP_SERVER_PORT=8000
EOF
```

## 步骤 4: 安装依赖

```bash
# 使用 uv 安装依赖
uv pip install -r requirements.txt
```

## 步骤 5: 启动 MCP 服务器

```bash
# 在一个终端窗口中启动 MCP 服务器
python mcp_server/openfga_mcp_server.py
```

## 步骤 6: 运行示例

```bash
# 在另一个终端窗口中运行示例

# 示例 1: 文档权限管理
python examples/01_document_permissions.py

# 示例 2: 多智能体协作
python examples/02_multi_agent_collaboration.py
```

## 预期输出

### 示例 1 输出

```
============================================================
文档权限管理示例
============================================================

📝 场景 1: Alice 创建文档 doc1
✅ 设置所有者: {'success': True, 'tuples_written': 1}

🔗 场景 2: Alice 分享文档给 Bob
✅ 添加查看权限: {'success': True, 'tuples_written': 1}

✏️ 场景 3: Alice 分享文档给 Charlie（编辑权限）
✅ 添加编辑权限: {'success': True, 'tuples_written': 1}

🔍 场景 4: 检查用户权限
  ✅ 允许 - alice 的 owner 权限
  ✅ 允许 - alice 的 editor 权限
  ✅ 允许 - alice 的 viewer 权限
  ✅ 允许 - bob 的 viewer 权限
  ❌ 拒绝 - bob 的 editor 权限
  ✅ 允许 - charlie 的 editor 权限
  ✅ 允许 - charlie 的 viewer 权限
  ❌ 拒绝 - david 的 viewer 权限

📋 场景 5: 列出 Alice 拥有的文档
Alice 拥有的文档: ['document:doc1']

📋 场景 6: 列出 Bob 可以查看的文档
Bob 可以查看的文档: ['document:doc1']
```

## 故障排除

### 问题 1: OpenFGA 连接失败

```bash
# 检查 OpenFGA 是否运行
docker ps | grep openfga

# 检查端口是否开放
curl http://localhost:8080/healthz
```

### 问题 2: MCP 服务器启动失败

```bash
# 检查依赖是否安装
uv pip list | grep fastmcp

# 检查环境变量
cat .env
```

### 问题 3: 权限检查失败

```bash
# 验证 Store ID 和 Model ID 是否正确
echo $STORE_ID
echo $MODEL_ID

# 检查授权模型
curl "http://localhost:8080/stores/$STORE_ID/authorization-models/$MODEL_ID"
```

## 下一步

- 查看 [README.md](README.md) 了解更多功能
- 阅读 [AgentScope 文档](https://doc.agentscope.io/)
- 探索 [OpenFGA 文档](https://openfga.dev/)
- 学习 [MCP 协议](https://modelcontextprotocol.io/)

## 清理环境

```bash
# 停止并删除 OpenFGA 容器
docker stop openfga
docker rm openfga

# 删除虚拟环境（如果需要）
rm -rf .venv
```
