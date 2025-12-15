# 第 7 章：SDK 集成实战

在主流编程语言和框架中集成 OpenFGA

## 章节概述

在前面的章节中，我们深入学习了 OpenFGA 的核心概念、授权模型设计和 API 使用。从本章开始，我们将进入实战阶段，学习如何在实际项目中集成 OpenFGA SDK。

OpenFGA 提供了多种编程语言的 SDK，包括 Node.js/TypeScript、Python、Go 和 Java。这些 SDK 封装了底层的 HTTP 和 gRPC API，提供了更友好的编程接口，简化了与 OpenFGA 服务的交互。本章将通过丰富的代码示例，展示如何在不同技术栈中集成 OpenFGA，帮助你快速将授权功能集成到实际应用中。

**为什么需要使用 SDK？**

虽然我们可以直接使用 HTTP API 与 OpenFGA 交互，但使用官方 SDK 有以下优势：

- **类型安全**：SDK 提供了类型定义，减少编程错误
- **简化调用**：封装了复杂的 API 调用逻辑，提供更简洁的接口
- **自动重试**：内置错误处理和重试机制，提高稳定性
- **连接管理**：自动管理 HTTP/gRPC 连接池，优化性能
- **最佳实践**：遵循官方推荐的使用模式

**学习目标：**

完成本章学习后，你将能够：

1. 理解不同语言 SDK 的特点和适用场景
2. 掌握 Node.js/TypeScript SDK 的安装和配置
3. **重点掌握** Python SDK 的完整使用方法（本章核心内容）
4. 了解 Go SDK 在微服务架构中的应用
5. 了解 Java SDK 在企业级应用中的集成
6. 掌握前端框架（React、Vue）中的授权检查方法
7. 掌握后端框架（Express、FastAPI、Spring Boot）的中间件集成
8. 理解 SDK 的通用模式和最佳实践
9. 掌握错误处理、重试策略和性能优化技巧

**预计阅读时间：** 45-60 分钟

**前置知识要求：**

- 第 6 章：HTTP 和 gRPC API 使用
- 熟悉至少一种编程语言（建议 Python 或 JavaScript）
- 了解基本的 Web 开发概念

**本章内容安排：**

本章将首先介绍各语言 SDK 的对比和选择建议，然后重点使用 Python 语言展示完整的集成流程，包括安装配置、授权模型管理、关系元组操作、权限检查等核心功能。接着，我们会简要介绍其他语言 SDK 的使用方法，并展示在流行前后端框架中的集成实践。最后，我们将总结 SDK 使用的最佳实践和性能优化技巧。

---

## 7.1 SDK 概览与选择

OpenFGA 官方维护了多个语言的 SDK，每个 SDK 都提供了统一的编程接口，同时也针对各语言的特性进行了优化。本节将介绍各语言 SDK 的特点，帮助你根据项目需求选择合适的 SDK。

### 7.1.1 官方支持的 SDK

截至 OpenFGA v1.11.0，官方支持以下语言的 SDK：

| SDK                    | 包名称                      | 版本要求    | 适用场景                     |
| ---------------------- | --------------------------- | ----------- | ---------------------------- |
| **Node.js/TypeScript** | `@openfga/sdk`              | Node.js 14+ | Web 应用、微服务、Serverless |
| **Python**             | `openfga-sdk`               | Python 3.8+ | 数据分析、AI 应用、Web 后端  |
| **Go**                 | `github.com/openfga/go-sdk` | Go 1.19+    | 高性能微服务、云原生应用     |
| **Java**               | `dev.openfga:openfga-sdk`   | Java 11+    | 企业级应用、Spring Boot      |

> **注意**：虽然 OpenFGA 也提供 .NET SDK，但根据本书的技术范围定位，本章不包含 .NET 相关内容。

### 7.1.2 SDK 功能对比

所有官方 SDK 都提供以下核心功能：

**基础功能：**

- ✅ Store 管理（创建、查询存储）
- ✅ 授权模型管理（读取、写入模型）
- ✅ 关系元组操作（读取、写入、删除）
- ✅ 授权检查（Check API）
- ✅ 关系查询（ListObjects、ListUsers API）
- ✅ 批量检查（BatchCheck API）
- ✅ 扩展元组（Expand API）

**高级特性：**

- ✅ 异步/同步调用支持
- ✅ 连接池管理
- ✅ 自动重试机制
- ✅ 错误处理
- ✅ 类型安全
- ✅ 遥测和度量（Telemetry）

### 7.1.3 SDK 选择建议

根据不同的应用场景，我们提供以下选择建议：

**Web 前后端应用**

