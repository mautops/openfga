# OpenFGA 企业内训教程

## 📚 课程简介

权限管理是每个软件系统都无法回避的问题。随着系统业务复杂度的增加，传统的权限模型（如 RBAC、ABAC）往往显得力不从心。代码中散布着各种权限检查逻辑，每次修改权限规则都要改动多处代码，想要查看某个人的权限范围，混乱到几乎无法统计。

OpenFGA 是受 Google Zanzibar 启发的开源授权系统，采用关系型访问控制（ReBAC）模型，能够优雅地解决企业级授权系统的各种挑战。本教程将帮助你快速掌握 OpenFGA 的核心概念和实践方法。

---

## 1. 💡 为什么需要 OpenFGA

### 1.1 传统授权系统的挑战

在深入讨论授权系统之前，我们先明确一个基础概念：**授权和认证是两回事**。认证解决的是"你是谁"，授权解决的是"你能做什么"。用户登录后，系统通过认证确认了你的身份，但接下来要决定你能访问哪些资源、执行哪些操作，这就是授权要解决的问题。

传统的权限模型，如 RBAC（基于角色的访问控制）和 ABAC（基于属性的访问控制），在企业级应用初期往往能很好地满足需求。但随着应用架构的演进和业务复杂度的提升，这些传统模型开始暴露出各种问题。

**角色爆炸与过度授权**

随着企业组织规模增长，角色数量会急剧膨胀。为了满足各种细粒度的权限需求，开发者会创建大量相似但略有差异的角色，比如"部门经理-销售部"、"部门经理-市场部"等。在一个拥有数百个部门的大型企业中，角色数量可能达到数千个，管理变得极其复杂。

更糟糕的是，随着时间的推移，角色往往会积重难返，积累过多的权限。某个角色最初只需要访问特定资源，但为了满足临时需求，权限被不断添加，最终这个角色拥有了远超实际需要的权限，违反了最小权限原则，增加了安全风险。

**分布式架构中的授权困境**

在微服务架构中，开发团队将授权逻辑分散在各个服务中，每个服务都有自己的权限实现方式。这种分散导致了一系列问题：授权逻辑不一致、策略更新困难、缺乏统一治理、审计困难等。

用户在一个服务中有权限，在另一个服务中可能没有，这种不一致性不仅影响用户体验，更可能带来安全漏洞。每次修改权限规则，开发团队都要同步修改多个服务，需要协调多个团队，协调成本高，出错概率大。

**测试与调试的困境**

授权逻辑往往与业务逻辑深度耦合，测试授权功能需要启动整个应用，测试成本高、效率低。当授权出现问题时，权限检查逻辑分散在代码各处，故障排除变得极其困难。用户报告"无法访问某个资源"时，开发者需要检查代码中的各种权限检查逻辑，排查数据库中的权限数据，分析日志中的访问记录，这个过程耗时且容易出错。

**性能与可扩展性问题**

在大规模应用中，授权检查可能成为系统性能的瓶颈。每个请求可能需要进行多次授权决策，如果每次决策都要查询数据库，高并发场景下数据库很快就会成为瓶颈。以某大型电商平台为例，高峰期每秒需要处理数万次请求，每个请求平均需要进行 3-5 次授权检查，这意味着每秒需要进行数十万次数据库查询，数据库压力可想而知。

这些问题促使我们寻求更好的授权解决方案，这也为 OpenFGA 的诞生和发展提供了契机。

### 1.2 OpenFGA 的诞生与发展

OpenFGA 的诞生并非偶然。它源于对现代授权系统需求的深刻洞察，以及对 Google Zanzibar 这一杰出设计的学习和借鉴。

**Google Zanzibar 的启发**

Google Zanzibar 是 Google 内部使用的全球一致性授权系统，为 Google 的数百个服务和数十亿用户提供权限检查服务。2019 年，Google 在 Zanzibar 论文中详细描述了这一系统的设计理念和实现细节，在业界引起了巨大反响。

Zanzibar 的核心设计理念：

- **关系型访问控制（ReBAC）**：基于用户与资源之间的关系来定义权限
- **全局一致性**：在分布式环境中保证授权决策的一致性
- **高性能**：能够在毫秒级内响应授权检查请求
- **可扩展**：支持数万亿级别的权限关系

Zanzibar 解决了 Google 面临的几个关键问题。Google 的各个产品（如 Gmail、Drive、Photos、YouTube）需要共享一致的权限模型，如果每个产品都有自己的权限实现方式，跨产品的权限管理将变得非常困难。Zanzibar 提供了一个统一的授权服务，所有产品都可以使用相同的权限模型。

**OpenFGA 的发展历程**

- **2022 年 5 月**：OpenFGA 项目在 GitHub 上正式开源发布
- **2022 年 9 月**：被 CNCF 接纳为沙箱（Sandbox）项目
- **2024 年 10 月**：从沙箱项目晋升为 CNCF 孵化级（Incubating）项目
- **2025 年 11 月**：已有 37 家企业公开承认在生产环境中使用 OpenFGA

OpenFGA 并非 Zanzibar 的直接移植，而是在深入理解 Zanzibar 设计理念的基础上，结合开源社区的需求和最佳实践，重新设计和实现的授权系统。它继承了 Zanzibar 的关系型访问控制（ReBAC）思想，使用关系元组（Relationship Tuples）来表达权限关系，这是 OpenFGA 与 Zanzibar 最核心的共同点。

针对开源社区的需求，OpenFGA 进行了优化和简化，降低了使用门槛和学习成本。它提供了更友好的 API 设计，更完善的文档和示例，以及更丰富的开发工具。社区提供了 Java、.NET、JavaScript、Go、Python 等多种主流编程语言的 SDK，满足不同技术栈的需求。

### 1.3 OpenFGA 的核心价值

