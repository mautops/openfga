# OpenFGA 授权模型格式说明

## 推荐格式：.fga DSL

OpenFGA 提供了人类友好的 DSL（领域特定语言）格式来定义授权模型。

### ✅ 推荐：使用 .fga 格式

**优点**：
- 易于阅读和理解
- 简洁明了
- 支持注释
- 易于版本控制
- 官方推荐格式

**示例** (`authorization_model.fga`):
```fga
model
  schema 1.1

type user

type document
  relations
    define owner: [user]
    define editor: [user]
    define viewer: [user] or editor or owner
```

### ❌ 不推荐：JSON 格式

**缺点**：
- 冗长复杂
- 难以阅读
- 容易出错
- 不适合人类编辑

**示例** (不推荐):
```json
{
  "schema_version": "1.1",
  "type_definitions": [
    {
      "type": "user",
      "relations": {}
    },
    {
      "type": "document",
      "relations": {
        "owner": {"this": {}},
        "editor": {"this": {}},
        "viewer": {
          "union": {
            "child": [
              {"this": {}},
              {"computedUserset": {"relation": "editor"}},
              {"computedUserset": {"relation": "owner"}}
            ]
          }
        }
      }
    }
  ]
}
```

## 如何使用 .fga 文件

### 1. 使用 fga CLI 工具

```bash
# 验证模型
fga model validate --file authorization_model.fga

# 写入模型到 OpenFGA
fga model write --store-id <store-id> --file authorization_model.fga
```

### 2. 在 Python 代码中使用

```python
from openfga_sdk import OpenFgaClient

async with OpenFgaClient(configuration) as client:
    # 读取 .fga 文件
    with open('authorization_model.fga', 'r') as f:
        model_dsl = f.read()
    
    # OpenFGA SDK 会自动将 DSL 转换为 JSON
    response = await client.write_authorization_model(
        body={"type_definitions": parse_dsl(model_dsl)}
    )
```

### 3. 转换工具

如果需要在 DSL 和 JSON 之间转换：

```bash
# DSL 转 JSON
fga model transform --file authorization_model.fga --output-format json

# JSON 转 DSL
fga model transform --file authorization_model.json --output-format dsl
```

## 最佳实践

1. **始终使用 .fga 格式**编写和维护授权模型
2. **添加注释**说明复杂的关系定义
3. **版本控制**将 .fga 文件纳入 Git 管理
4. **代码审查**让团队成员审查模型变更
5. **测试验证**使用 fga CLI 验证模型语法

## 示例对比

### 简单模型

**DSL 格式** (5 行):
```fga
type user

type document
  relations
    define owner: [user]
```

**JSON 格式** (20+ 行):
```json
{
  "schema_version": "1.1",
  "type_definitions": [
    {
      "type": "user",
      "relations": {},
      "metadata": {"relations": {}}
    },
    {
      "type": "document",
      "relations": {
        "owner": {"this": {}}
      },
      "metadata": {
        "relations": {
          "owner": {
            "directly_related_user_types": [
              {"type": "user"}
            ]
          }
        }
      }
    }
  ]
}
```

## 总结

- ✅ **使用 .fga DSL 格式**：人类友好，易于维护
- ❌ **避免 JSON 格式**：仅用于 API 传输，不适合人工编辑
- 🔧 **使用工具**：fga CLI 提供了完整的模型管理功能

更多信息请参考：
- [OpenFGA 模型语法文档](https://openfga.dev/docs/modeling/language)
- [fga CLI 文档](https://github.com/openfga/cli)