- **首选**：Node.js/TypeScript SDK
- **理由**：原生支持异步操作，与现代 Web 框架（Next.js、Express）深度集成
- **适用**：React/Vue 前端、Node.js 后端、Serverless 函数

**数据处理与 AI 应用**

- **首选**：Python SDK
- **理由**：与 Python 生态系统无缝集成，支持异步 I/O
- **适用**：数据分析、机器学习、AI Agent、FastAPI 后端

**高性能微服务**

- **首选**：Go SDK
- **理由**：原生支持并发，性能卓越，内存占用低
- **适用**：云原生应用、gRPC 微服务、Kubernetes 环境

**企业级 Java 应用**

- **首选**：Java SDK
- **理由**：与 Spring Boot、Maven/Gradle 生态完美集成
- **适用**：Spring Boot 应用、企业级系统、遗留系统集成

### 7.1.4 SDK 安装方式速查

为了方便读者快速开始，这里提供各 SDK 的安装命令：

**Node.js/TypeScript**

```bash
npm install @openfga/sdk
# 或使用 yarn
yarn add @openfga/sdk
```

**Python**

```bash
pip install openfga-sdk
```

**Go**

```bash
go get github.com/openfga/go-sdk
```

**Java（Maven）**

```xml
<dependency>
    <groupId>dev.openfga</groupId>
    <artifactId>openfga-sdk</artifactId>
    <version>0.5.0</version>
</dependency>
```

**Java（Gradle）**

```gradle
implementation 'dev.openfga:openfga-sdk:0.5.0'
```

### 7.1.5 本章示例代码约定

为了保持内容聚焦和深度，本章将**主要使用 Python**作为示例语言，原因如下：

1. **易读性强**：Python 语法清晰简洁，即使不熟悉 Python 的读者也能理解
2. **应用广泛**：适用于 Web 后端、数据处理、AI 应用等多种场景
3. **完整示例**：Python SDK 功能完整，支持所有 OpenFGA 特性
4. **异步支持**：原生支持 async/await，适合现代应用开发

对于其他语言，我们会提供关键代码片段和集成要点，完整示例可参考官方文档和 GitHub 仓库。

---

## 7.2 Node.js/TypeScript SDK 集成

Node.js/TypeScript SDK 是 OpenFGA 最流行的 SDK 之一,特别适合构建现代 Web 应用。它提供了完整的类型定义,支持异步操作,并且可以在 Node.js 后端和浏览器前端中使用(需注意安全性)。

### 7.2.1 安装与配置

**安装 SDK**

```bash
# 使用 npm
npm install @openfga/sdk

# 使用 yarn
yarn add @openfga/sdk

# 使用 pnpm
pnpm add @openfga/sdk
```

**基本配置**

```typescript
import { OpenFgaClient } from "@openfga/sdk";

// 创建客户端实例
const fgaClient = new OpenFgaClient({
  apiUrl: process.env.FGA_API_URL || "http://localhost:8080", // OpenFGA 服务地址
  storeId: process.env.FGA_STORE_ID, // Store ID
  authorizationModelId: process.env.FGA_MODEL_ID, // 可选,授权模型 ID
});
```

> **代码说明:**
>
> - **apiUrl**: OpenFGA 服务的 HTTP API 地址
> - **storeId**: 存储 ID,用于隔离不同应用的授权数据
> - **authorizationModelId**: 可选参数,指定默认使用的授权模型版本
> - 配置项可以通过环境变量管理,便于在不同环境间切换

### 7.2.2 核心操作示例

**权限检查 (Check)**

```typescript
// 检查用户是否有权限
const { allowed } = await fgaClient.check(
  {
    user: "user:alice",
    relation: "viewer",
    object: "document:planning",
  },
  {
    authorizationModelId: "01HVMMBCMGZNT3SED4Z17ECXCA", // 可选,覆盖默认模型
  }
);

console.log(`Access ${allowed ? "granted" : "denied"}`);
```

**列出对象 (ListObjects)**

```typescript
// 查询用户可以访问的所有对象
const response = await fgaClient.listObjects(
  {
    user: "user:alice",
    relation: "reader",
    type: "document",
  },
  {
    authorizationModelId: "01HVMMBCMGZNT3SED4Z17ECXCA",
  }
);

console.log("Accessible documents:", response.objects);
// 输出: ["document:planning", "document:roadmap"]
```

---

## 7.3 Python SDK 集成详解 (重点章节)

Python SDK 是本章的重点内容,我们将通过详尽的示例展示如何在 Python 应用中集成 OpenFGA。Python SDK 支持同步和异步两种调用方式,适用于 Web 应用、数据处理、AI 应用等多种场景。