了解了 OpenFGA 的诞生背景，我们来看看它到底能为我们带来什么价值。

**声明式授权模型与策略即代码**

OpenFGA 采用声明式的授权模型，开发者通过简洁的 DSL（领域特定语言）定义权限规则，通过关系元组管理权限数据。授权模型可以像代码一样进行版本控制、代码审查和自动化测试。授权模型可以独立测试，不依赖业务代码，OpenFGA 提供了 CLI 工具和 Playground 来测试授权模型，开发者可以在不启动整个应用的情况下测试授权逻辑。

**极致的性能与可扩展性**

OpenFGA 在性能方面表现卓越，系统能够在毫秒级别内响应授权检查请求。根据测试数据，OpenFGA 可以处理每秒 100 万次授权检查请求，支持存储 1000 亿个关系元组。系统还支持批量操作，可以一次性检查多个权限关系，进一步提升了性能。

**强大的查询能力**

OpenFGA 提供了强大的查询能力，让开发者能够轻松回答复杂的权限问题。比如"用户 张三（zhangsan）可以查看哪些文档"、"哪些用户可以编辑这个文档"等。这些查询能力不仅提高了开发效率，也让企业能够更好地进行权限审计和合规检查。

**灵活的授权模式支持**

OpenFGA 支持多种授权模式，包括关系型访问控制（ReBAC）、角色型访问控制（RBAC）和属性型访问控制（ABAC），可以满足不同场景的需求。更重要的是，OpenFGA 的关系型访问控制模型可以优雅地表达复杂的权限关系，比如层级权限、多租户权限、动态权限等。

**完善的开发工具与集成**

OpenFGA 提供了完善的开发工具链，包括 CLI、Playground、多语言 SDK、VSCode 扩展、Terraform Provider 等，大大提升了开发体验。这些工具让开发者能够更快速地开发和测试授权逻辑，提高了开发效率。

---

## 2. 🚀 快速上手 OpenFGA

了解了 OpenFGA 的价值，接下来我们开始动手实践。这一章我们将通过一个完整的文档协作系统示例，让你在短时间内完成从环境搭建到第一个授权检查的全过程。

### 2.1 环境准备与快速启动

在开始之前，我们需要快速搭建一个 OpenFGA 运行环境。如果你之前用过 Docker，这个过程对你来说应该轻车熟路。如果你还没接触过 Docker，也不用担心，跟着步骤一步步来就行。

**前置要求：**

- 已安装 Docker（版本 20.10 或更高）
- 确保 Docker 服务正在运行

**一键启动 OpenFGA：**

OpenFGA 提供了官方的 Docker 镜像，只需要一条命令就能启动服务：

```bash
docker pull openfga/openfga && \
docker run -p 8080:8080 -p 8081:8081 -p 3000:3000 openfga/openfga run
```

命令说明：

- `-p 8080:8080` 映射 HTTP API 端口
- `-p 8081:8081` 映射 gRPC API 端口
- `-p 3000:3000` 映射 Playground 端口（可选，用于可视化测试）

当看到类似以下输出时，表示服务已成功启动：

```
{"level":"info","ts":1234567890.123,"msg":"starting openfga service..."}
{"level":"info","ts":1234567890.456,"msg":"grpc server listening","addr":"0.0.0.0:8081"}
{"level":"info","ts":1234567890.789,"msg":"http server listening","addr":"0.0.0.0:8080"}
```

**安装 fga CLI 工具：**

在实际开发中，你会发现 CLI 工具比 Web 界面更高效。安装 fga CLI 的过程很简单，但不同操作系统略有差异。

**macOS/Linux 系统：**

```bash
curl -L https://github.com/openfga/cli/releases/latest/download/fga-darwin-amd64 -o fga
chmod +x fga
sudo mv fga /usr/local/bin/
fga version
```

如果使用 Homebrew，安装会更简单：

```bash
brew install openfga/tap/fga
```

**Windows 系统：**

