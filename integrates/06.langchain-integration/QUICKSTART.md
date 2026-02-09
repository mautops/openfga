# LangChain + OpenFGA 集成示例 - 快速开始指南

## 5 分钟快速开始

### 前置要求

- Python 3.9+
- Docker（用于运行 OpenFGA）
- OpenAI API Key

### 步骤 1: 启动 OpenFGA (1 分钟)

```bash
# 使用 Docker 启动 OpenFGA
docker run -d \
  --name openfga \
  -p 8080:8080 \
  openfga/openfga run

# 验证 OpenFGA 是否运行
curl http://localhost:8080/healthz
```

### 步骤 2: 安装依赖 (1 分钟)

```bash
# 进入项目目录
cd 06.langchain-integration

# 创建虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 步骤 3: 设置 OpenFGA (1 分钟)

```bash
# 运行设置脚本（自动创建 Store 和上传授权模型）
python setup_openfga.py
```

这个脚本会：
1. 创建一个新的 OpenFGA Store
2. 上传授权模型
3. 生成 `.env` 文件

### 步骤 4: 配置 API Key (30 秒)

```bash
# 编辑 .env 文件
nano .env  # 或使用你喜欢的编辑器

# 修改以下行：
OPENAI_API_KEY=your-openai-api-key  # 填入你的 OpenAI API Key
```

### 步骤 5: 运行示例 (1.5 分钟)

```bash
# 运行完整示例
python example_agent.py
```

你将看到 7 个示例场景的运行结果：
1. ✅ 读取有权限的文档
2. ❌ 尝试读取无权限的文档
3. ✅ 编辑有权限的文档
4. ❌ 尝试编辑无权限的文档
5. ✅ 查询数据库
6. ❌ 尝试执行敏感操作
7. ✅ 动态授予权限后读取文档

## 运行测试

```bash
# 运行单元测试
pytest test_tools.py -v
```

## 下一步

- 阅读 [README.md](README.md) 了解详细文档
- 查看 [authorization_model.fga](authorization_model.fga) 了解授权模型
- 修改 [example_agent.py](example_agent.py) 创建你自己的 Agent
- 参考第 15、16 章了解更多 AI 场景权限管理知识

## 常见问题

### Q: OpenFGA 启动失败？

```bash
# 检查端口是否被占用
lsof -i :8080

# 停止并删除旧容器
docker stop openfga && docker rm openfga

# 重新启动
docker run -d --name openfga -p 8080:8080 openfga/openfga run
```

### Q: 示例运行失败？

1. 确认 OpenFGA 正在运行：`curl http://localhost:8080/healthz`
2. 确认 `.env` 文件中的配置正确
3. 确认 OpenAI API Key 有效
4. 查看日志输出，定位具体错误

### Q: 如何修改权限模型？

1. 编辑 `authorization_model.fga` 文件
2. 重新运行 `python setup_openfga.py`
3. 或手动上传模型：
   ```bash
   curl -X POST http://localhost:8080/stores/{store_id}/authorization-models \
     -H "Content-Type: application/json" \
     -d @authorization_model.json
   ```

## 获取帮助

- 查看 [OpenFGA 官方文档](https://openfga.dev/docs)
- 查看 [LangChain 官方文档](https://python.langchain.com/docs/get_started/introduction)
- 阅读本书第 15、16 章

## 许可证

MIT License