### 7.3.1 环境准备与安装

**系统要求**

- Python 3.8 或更高版本
- pip 包管理器

**安装 SDK**

```bash
# 使用 pip 安装
pip install openfga-sdk

# 查看版本
pip show openfga-sdk
```

**验证安装**

```python
import openfga_sdk
print(f"OpenFGA SDK 版本: {openfga_sdk.__version__}")
```

### 7.3.2 客户端配置

**基本配置(异步方式)**

```python
import asyncio
import os
from openfga_sdk.client import ClientConfiguration, OpenFgaClient

async def main():
    # 配置客户端
    configuration = ClientConfiguration(
        api_url=os.environ.get('FGA_API_URL', 'http://localhost:8080'),  # OpenFGA 服务地址
        store_id=os.environ.get('FGA_STORE_ID'),  # Store ID
        authorization_model_id=os.environ.get('FGA_MODEL_ID'),  # 可选,授权模型 ID
    )

    # 创建客户端(使用上下文管理器自动关闭连接)
    async with OpenFgaClient(configuration) as fga_client:
        # 在这里执行 OpenFGA 操作
        print("OpenFGA 客户端已就绪")

        # 业务逻辑...
        pass

# 运行异步函数
if __name__ == "__main__":
    asyncio.run(main())
```

> **代码说明:**
>
> - **ClientConfiguration**: 配置对象,包含 API 地址、Store ID 等信息
> - **async with**: 使用上下文管理器确保连接正确关闭
> - **asyncio.run**: Python 3.7+ 推荐的异步程序入口
> - 所有环境变量通过 `os.environ.get()` 获取,支持默认值

**带身份认证的配置**

```python
from openfga_sdk.client import ClientConfiguration, OpenFgaClient
from openfga_sdk.credentials import Credentials, CredentialConfiguration

async def main():
    # API Token 认证
    credentials = Credentials(
        method='api_token',
        configuration=CredentialConfiguration(
            api_token=os.environ.get('FGA_API_TOKEN')
        )
    )

    configuration = ClientConfiguration(
        api_scheme='https',  # 生产环境使用 HTTPS
        api_host='api.fga.example.com',  # 生产环境地址
        store_id=os.environ.get('FGA_STORE_ID'),
        credentials=credentials,
    )

    async with OpenFgaClient(configuration) as fga_client:
        # 业务逻辑
        pass

if __name__ == "__main__":
    asyncio.run(main())
```

> **注意事项:**
>
> - 生产环境必须使用 HTTPS 协议
> - API Token 应通过环境变量或密钥管理服务获取,不要硬编码
> - Store ID 在不同环境(开发、测试、生产)可能不同

### 7.3.3 创建 Store 和授权模型

**创建 Store**

```python
from openfga_sdk import CreateStoreRequest

async def create_store(fga_client):
    """创建一个新的 OpenFGA Store"""
    try:
        store_request = CreateStoreRequest(name="my-application-store")
        response = await fga_client.create_store(store_request)

        store_id = response.id
        print(f"Store 创建成功,ID: {store_id}")
        return store_id

    except Exception as e:
        print(f"创建 Store 失败: {e}")
        raise
```

**定义并创建授权模型**

```python
from openfga_sdk import WriteAuthorizationModelRequest, TypeDefinition, Userset, Usersets, ObjectRelation, RelationMetadata, RelationReference, Metadata

async def create_authorization_model(fga_client):
    """创建授权模型:文档权限管理"""

    # 定义 user 类型
    user_type = TypeDefinition(type="user")

    # 定义 document 类型及其关系
    document_relations = {
        "owner": Userset(this={}),
        "editor": Userset(this={}),
        "viewer": Userset(
            union=Usersets(
                child=[
                    Userset(this={}),  # 直接 viewer
                    Userset(computed_userset=ObjectRelation(
                        object="",
                        relation="editor"
                    )),  # editor 也是 viewer
                    Userset(computed_userset=ObjectRelation(
                        object="",
                        relation="owner"
                    )),  # owner 也是 viewer
                ]
            )
        ),
    }

    # 定义关系元数据
    document_metadata = Metadata(
        relations={
            "owner": RelationMetadata(
                directly_related_user_types=[
                    RelationReference(type="user"),
                ]
            ),
            "editor": RelationMetadata(
                directly_related_user_types=[
                    RelationReference(type="user"),
                ]
            ),
            "viewer": RelationMetadata(
                directly_related_user_types=[
                    RelationReference(type="user"),
                ]
            ),
        }
    )

    document_type = TypeDefinition(
        type="document",
        relations=document_relations,
        metadata=document_metadata
    )

    # 创建授权模型请求
    body = WriteAuthorizationModelRequest(
        schema_version="1.1",
        type_definitions=[user_type, document_type]
    )

    try:
        response = await fga_client.write_authorization_model(body)
        model_id = response.authorization_model_id
        print(f"授权模型创建成功,ID: {model_id}")
        return model_id

    except Exception as e:
        print(f"创建授权模型失败: {e}")
        raise
```