Windows 可以使用 Chocolatey：`choco install fga`，或从 [GitHub Releases](https://github.com/openfga/cli/releases) 手动下载可执行文件。

**验证服务运行状态：**

可以使用 curl 命令或浏览器访问健康检查端点：

```bash
curl http://localhost:8080/healthz
```

如果服务正常，会看到类似 `{"status":"ok"}` 的输出。或者打开浏览器访问 `http://localhost:8080/healthz`，也能看到相同的响应。

### 2.2 创建第一个 Store 和授权模型

服务启动成功后，接下来创建第一个 Store（存储空间）和授权模型。Store 是 OpenFGA 中用于隔离不同应用或租户数据的逻辑容器，每个 Store 都有自己独立的授权模型和关系元组。在实际项目中，你通常会为每个应用或租户创建一个独立的 Store，这样可以实现严格的数据隔离。

**创建 Store：**

使用 fga CLI 创建 Store 非常简单：

```bash
fga store create --name "我的第一个应用"
```

输出示例会显示 Store ID，需要保存这个 ID 并设置为环境变量：

```bash
export STORE_ID="01HZ3XK5Y8M9N0P1Q2R3S4T5U"
```

在实际项目中，你可能会创建多个 Store，建议使用有意义的名称，比如 `"生产环境-电商平台"` 或 `"测试环境-文档系统"`，这样便于管理和识别。

**创建授权模型：**

授权模型定义了系统中的实体类型、关系和权限。让我们创建一个简单的文档协作系统模型：

```bash
cat > model.fga << 'EOF'
model
  schema 1.1

type user

type document
  relations
    define owner: [user]
    define viewer: [user] or owner
    define editor: [user] or owner
EOF
```

然后使用 fga CLI 写入模型：

```bash
fga model write --store-id ${STORE_ID} --file model.fga
```

输出会显示 Model ID，需要保存它：

```bash
export MODEL_ID="01HZ3XK5Y8M9N0P1Q2R3S4T5U6V"
```

**理解模型的基本结构：**

授权模型由三个核心概念组成：

- **类型（Type）**：系统中的实体类型，如 `user`、`document`
- **关系（Relation）**：实体之间的关系，如 `owner`、`viewer`
- **权限（Permission）**：通过关系定义的访问权限

在上面的模型中，`viewer` 和 `editor` 都继承了 `owner` 的权限，这意味着如果用户是文档的所有者，自动拥有查看和编辑权限。这种继承机制让权限模型更加灵活和强大。

在实际开发中，你可能会发现模型设计需要多次迭代。不用担心，OpenFGA 支持模型版本管理，每次修改都会创建新版本，旧版本的关系元组仍然有效，这为你提供了平滑的迁移路径。

### 2.3 创建关系元组

模型定义好了，接下来需要创建关系元组（Relationship Tuple）来建立用户和文档之间的实际关系。关系元组定义了实体之间的实际关系。在实际项目中，这些关系元组通常由应用代码在用户执行操作时自动创建，比如用户创建文档时创建 `owner` 关系，用户邀请协作者时创建 `viewer` 或 `editor` 关系。

**创建关系元组：**

使用 fga CLI 创建单个关系元组：

```bash
# 创建文档所有者关系
fga tuple write --store-id ${STORE_ID} user:zhangsan owner document:doc1

# 创建查看者关系
fga tuple write --store-id ${STORE_ID} user:lisi viewer document:doc1
```

在实际项目中，你往往需要一次性创建多个关系元组。这时可以创建一个 JSON 文件：

```bash
cat > tuples.json << 'EOF'
{
  "tuples": [
    {"user": "user:zhangsan", "relation": "owner", "object": "document:doc1"},
    {"user": "user:lisi", "relation": "viewer", "object": "document:doc1"}
  ]
}
EOF

fga tuple write --store-id ${STORE_ID} --file tuples.json
```

**理解关系元组的含义：**

关系元组的格式为 `user:zhangsan#owner@document:doc1`，其中 `user:zhangsan` 是用户标识，`owner` 是关系类型，`document:doc1` 是文档标识。这个元组表示用户 张三（zhangsan）是文档 doc1 的所有者。在实际项目中，你需要确保用户标识和对象标识的格式一致，建议使用 `type:id` 的格式，比如 `user:123`、`document:abc-123`。

**查看关系元组：**

创建关系元组后，你可以使用 fga CLI 查看已创建的关系元组：

```bash
# 查询特定对象的所有关系元组
fga tuple read --store-id ${STORE_ID} --object document:doc1

# 查询特定用户的所有关系元组
fga tuple read --store-id ${STORE_ID} --user user:zhangsan
```

在实际开发中，你会发现这些查询命令非常有用，特别是在调试权限问题时，能够快速查看用户和资源之间的关系。

### 2.4 执行第一个授权检查

模型和关系元组都准备好了，接下来执行第一个授权检查，验证权限是否正确。这是最激动人心的时刻，你将看到 OpenFGA 如何根据关系元组和授权模型进行权限计算。

**使用 fga CLI 进行权限检查：**

使用 fga CLI 进行权限检查非常简单：

```bash
# 检查 张三（zhangsan）是否有编辑权限
fga query check --store-id ${STORE_ID} --model-id ${MODEL_ID} user:zhangsan editor document:doc1
```

如果一切正常，你会看到 `allowed: true` 的输出。这意味着 张三（zhangsan）确实拥有编辑权限，因为他被设置为文档的所有者，而 `editor` 关系继承了 `owner` 的权限。

让我们再检查一下 李四（lisi）的权限：

```bash
# 检查 李四（lisi）是否有编辑权限
fga query check --store-id ${STORE_ID} --model-id ${MODEL_ID} user:lisi editor document:doc1
```

这次你会看到 `allowed: false`，因为 李四（lisi）只是查看者，而 `editor` 关系不继承 `viewer` 的权限。

**使用配置文件简化命令：**

在实际开发中，你会发现每次都要输入 `--store-id` 和 `--model-id` 参数很麻烦。OpenFGA CLI 支持配置文件，可以避免重复输入参数：

```bash
cat > ~/.fga.yaml << EOF
api-url: http://localhost:8080
store-id: ${STORE_ID}
model-id: ${MODEL_ID}
EOF
```

配置后，可以简化命令：

```bash
fga query check user:zhangsan editor document:doc1
```

**理解授权检查的结果：**

`allowed: true` 表示用户拥有该权限，`allowed: false` 表示用户不拥有该权限。张三（zhangsan）有编辑权限是因为他是文档的所有者（`owner`），而 `editor` 关系继承了 `owner` 的权限。李四（lisi）没有编辑权限是因为他只是查看者（`viewer`），而 `editor` 关系不继承 `viewer` 的权限。

**验证权限传播机制：**

OpenFGA 的强大之处在于它的权限继承机制。让我们验证一下：

```bash
# 检查 张三（zhangsan）是否有查看权限
fga query check --store-id ${STORE_ID} --model-id ${MODEL_ID} user:zhangsan viewer document:doc1
```

即使我们没有为 张三（zhangsan）创建 `viewer` 关系元组，但由于 张三（zhangsan）是 `owner`，而 `viewer` 继承了 `owner` 的权限，所以检查结果应该是 `allowed: true`。这就是 OpenFGA 关系继承的魅力所在，你只需要定义核心关系，OpenFGA 会自动处理权限的传播。

在实际项目中，你会发现这种继承机制大大简化了权限管理。不需要为每个用户显式创建所有关系，只需要创建核心关系，OpenFGA 会自动计算派生权限。

### 2.5 完整示例：文档协作系统

现在让我们完成一个完整的文档协作系统示例，整合前面学到的所有知识。场景是一个文档协作系统，需要支持以下功能：用户可以创建文档并成为所有者，所有者可以邀请其他用户查看或编辑文档，查看者只能查看文档不能编辑，编辑者可以查看和编辑文档。

**权限模型设计：**

我们已经创建了授权模型，现在扩展它，添加明确的权限定义：

```openfga
model
  schema 1.1

type user

type document
  relations
    define owner: [user]
    define viewer: [user] or owner
    define editor: [user] or owner
    define can_view: viewer or editor
    define can_edit: editor
```

这个模型定义了三个关系（`owner`、`viewer`、`editor`）和两个权限（`can_view`、`can_edit`）。权限通过关系来定义，`can_view` 权限授予所有 `viewer` 和 `editor`，`can_edit` 权限只授予 `editor`。由于 `viewer` 和 `editor` 都继承了 `owner` 的权限，所以 `owner` 自动拥有所有权限。

**更新授权模型：**

使用 fga CLI 更新模型：

```bash
fga model write --store-id ${STORE_ID} --file model.fga
export MODEL_ID=$(fga model get --store-id ${STORE_ID} --field id)
```

**关系元组创建：**

现在创建关系元组，模拟一个真实的协作场景：

```bash
# 张三（zhangsan）创建文档 doc1，成为所有者
fga tuple write --store-id ${STORE_ID} user:zhangsan owner document:doc1

# 张三（zhangsan）邀请 李四（lisi）查看文档
fga tuple write --store-id ${STORE_ID} user:lisi viewer document:doc1

# 张三（zhangsan）邀请 王五（wangwu）编辑文档
fga tuple write --store-id ${STORE_ID} user:wangwu editor document:doc1
```

或者使用批量写入方式，这在初始化数据时更高效：

```bash
cat > tuples.json << 'EOF'
{
  "tuples": [
    {"user": "user:zhangsan", "relation": "owner", "object": "document:doc1"},
    {"user": "user:lisi", "relation": "viewer", "object": "document:doc1"},
    {"user": "user:wangwu", "relation": "editor", "object": "document:doc1"}
  ]
}
EOF

fga tuple write --store-id ${STORE_ID} --file tuples.json
```

**权限检查验证：**

现在使用 fga CLI 验证各种权限（如果已配置 `~/.fga.yaml`，可以省略 `--store-id` 和 `--model-id` 参数）：

```bash
# 张三（zhangsan）（所有者）可以查看和编辑
fga query check user:zhangsan can_view document:doc1  # 预期: allowed: true
fga query check user:zhangsan can_edit document:doc1  # 预期: allowed: true

# 李四（lisi）（查看者）只能查看，不能编辑
fga query check user:lisi can_view document:doc1    # 预期: allowed: true
fga query check user:lisi can_edit document:doc1    # 预期: allowed: false

# 王五（wangwu）（编辑者）可以查看和编辑
fga query check user:wangwu can_view document:doc1  # 预期: allowed: true
fga query check user:wangwu can_edit document:doc1   # 预期: allowed: true
```

**验证关系继承：**

让我们验证一下关系继承是否正常工作：

```bash
# 验证 张三（zhangsan）作为 owner，自动拥有 viewer 和 editor 关系
fga query check user:zhangsan viewer document:doc1  # 预期: allowed: true
fga query check user:zhangsan editor document:doc1  # 预期: allowed: true

# 验证 王五（wangwu）作为 editor，自动拥有 viewer 关系
fga query check user:wangwu viewer document:doc1  # 预期: allowed: true
```

所有权限检查都返回预期结果，权限继承机制正常工作，不同角色的权限正确区分。恭喜！你已经完成了第一个完整的 OpenFGA 应用示例！

在实际项目中，你会发现这种权限模型设计方式非常灵活。当业务需求变化时，只需要修改授权模型，不需要修改应用代码，这种解耦让权限管理变得简单而高效。

### 2.6 常见问题与快速排查

在快速入门过程中，你可能会遇到一些常见问题。这里提供快速排查方法，帮助你快速定位和解决问题。

**启动失败问题排查：**

如果 Docker 容器无法启动，可以按照以下步骤排查：

1. 检查 Docker 是否运行：`docker ps`
2. 检查端口是否被占用：`lsof -i :8080`（macOS/Linux）或 `netstat -ano | findstr :8080`（Windows）
3. 查看容器日志：`docker logs <container_id>`

如果端口被占用，可以修改端口映射，比如使用 `-p 8082:8080` 将容器内的 8080 端口映射到主机的 8082 端口。如果 Docker 未运行，需要启动 Docker 服务。

**授权检查返回 false 的原因分析：**

当授权检查返回 `allowed: false` 时，需要排查以下几个可能的原因：

1. **关系元组未创建**：最常见的原因，可能忘记创建关系元组
2. **授权模型未设置**：可能使用了错误的 Model ID
3. **关系定义错误**：授权模型中的关系定义可能有问题
4. **权限继承路径错误**：关系继承路径可能不正确

排查方法：

```bash
# 1. 检查关系元组是否存在
fga tuple read --store-id ${STORE_ID} --object document:doc1

# 2. 检查授权模型
fga model get --store-id ${STORE_ID} --model-id ${MODEL_ID}

# 3. 验证模型语法
fga model validate --file model.fga

# 4. 使用 Playground 可视化检查（访问 http://localhost:3000）
```

**模型语法错误排查：**

常见语法错误包括：

- 缺少类型定义：确保所有使用的类型都已定义
- 关系引用错误：确保关系引用正确
- 语法格式错误：确保缩进和格式正确

可以使用 Playground 的模型验证功能，或查看 fga CLI 返回的错误信息进行排查。在实际开发中，建议使用 VSCode 的 OpenFGA 扩展，它提供了语法高亮和实时验证功能，能够帮助你快速发现语法错误。

**Store ID 或 Model ID 错误：**

如果遇到 "store not found" 或 "model not found" 错误，可能是 Store ID 或 Model ID 不正确：

```bash
# 列出所有 Store
fga store list

# 查看当前 Store 的 Model ID
fga model get --store-id ${STORE_ID} --field id
```

---

## 3. 🐍 Python SDK 实战

掌握了 CLI 的基本操作后，接下来我们看看如何在 Python 应用中集成 OpenFGA。Python SDK 提供了完整的 API 封装，让你能够轻松地在应用代码中实现权限管理。

### 3.1 安装 Python SDK

首先需要安装 OpenFGA Python SDK：

```bash
pip install openfga-sdk
```

### 3.2 初始化客户端

在使用 Python SDK 之前，需要初始化 OpenFGA 客户端。根据[官方文档](https://pypi.org/project/openfga-sdk/)，强烈建议使用 `async with` 上下文管理器，只初始化一次 `OpenFgaClient` 并在整个应用中复用：

```python
from openfga_sdk import OpenFgaClient, ClientConfiguration
from openfga_sdk.client.models import (
    ClientCheckRequest,
    ClientWriteRequest,
    ClientTuple,
    ClientListObjectsRequest,
    ClientListUsersRequest,
    CreateStoreRequest,
)
from openfga_sdk.models.fga_object import FgaObject

# 配置客户端
configuration = ClientConfiguration(
    api_url="http://localhost:8080",  # OpenFGA 服务地址（必需）
    store_id=None,  # 可选，调用 CreateStore 或 ListStores 时不需要
    authorization_model_id=None,  # 可选，可以在每个请求中覆盖
)

# 推荐使用 async with 上下文管理器
async def main():
    async with OpenFgaClient(configuration) as fga_client:
        # 使用客户端进行操作
        # ...
        await fga_client.close()
        return
```

**注意**：`OpenFgaClient` 默认会在 429 和 5xx 错误时自动重试最多 3 次。

### 3.3 文件和文件夹授权模型

让我们设计一个文件和文件夹的授权模型，支持层级权限管理。这个模型比之前的文档模型更复杂，它展示了 OpenFGA 如何处理层级关系和权限继承：

```python
# 文件和文件夹授权模型
model_definition = """
model
  schema 1.1

type user

type folder
  relations
    define parent: [folder]
    define owner: [user]
    define viewer: [user] or owner or viewer from parent
    define editor: [user] or owner or editor from parent
    define can_view: viewer
    define can_edit: editor

type file
  relations
    define parent: [folder]
    define owner: [user]
    define viewer: [user] or owner or viewer from parent
    define editor: [user] or owner or editor from parent
    define can_view: viewer
    define can_edit: editor
"""
```

这个模型的特点：

- **文件夹层级关系**：文件夹可以有 `parent` 关系，形成层级结构
- **权限继承**：子文件夹和文件继承父文件夹的权限
- **权限定义**：`viewer` 和 `editor` 关系，以及对应的 `can_view` 和 `can_edit` 权限

### 3.4 创建 Store 和授权模型

模型设计好了，接下来通过 Python SDK 创建 Store 和授权模型：

```python
import asyncio
from openfga_sdk import OpenFgaClient, ClientConfiguration
from openfga_sdk.client.models import CreateStoreRequest

async def setup_openfga():
    async with OpenFgaClient(configuration) as fga_client:
        # 创建 Store（需要传入 CreateStoreRequest 对象）
        body = CreateStoreRequest(name="文件管理系统")
        store_response = await fga_client.create_store(body)
        store_id = store_response.id
        print(f"Store ID: {store_id}")

        # 更新配置中的 Store ID
        fga_client.store_id = store_id

        # 写入授权模型
        model_response = await fga_client.write_authorization_model(
            body={
                "schema_version": "1.1",
                "type_definitions": [
                    {
                        "type": "user"
                    },
                    {
                        "type": "folder",
                        "relations": {
                            "parent": {
                                "this": {}
                            },
                            "owner": {
                                "this": {}
                            },
                            "viewer": {
                                "union": {
                                    "child": [
                                        {"this": {}},
                                        {"computedUserset": {"relation": "owner"}},
                                        {"tupleToUserset": {
                                            "tupleset": {"relation": "parent"},
                                            "computedUserset": {"relation": "viewer"}
                                        }}
                                    ]
                                }
                            },
                            "editor": {
                                "union": {
                                    "child": [
                                        {"this": {}},
                                        {"computedUserset": {"relation": "owner"}},
                                        {"tupleToUserset": {
                                            "tupleset": {"relation": "parent"},
                                            "computedUserset": {"relation": "editor"}
                                        }}
                                    ]
                                }
                            },
                            "can_view": {
                                "computedUserset": {"relation": "viewer"}
                            },
                            "can_edit": {
                                "computedUserset": {"relation": "editor"}
                            }
                        }
                    },
                    {
                        "type": "file",
                        "relations": {
                            "parent": {
                                "this": {}
                            },
                            "owner": {
                                "this": {}
                            },
                            "viewer": {
                                "union": {
                                    "child": [
                                        {"this": {}},
                                        {"computedUserset": {"relation": "owner"}},
                                        {"tupleToUserset": {
                                            "tupleset": {"relation": "parent"},
                                            "computedUserset": {"relation": "viewer"}
                                        }}
                                    ]
                                }
                            },
                            "editor": {
                                "union": {
                                    "child": [
                                        {"this": {}},
                                        {"computedUserset": {"relation": "owner"}},
                                        {"tupleToUserset": {
                                            "tupleset": {"relation": "parent"},
                                            "computedUserset": {"relation": "editor"}
                                        }}
                                    ]
                                }
                            },
                            "can_view": {
                                "computedUserset": {"relation": "viewer"}
                            },
                            "can_edit": {
                                "computedUserset": {"relation": "editor"}
                            }
                        }
                    }
                ]
            }
        )

        authorization_model_id = model_response.authorization_model_id
        print(f"Authorization Model ID: {authorization_model_id}")

        return store_id, authorization_model_id

# 运行设置
store_id, model_id = asyncio.run(setup_openfga())
```

### 3.5 创建关系元组

Store 和模型都创建好了，接下来创建关系元组。我们将建立一个文件夹层级结构，并设置不同用户的权限：

```python
from openfga_sdk import OpenFgaClient, ClientConfiguration
from openfga_sdk.client.models import ClientWriteRequest, ClientTuple

async def create_relationships():
    async with OpenFgaClient(configuration) as fga_client:
        fga_client.store_id = store_id  # 使用之前创建的 Store ID

        # 创建文件夹层级关系
        # folder:project1 是根文件夹
        # folder:project1/docs 是 project1 的子文件夹

        # 张三（zhangsan）是 project1 文件夹的所有者
        # 使用 ClientWriteRequest 和 ClientTuple（不是字典）
        await fga_client.write(
            ClientWriteRequest(
                writes=[
                    ClientTuple(
                        user="user:zhangsan",
                        relation="owner",
                        object="folder:project1"
                    ),
                    ClientTuple(
                        user="user:zhangsan",
                        relation="owner",
                        object="file:readme.md"
                    )
                ]
            )
        )

        # 设置文件夹层级关系：docs 是 project1 的子文件夹
        await fga_client.write(
            ClientWriteRequest(
                writes=[
                    ClientTuple(
                        user="folder:project1",
                        relation="parent",
                        object="folder:project1/docs"
                    ),
                    ClientTuple(
                        user="folder:project1/docs",
                        relation="parent",
                        object="file:readme.md"
                    )
                ]
            )
        )

        # 李四（lisi）是 docs 文件夹的查看者
        await fga_client.write(
            ClientWriteRequest(
                writes=[
                    ClientTuple(
                        user="user:lisi",
                        relation="viewer",
                        object="folder:project1/docs"
                    )
                ]
            )
        )

        # 王五（wangwu）是 docs 文件夹的编辑者
        await fga_client.write(
            ClientWriteRequest(
                writes=[
                    ClientTuple(
                        user="user:wangwu",
                        relation="editor",
                        object="folder:project1/docs"
                    )
                ]
            )
        )

        print("关系元组创建完成")

asyncio.run(create_relationships())
```

### 3.6 执行授权检查

关系元组创建完成后，我们可以通过 Python SDK 检查用户对文件和文件夹的权限：

```python
from openfga_sdk import OpenFgaClient, ClientConfiguration
from openfga_sdk.client.models import ClientCheckRequest

async def check_permissions():
    async with OpenFgaClient(configuration) as fga_client:
        fga_client.store_id = store_id

        # 检查 张三（zhangsan）对 project1 文件夹的权限
        # 张三（zhangsan）是所有者，应该拥有所有权限
        # 使用 ClientCheckRequest（不是 CheckRequest）
        result = await fga_client.check(
            ClientCheckRequest(
                user="user:zhangsan",
                relation="can_view",
                object="folder:project1"
            )
        )
        print(f"张三（zhangsan） can_view folder:project1: {result.allowed}")  # True

        result = await fga_client.check(
            ClientCheckRequest(
                user="user:zhangsan",
                relation="can_edit",
                object="folder:project1"
            )
        )
        print(f"张三（zhangsan） can_edit folder:project1: {result.allowed}")  # True

        # 检查 李四（lisi）对 docs 文件夹的权限
        # 李四（lisi）是查看者，只能查看不能编辑
        result = await fga_client.check(
            ClientCheckRequest(
                user="user:lisi",
                relation="can_view",
                object="folder:project1/docs"
            )
        )
        print(f"李四（lisi） can_view folder:project1/docs: {result.allowed}")  # True

        result = await fga_client.check(
            ClientCheckRequest(
                user="user:lisi",
                relation="can_edit",
                object="folder:project1/docs"
            )
        )
        print(f"李四（lisi） can_edit folder:project1/docs: {result.allowed}")  # False

        # 检查权限继承：张三（zhangsan）是 project1 的所有者
        # 由于 docs 是 project1 的子文件夹，张三（zhangsan）应该自动拥有 docs 的权限
        result = await fga_client.check(
            ClientCheckRequest(
                user="user:zhangsan",
                relation="can_view",
                object="folder:project1/docs"
            )
        )
        print(f"张三（zhangsan） can_view folder:project1/docs (继承): {result.allowed}")  # True

        # 检查文件权限：readme.md 属于 docs 文件夹
        # 王五（wangwu）是 docs 的编辑者，应该可以编辑 readme.md
        result = await fga_client.check(
            ClientCheckRequest(
                user="user:wangwu",
                relation="can_edit",
                object="file:readme.md"
            )
        )
        print(f"王五（wangwu） can_edit file:readme.md: {result.allowed}")  # True

asyncio.run(check_permissions())
```

### 3.7 查询操作

除了检查单个权限，OpenFGA 还提供了强大的查询能力。你可以查询用户对特定关系拥有权限的所有资源，或者查询对特定资源拥有特定关系的所有用户：

```python
from openfga_sdk import OpenFgaClient, ClientConfiguration
from openfga_sdk.client.models import ClientListObjectsRequest, ClientListUsersRequest
from openfga_sdk.models.fga_object import FgaObject

async def query_permissions():
    async with OpenFgaClient(configuration) as fga_client:
        fga_client.store_id = store_id

        # ListObjects: 查询用户 张三（zhangsan）可以查看的所有文件夹
        # 使用 ClientListObjectsRequest（不是字典）
        response = await fga_client.list_objects(
            ClientListObjectsRequest(
                user="user:zhangsan",
                relation="can_view",
                type="folder"
            )
        )
        print(f"张三（zhangsan）可以查看的文件夹: {response.objects}")
        # 输出: ['folder:project1', 'folder:project1/docs']

        # ListObjects: 查询用户 李四（lisi）可以查看的所有文件
        response = await fga_client.list_objects(
            ClientListObjectsRequest(
                user="user:lisi",
                relation="can_view",
                type="file"
            )
        )
        print(f"李四（lisi）可以查看的文件: {response.objects}")
        # 输出: ['file:readme.md'] (因为 李四（lisi）是 docs 文件夹的查看者，readme.md 在 docs 中)

        # ListUsers: 查询对 docs 文件夹拥有编辑权限的所有用户
        # 使用 ClientListUsersRequest 和 FgaObject（不是字典）
        response = await fga_client.list_users(
            ClientListUsersRequest(
                object=FgaObject(type="folder", id="project1/docs"),
                relation="can_edit"
            )
        )
        print(f"可以编辑 folder:project1/docs 的用户: {response.users}")
        # 输出: ['user:zhangsan', 'user:wangwu']
        # 张三（zhangsan）因为继承自父文件夹，王五（wangwu）因为直接是编辑者

asyncio.run(query_permissions())
```

### 3.8 完整示例代码

下面是一个完整的示例，整合了所有操作。建议将模型定义保存为独立的 `.fga` 文件，然后通过 SDK 读取：

```python
import asyncio
from openfga_sdk import OpenFgaClient, ClientConfiguration
from openfga_sdk.client.models import (
    ClientCheckRequest,
    ClientWriteRequest,
    ClientTuple,
    ClientListObjectsRequest,
    ClientListUsersRequest,
    CreateStoreRequest,
)
from openfga_sdk.models.fga_object import FgaObject

async def main():
    # 1. 初始化客户端
    configuration = ClientConfiguration(
        api_url="http://localhost:8080",
        store_id=None,
    )

    # 使用 async with 上下文管理器
    async with OpenFgaClient(configuration) as client:
        # 2. 创建 Store（需要传入 CreateStoreRequest 对象）
        body = CreateStoreRequest(name="文件管理系统")
        store_response = await client.create_store(body)
        client.store_id = store_response.id
        print(f"✓ Store 创建成功: {client.store_id}")

        # 3. 写入授权模型
        # 注意：实际项目中建议将模型定义保存在 model.fga 文件中
        # 这里为了演示，我们直接使用 JSON 格式定义模型
        model_response = await client.write_authorization_model(
            body={
                "schema_version": "1.1",
                "type_definitions": [
                    {"type": "user"},
                    {
                        "type": "folder",
                        "relations": {
                            "parent": {"this": {}},
                            "owner": {"this": {}},
                            "viewer": {
                                "union": {
                                    "child": [
                                        {"this": {}},
                                        {"computedUserset": {"relation": "owner"}},
                                        {"tupleToUserset": {
                                            "tupleset": {"relation": "parent"},
                                            "computedUserset": {"relation": "viewer"}
                                        }}
                                    ]
                                }
                            },
                            "editor": {
                                "union": {
                                    "child": [
                                        {"this": {}},
                                        {"computedUserset": {"relation": "owner"}},
                                        {"tupleToUserset": {
                                            "tupleset": {"relation": "parent"},
                                            "computedUserset": {"relation": "editor"}
                                        }}
                                    ]
                                }
                            },
                            "can_view": {"computedUserset": {"relation": "viewer"}},
                            "can_edit": {"computedUserset": {"relation": "editor"}}
                        }
                    },
                    {
                        "type": "file",
                        "relations": {
                            "parent": {"this": {}},
                            "owner": {"this": {}},
                            "viewer": {
                                "union": {
                                    "child": [
                                        {"this": {}},
                                        {"computedUserset": {"relation": "owner"}},
                                        {"tupleToUserset": {
                                            "tupleset": {"relation": "parent"},
                                            "computedUserset": {"relation": "viewer"}
                                        }}
                                    ]
                                }
                            },
                            "editor": {
                                "union": {
                                    "child": [
                                        {"this": {}},
                                        {"computedUserset": {"relation": "owner"}},
                                        {"tupleToUserset": {
                                            "tupleset": {"relation": "parent"},
                                            "computedUserset": {"relation": "editor"}
                                        }}
                                    ]
                                }
                            },
                            "can_view": {"computedUserset": {"relation": "viewer"}},
                            "can_edit": {"computedUserset": {"relation": "editor"}}
                        }
                    }
                ]
            }
        )
        print(f"✓ 授权模型创建成功: {model_response.authorization_model_id}")

        # 4. 创建关系元组
        # 使用 ClientWriteRequest 和 ClientTuple（不是字典）
        await client.write(
            ClientWriteRequest(
                writes=[
                    # 张三（zhangsan）是 project1 文件夹的所有者
                    ClientTuple(user="user:zhangsan", relation="owner", object="folder:project1"),
                    # 设置文件夹层级：docs 是 project1 的子文件夹
                    ClientTuple(user="folder:project1", relation="parent", object="folder:project1/docs"),
                    # readme.md 文件属于 docs 文件夹
                    ClientTuple(user="folder:project1/docs", relation="parent", object="file:readme.md"),
                    # 李四（lisi）是 docs 文件夹的查看者
                    ClientTuple(user="user:lisi", relation="viewer", object="folder:project1/docs"),
                    # 王五（wangwu）是 docs 文件夹的编辑者
                    ClientTuple(user="user:wangwu", relation="editor", object="folder:project1/docs"),
                ]
            )
        )
        print("✓ 关系元组创建完成")

        # 5. 执行权限检查
        print("\n=== 权限检查结果 ===")
        checks = [
            ("user:zhangsan", "can_view", "folder:project1", True, "张三（zhangsan）查看 project1"),
            ("user:zhangsan", "can_edit", "folder:project1", True, "张三（zhangsan）编辑 project1"),
            ("user:lisi", "can_view", "folder:project1/docs", True, "李四（lisi）查看 docs"),
            ("user:lisi", "can_edit", "folder:project1/docs", False, "李四（lisi）编辑 docs（无权限）"),
            ("user:zhangsan", "can_view", "folder:project1/docs", True, "张三（zhangsan）查看 docs（继承权限）"),
            ("user:wangwu", "can_edit", "file:readme.md", True, "王五（wangwu）编辑 readme.md（继承权限）"),
        ]

        for user, relation, obj, expected, desc in checks:
            result = await client.check(
                ClientCheckRequest(user=user, relation=relation, object=obj)
            )
            status = "✓" if result.allowed == expected else "✗"
            print(f"{status} {desc}: {result.allowed} (预期: {expected})")

        # 6. 查询操作
        print("\n=== 查询操作结果 ===")
        # 查询 张三（zhangsan）可以查看的所有文件夹
        objects_response = await client.list_objects(
            ClientListObjectsRequest(user="user:zhangsan", relation="can_view", type="folder")
        )
        print(f"✓ 张三（zhangsan）可以查看的文件夹: {objects_response.objects}")
        # 预期输出: ['folder:project1', 'folder:project1/docs']

        # 查询对 docs 文件夹拥有编辑权限的所有用户
        users_response = await client.list_users(
            ClientListUsersRequest(
                object=FgaObject(type="folder", id="project1/docs"),
                relation="can_edit"
            )
        )
        print(f"✓ 可以编辑 folder:project1/docs 的用户: {users_response.users}")
        # 预期输出: ['user:zhangsan', 'user:wangwu']
        # 张三（zhangsan）因为继承自父文件夹，王五（wangwu）因为直接是编辑者

if __name__ == "__main__":
    asyncio.run(main())
```

**运行示例：**

```bash
# 确保 OpenFGA 服务正在运行
# docker run -p 8080:8080 openfga/openfga run

# 运行 Python 脚本
python example.py
```

**预期输出：**

```
✓ Store 创建成功: 01HZ3XK5Y8M9N0P1Q2R3S4T5U
✓ 授权模型创建成功: 01HZ3XK5Y8M9N0P1Q2R3S4T5U6V
✓ 关系元组创建完成

=== 权限检查结果 ===
✓ 张三（zhangsan）查看 project1: True (预期: True)
✓ 张三（zhangsan）编辑 project1: True (预期: True)
✓ 李四（lisi）查看 docs: True (预期: True)
✓ 李四（lisi）编辑 docs（无权限）: False (预期: False)
✓ 张三（zhangsan）查看 docs（继承权限）: True (预期: True)
✓ 王五（wangwu）编辑 readme.md（继承权限）: True (预期: True)

=== 查询操作结果 ===
✓ 张三（zhangsan）可以查看的文件夹: ['folder:project1', 'folder:project1/docs']
✓ 可以编辑 folder:project1/docs 的用户: ['user:zhangsan', 'user:wangwu']
```

### 3.9 错误处理

在实际应用中，需要添加适当的错误处理。网络请求可能失败，API 可能返回错误，这些都需要妥善处理：

```python
from openfga_sdk.exceptions import ApiException
from openfga_sdk.client.models import ClientCheckRequest

async def safe_check_permission(user, relation, obj):
    async with OpenFgaClient(configuration) as fga_client:
        fga_client.store_id = store_id
        try:
            result = await fga_client.check(
                ClientCheckRequest(user=user, relation=relation, object=obj)
            )
            return result.allowed
        except ApiException as e:
            print(f"API 错误: {e.status_code} - {e.reason}")
            return False
        except Exception as e:
            print(f"未知错误: {str(e)}")
            return False
```

### 3.10 最佳实践

在实际项目中，遵循以下最佳实践可以让你的 OpenFGA 集成更加稳定和高效：

1. **使用异步客户端**：Python SDK 支持异步操作，在高并发场景下性能更好
2. **批量操作**：使用 `write` 方法一次性创建多个关系元组，而不是逐个创建
3. **缓存授权结果**：对于频繁检查的权限，可以添加缓存层提升性能
4. **错误处理**：始终添加适当的错误处理逻辑
5. **连接池管理**：在生产环境中，合理配置 HTTP 连接池参数

---

## 4. 📝 课程总结

通过本教程的学习，你已经完成了 OpenFGA 的快速入门，掌握了从环境搭建到第一个授权检查的完整流程。

**核心要点回顾：**

1. **OpenFGA 的价值**：解决了传统授权系统的角色爆炸、策略管理复杂、分布式授权困境等问题
2. **核心概念**：Store（存储空间）、授权模型（Authorization Model）、关系元组（Relationship Tuple）
3. **基本操作**：创建 Store、定义授权模型、创建关系元组、执行授权检查
4. **权限继承**：OpenFGA 的强大之处在于它的权限继承机制，只需要定义核心关系，系统会自动处理权限的传播

**下一步学习建议：**

- 深入学习 OpenFGA 的架构与组件
- 掌握授权模型设计的最佳实践
- 学习如何通过 API 和 SDK 集成 OpenFGA
- 了解高级授权模式和性能优化技巧

在实际项目中，你会发现这种权限模型设计方式非常灵活。当业务需求变化时，只需要修改授权模型，不需要修改应用代码，这种解耦让权限管理变得简单而高效。