> **代码说明:**
>
> - **TypeDefinition**: 定义对象类型(如 user, document)
> - **Userset**: 定义用户集合,支持 this(直接关系)、union(联合)、computed_userset(计算关系)等
> - **RelationMetadata**: 定义关系的元数据,指定哪些类型可以有这个关系
> - **schema_version**: OpenFGA v1.11.0 使用 "1.1" 版本

### 7.3.4 关系元组操作

**写入关系元组**

```python
from openfga_sdk import ClientTuple

async def write_tuples_example(fga_client):
    """写入关系元组示例"""

    # 单个元组
    tuple_1 = ClientTuple(
        user="user:alice",
        relation="owner",
        object="document:planning-doc"
    )

    # 批量写入
    tuples = [
        ClientTuple(
            user="user:alice",
            relation="owner",
            object="document:planning-doc"
        ),
        ClientTuple(
            user="user:bob",
            relation="editor",
            object="document:planning-doc"
        ),
        ClientTuple(
            user="user:charlie",
            relation="viewer",
            object="document:planning-doc"
        ),
    ]

    try:
        # 写入元组
        response = await fga_client.write(writes=tuples)
        print("关系元组写入成功")

    except Exception as e:
        print(f"写入元组失败: {e}")
        raise
```

**读取关系元组**

```python
from openfga_sdk import ReadRequestTupleKey

async def read_tuples_example(fga_client):
    """读取关系元组示例"""

    # 查询特定用户的所有关系
    body = ReadRequestTupleKey(
        user="user:alice",
        relation="owner",
        object="document:planning-doc",
    )

    try:
        response = await fga_client.read(body)
        print(f"找到 {len(response.tuples)} 个关系元组:")
        for tuple in response.tuples:
            print(f"  {tuple.key.user} --{tuple.key.relation}--> {tuple.key.object}")

    except Exception as e:
        print(f"读取元组失败: {e}")
        raise

    # 查询文档的所有权限关系
    body_all = ReadRequestTupleKey(
        object="document:planning-doc",  # 只指定对象
    )

    response_all = await fga_client.read(body_all)
    print(f"\n文档的所有权限关系:")
    for tuple in response_all.tuples:
        print(f"  {tuple.key.user} --{tuple.key.relation}--> {tuple.key.object}")
```

**删除关系元组**

```python
async def delete_tuples_example(fga_client):
    """删除关系元组示例"""

    # 要删除的元组
    tuple_to_delete = ClientTuple(
        user="user:charlie",
        relation="viewer",
        object="document:planning-doc"
    )

    try:
        # 删除元组
        response = await fga_client.write(deletes=[tuple_to_delete])
        print("关系元组删除成功")

    except Exception as e:
        print(f"删除元组失败: {e}")
        raise
```

> **代码说明:**
>
> - **writes**: 添加新的关系元组
> - **deletes**: 删除已有的关系元组
> - **read**: 查询关系元组,支持部分匹配(不指定某些字段则匹配所有)
> - 同一个 `write()` 调用可以同时包含 writes 和 deletes

### 7.3.5 权限检查

**基本权限检查**

```python
from openfga_sdk import ClientCheckRequest

async def check_permission(fga_client):
    """检查用户权限"""

    # 检查 Alice 是否是文档的 owner
    body = ClientCheckRequest(
        user="user:alice",
        relation="owner",
        object="document:planning-doc",
    )

    try:
        response = await fga_client.check(body)

        if response.allowed:
            print("✓ Alice 是文档的 owner")
        else:
            print("✗ Alice 不是文档的 owner")

        return response.allowed

    except Exception as e:
        print(f"权限检查失败: {e}")
        raise
```

**带上下文的权限检查**

```python
async def check_with_context(fga_client):
    """带条件的权限检查"""

    # 假设授权模型中定义了基于时间的条件
    body = ClientCheckRequest(
        user="user:bob",
        relation="editor",
        object="document:planning-doc",
        context={
            "current_time": "2024-01-15T10:00:00Z",
            "ip_address": "192.168.1.100"
        }
    )

    response = await fga_client.check(body)
    print(f"权限检查结果(带上下文): {response.allowed}")
```

**批量权限检查**

```python
async def batch_check(fga_client):
    """批量检查多个权限"""

    checks = [
        ClientCheckRequest(
            user="user:alice",
            relation="viewer",
            object="document:planning-doc"
        ),
        ClientCheckRequest(
            user="user:bob",
            relation="editor",
            object="document:planning-doc"
        ),
        ClientCheckRequest(
            user="user:charlie",
            relation="owner",
            object="document:planning-doc"
        ),
    ]

    options = {
        "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1"
    }

    try:
        results = await fga_client.batch_check(checks, options)

        for i, result in enumerate(results.responses):
            user = checks[i].user
            relation = checks[i].relation
            print(f"{user} --{relation}-->: {'✓ 允许' if result.allowed else '✗ 拒绝'}")

    except Exception as e:
        print(f"批量检查失败: {e}")
        raise
```

> **代码说明:**
>
> - **check**: 单次权限检查,返回布尔值 allowed
> - **context**: 传递上下文信息用于条件判断(ABAC)
> - **batch_check**: 批量检查,一次请求检查多个权限,提高性能
> - 批量检查时建议指定 authorization_model_id 以保证一致性

### 7.3.6 查询用户和对象

**列出对象 (ListObjects)**

```python
from openfga_sdk import ClientListObjectsRequest

async def list_objects_example(fga_client):
    """查询用户可以访问的所有对象"""

    body = ClientListObjectsRequest(
        user="user:alice",
        relation="viewer",
        type="document",
    )

    options = {
        "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1"
    }

    try:
        response = await fga_client.list_objects(body, options)

        print(f"Alice 可以查看的文档:")
        for obj in response.objects:
            print(f"  - {obj}")
        # 输出: document:planning-doc, document:roadmap, document:report

    except Exception as e:
        print(f"查询对象失败: {e}")
        raise
```

> **代码说明:**
>
> - **list_objects**: 查找用户有特定关系的所有对象,常用于生成资源列表
> - **type**: 指定对象类型进行过滤
> - 这个 API 的性能开销较大,建议配合缓存使用
> - 常用于生成用户的资源访问列表 UI

### 7.3.7 完整集成示例

以下是一个完整的 Python 应用示例,展示如何整合所有功能:

```python
import asyncio
import os
from typing import List
from openfga_sdk.client import ClientConfiguration, OpenFgaClient
from openfga_sdk import (
    ClientTuple,
    ClientCheckRequest,
    ClientListObjectsRequest,
    ReadRequestTupleKey,
)

class DocumentPermissionService:
    """文档权限管理服务"""

    def __init__(self, fga_client: OpenFgaClient):
        self.client = fga_client

    async def grant_permission(
        self,
        user_id: str,
        document_id: str,
        role: str
    ) -> bool:
        """授予用户对文档的权限"""
        tuple = ClientTuple(
            user=f"user:{user_id}",
            relation=role,  # owner, editor, viewer
            object=f"document:{document_id}"
        )

        try:
            await self.client.write(writes=[tuple])
            print(f"✓ 授予 {user_id} 对 {document_id} 的 {role} 权限")
            return True
        except Exception as e:
            print(f"✗ 授权失败: {e}")
            return False

    async def check_permission(
        self,
        user_id: str,
        document_id: str,
        permission: str
    ) -> bool:
        """检查用户是否有权限"""
        body = ClientCheckRequest(
            user=f"user:{user_id}",
            relation=permission,
            object=f"document:{document_id}"
        )

        try:
            response = await self.client.check(body)
            return response.allowed
        except Exception as e:
            print(f"✗ 权限检查失败: {e}")
            return False

    async def list_user_documents(
        self,
        user_id: str,
        permission: str = "viewer"
    ) -> List[str]:
        """列出用户可以访问的所有文档"""
        body = ClientListObjectsRequest(
            user=f"user:{user_id}",
            relation=permission,
            type="document"
        )

        try:
            response = await self.client.list_objects(body)
            # 提取文档 ID
            doc_ids = [obj.replace("document:", "") for obj in response.objects]
            return doc_ids
        except Exception as e:
            print(f"✗ 查询文档失败: {e}")
            return []


async def main():
    """主函数"""
    # 配置客户端
    configuration = ClientConfiguration(
        api_url=os.environ.get('FGA_API_URL', 'http://localhost:8080'),
        store_id=os.environ.get('FGA_STORE_ID'),
        authorization_model_id=os.environ.get('FGA_MODEL_ID'),
    )

    async with OpenFgaClient(configuration) as fga_client:
        # 创建服务实例
        service = DocumentPermissionService(fga_client)

        # 示例操作
        print("\n=== 1. 授予权限 ===")
        await service.grant_permission("alice", "planning-doc", "owner")
        await service.grant_permission("bob", "planning-doc", "editor")

        print("\n=== 2. 权限检查 ===")
        can_view = await service.check_permission("alice", "planning-doc", "viewer")
        print(f"Alice 可以查看文档: {can_view}")

        print("\n=== 3. 列出用户的文档 ===")
        alice_docs = await service.list_user_documents("alice", "viewer")
        print(f"Alice 可以查看的文档: {alice_docs}")


if __name__ == "__main__":
    asyncio.run(main())
```

> **代码说明:**
>
> - **DocumentPermissionService**: 封装了文档权限管理的常用操作
> - **依赖注入**: 通过构造函数注入 OpenFgaClient,便于测试
> - **错误处理**: 每个方法都包含 try-except,确保稳定性
> - **类型提示**: 使用 Python 类型提示,提高代码可读性

---

## 7.4 Go SDK 集成

Go SDK 适用于高性能微服务和云原生应用,具有出色的并发性能。

### 7.4.1 安装与配置

```bash
go get github.com/openfga/go-sdk
```

```go
package main

import (
    "context"
    "os"
    "github.com/openfga/go-sdk/client"
)

func main() {
    fgaClient, err := client.NewSdkClient(&client.ClientConfiguration{
        ApiUrl:               os.Getenv("FGA_API_URL"),
        StoreId:              os.Getenv("FGA_STORE_ID"),
        AuthorizationModelId: os.Getenv("FGA_MODEL_ID"),
    })
    if err != nil {
        panic(err)
    }
    defer fgaClient.Close()
}
```

### 7.4.2 权限检查示例

```go
func checkPermission(fgaClient *client.OpenFgaClient) {
    body := client.ClientCheckRequest{
        User:     "user:alice",
        Relation: "viewer",
        Object:   "document:planning",
    }

    response, err := fgaClient.Check(context.Background()).
        Body(body).
        Execute()

    if err != nil {
        fmt.Printf("检查失败: %v\n", err)
        return
    }

    fmt.Printf("允许访问: %v\n", response.GetAllowed())
}
```

---

## 7.5 Java SDK 集成

Java SDK 适用于企业级应用,与 Spring Boot 深度集成。

### 7.5.1 Maven 依赖

```xml
<dependency>
    <groupId>dev.openfga</groupId>
    <artifactId>openfga-sdk</artifactId>
    <version>0.5.0</version>
</dependency>
```

### 7.5.2 Spring Boot 配置

```java
import dev.openfga.sdk.api.client.OpenFgaClient;
import dev.openfga.sdk.api.configuration.ClientConfiguration;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenFgaConfig {

    @Value("${openfga.api-url}")
    private String apiUrl;

    @Value("${openfga.store-id}")
    private String storeId;

    @Bean
    public OpenFgaClient openFgaClient() throws Exception {
        var config = new ClientConfiguration()
            .apiUrl(apiUrl)
            .storeId(storeId);
        return new OpenFgaClient(config);
    }
}
```

---

## 7.6 前端框架集成

### 7.6.1 React Hook 示例

```typescript
// hooks/usePermission.ts
import { useState, useEffect } from "react";

export function usePermission(
  userId: string,
  objectId: string,
  relation: string
) {
  const [allowed, setAllowed] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/check-permission", {
      method: "POST",
      body: JSON.stringify({ userId, objectId, relation }),
    })
      .then((res) => res.json())
      .then((data) => setAllowed(data.allowed))
      .finally(() => setLoading(false));
  }, [userId, objectId, relation]);

  return { allowed, loading };
}

// 使用示例
function DocumentEditor({ documentId, userId }) {
  const { allowed, loading } = usePermission(userId, documentId, "editor");

  if (loading) return <div>Loading...</div>;
  if (!allowed) return <div>Access Denied</div>;
  return <div>Editor Content...</div>;
}
```

---

## 7.7 后端框架集成

### 7.7.1 FastAPI 中间件示例

```python
from fastapi import FastAPI, Depends, HTTPException, Header
from openfga_sdk.client import OpenFgaClient, ClientConfiguration, ClientCheckRequest
import os

app = FastAPI()

fga_config = ClientConfiguration(
    api_url=os.getenv("FGA_API_URL"),
    store_id=os.getenv("FGA_STORE_ID"),
)

async def get_fga_client():
    """依赖注入:获取 FGA 客户端"""
    async with OpenFgaClient(fga_config) as client:
        yield client

async def require_permission(
    user_id: str,
    object_id: str,
    relation: str,
    fga_client: OpenFgaClient = Depends(get_fga_client)
):
    """权限检查装饰器"""
    body = ClientCheckRequest(
        user=f"user:{user_id}",
        relation=relation,
        object=object_id
    )

    response = await fga_client.check(body)
    if not response.allowed:
        raise HTTPException(status_code=403, detail="Permission denied")

@app.get("/documents/{doc_id}")
async def get_document(
    doc_id: str,
    user_id: str = Header(...),
    fga_client: OpenFgaClient = Depends(get_fga_client)
):
    """获取文档(需要 viewer 权限)"""
    await require_permission(user_id, f"document:{doc_id}", "viewer", fga_client)
    return {"doc_id": doc_id, "content": "..."}
```

---

## 7.8 SDK 最佳实践与性能优化

### 7.8.1 使用批量操作

```python
# 推荐:批量检查
checks = [
    ClientCheckRequest(user="user:a", relation="viewer", object="doc:1"),
    ClientCheckRequest(user="user:b", relation="viewer", object="doc:2"),
]
results = await fga_client.batch_check(checks)

# 不推荐:循环单独检查
for check in checks:
    await fga_client.check(check)  # 多次网络请求
```

### 7.8.2 缓存策略

```python
from functools import lru_cache
import time

class PermissionCache:
    """权限结果缓存"""
    def __init__(self, ttl=60):
        self.cache = {}
        self.ttl = ttl

    def get(self, key):
        if key in self.cache:
            value, ts = self.cache[key]
            if time.time() - ts < self.ttl:
                return value
        return None

    def set(self, key, value):
        self.cache[key] = (value, time.time())

# 使用缓存
cache = PermissionCache(ttl=60)

async def check_cached(user, relation, obj):
    key = f"{user}:{relation}:{obj}"
    result = cache.get(key)
    if result is not None:
        return result

    body = ClientCheckRequest(user=user, relation=relation, object=obj)
    response = await fga_client.check(body)
    cache.set(key, response.allowed)
    return response.allowed
```

### 7.8.3 错误重试

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def check_with_retry(fga_client, user, relation, obj):
    """带重试的权限检查"""
    body = ClientCheckRequest(user=user, relation=relation, object=obj)
    return await fga_client.check(body)
```

> **最佳实践总结:**
>
> 1. **连接管理**: 使用单例模式共享客户端实例
> 2. **批量操作**: 优先使用批量 API 减少网络开销
> 3. **缓存策略**: 缓存权限检查结果,TTL 建议 30-60 秒
> 4. **错误处理**: 实现重试机制,区分可重试和不可重试的错误
> 5. **监控告警**: 记录 API 调用延迟和错误率

---

## 7.9 本章小结

在本章中,我们深入学习了 OpenFGA SDK 在多种编程语言和框架中的集成方法。通过丰富的代码示例和实践案例,相信你已经掌握了在实际项目中使用 OpenFGA 的核心技能。

**核心知识回顾:**

1. **SDK 选择与配置**

   - 根据项目需求选择合适的 SDK(Node.js、Python、Go、Java)
   - 掌握了客户端配置方法,包括基本配置和身份认证
   - 理解了不同 SDK 的特点和适用场景

2. **Python SDK 集成(重点)**

   - 完整学习了 Python SDK 的安装、配置和使用
   - 掌握了 Store 和授权模型的创建方法
   - 熟练使用关系元组的读写操作
   - 深入理解权限检查(Check)、列出对象(ListObjects)等核心 API
   - 学会了封装权限服务类,便于在实际项目中复用

3. **其他语言 SDK**

   - 了解了 Node.js/TypeScript SDK 的基本使用
   - 学习了 Go SDK 在高性能微服务中的应用
   - 掌握了 Java SDK 与 Spring Boot 的集成方法

4. **框架集成实践**

   - 前端框架集成:学会在 React 中使用自定义 Hook 管理权限
   - 后端框架集成:掌握了 FastAPI 中间件方式集成 OpenFGA
   - 理解了前后端协作中的权限检查流程

5. **最佳实践与优化**
   - 使用批量操作减少网络请求
   - 实现缓存策略提高性能
   - 采用错误重试机制提高可靠性
   - 掌握连接管理和资源复用技巧

**学习成果检验:**

完成本章学习后,你应该能够:

- ✅ 在任意主流语言项目中集成 OpenFGA SDK
- ✅ 独立完成授权模型的创建和管理
- ✅ 熟练使用 SDK 进行权限检查和元组操作
- ✅ 将 OpenFGA 集成到现有 Web 框架中
- ✅ 应用性能优化策略提升系统效率
- ✅ 处理常见错误和异常情况

**与后续章节的衔接:**

本章着重于 SDK 的基础使用和集成方法。在第 8 章《高级授权模式》中,我们将学习如何设计复杂的授权模型来满足企业级应用需求。在第 9 章《性能优化与扩展》中,我们将深入探讨大规模应用场景下的性能优化策略。

**持续学习建议:**

1. **动手实践**: 在自己的项目中尝试集成 OpenFGA
2. **阅读源码**: 研究 SDK 源码加深理解
3. **社区交流**: 参与 OpenFGA 社区讨论,学习最佳实践
4. **关注更新**: 定期查看官方文档,了解新特性和改进

---

## 实践练习

### 基础练习

**练习 7-1: 基础权限检查**

创建一个 Python 脚本,实现以下功能:

1. 连接到本地 OpenFGA 服务
2. 创建一个简单的授权模型(user 和 document 类型)
3. 添加 3 个关系元组
4. 检查用户对文档的 viewer 权限

**提示**: 参考 7.3.2 和 7.3.5 小节的示例代码。

**练习 7-2: 列出用户文档**

扩展练习 7-1,实现一个函数,列出指定用户可以访问的所有文档。

**提示**: 使用 `list_objects` API,参考 7.3.6 小节。

### 进阶练习

**练习 7-3: 权限管理服务封装**

设计并实现一个完整的权限管理服务类,包含以下方法:

```python
class PermissionService:
    async def grant(user_id, resource_id, permission): ...
    async def revoke(user_id, resource_id, permission): ...
    async def check(user_id, resource_id, permission): ...
    async def list_resources(user_id, permission): ...
```

要求:

- 完善的错误处理
- 日志记录
- 支持批量操作

**提示**: 参考 7.3.7 小节的完整示例。

**练习 7-4: FastAPI 集成**

创建一个 FastAPI 应用,集成 OpenFGA 实现以下接口:

1. `POST /documents`: 创建文档(自动授予创建者 owner 权限)
2. `GET /documents/{id}`: 获取文档(需要 viewer 权限)
3. `PUT /documents/{id}`: 更新文档(需要 editor 权限)
4. `DELETE /documents/{id}`: 删除文档(需要 owner 权限)
5. `GET /documents`: 列出当前用户可访问的所有文档

**提示**: 参考 7.7.1 小节的 FastAPI 中间件示例。

### 挑战练习

**练习 7-5: 性能优化实战**

实现一个带性能优化的权限检查系统:

1. 实现两层缓存机制(内存缓存 + Redis)
2. 支持批量权限检查
3. 实现智能重试机制(区分可重试和不可重试错误)
4. 添加性能监控(记录 API 延迟、缓存命中率)

要求:

- 缓存失效策略合理
- 并发安全
- 完整的监控指标

**提示**: 参考 7.8 节的最佳实践,结合 Redis 等技术。

**练习 7-6: 多语言 SDK 对比实现**

分别使用 Python、Node.js 和 Go 实现相同的功能:

1. 连接到 OpenFGA 服务
2. 创建授权模型
3. 执行权限检查
4. 列出用户可访问的资源

对比三种语言的:

- 代码风格差异
- 性能表现
- 适用场景

**提示**: 参考 7.2、7.3、7.4 节的示例代码。

---

## 延伸阅读

**官方文档:**

- [OpenFGA Python SDK 文档](https://github.com/openfga/python-sdk)
- [OpenFGA Node.js SDK 文档](https://github.com/openfga/js-sdk)
- [OpenFGA Go SDK 文档](https://github.com/openfga/go-sdk)
- [OpenFGA Java SDK 文档](https://github.com/openfga/java-sdk)

**社区资源:**

- [OpenFGA 官方文档](https://openfga.dev/docs)
- [OpenFGA GitHub 仓库](https://github.com/openfga/openfga)
- [OpenFGA 社区 Slack](https://openfga.dev/community)

**相关技术:**

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [asyncio 异步编程](https://docs.python.org/3/library/asyncio.html)
- [Spring Boot 官方指南](https://spring.io/guides)

**下一步学习:**

完成本章后,建议继续学习:

- **第 8 章**: 高级授权模式 - 学习多租户、层级权限等复杂场景
- **第 9 章**: 性能优化与扩展 - 深入了解大规模应用的优化技巧
- **第 11 章**: 企业级应用实践案例 - 学习真实项目的完整实践

---
