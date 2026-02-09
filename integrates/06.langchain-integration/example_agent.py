"""
完整的 LangChain Agent 示例

演示如何创建带权限检查的 LangChain Agent，包括：
1. 文档查询工具（需要 viewer 权限）
2. 文档编辑工具（需要 editor 权限）
3. 数据库查询工具（需要 db_reader 权限）
4. 敏感操作工具（需要 admin 权限）
"""

import asyncio
import os
import logging
from typing import Optional
from dotenv import load_dotenv

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from agent_permissions import OpenFGAPermissionChecker
from tools import create_protected_tools

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def setup_permissions(
    permission_checker: OpenFGAPermissionChecker,
    agent_id: str,
    user_id: str
):
    """设置权限关系

    Args:
        permission_checker: 权限检查器
        agent_id: Agent ID
        user_id: 用户 ID
    """
    logger.info(f"正在为 Agent {agent_id} 设置权限...")

    # 1. Agent 属于用户
    await permission_checker.grant_permission(
        user=f"agent:{agent_id}",
        relation="owner",
        object=f"user:{user_id}"
    )

    # 2. Agent 可以查看文档 doc1 和 doc2
    await permission_checker.grant_permission(
        user=f"agent:{agent_id}",
        relation="viewer",
        object="document:doc1"
    )
    await permission_checker.grant_permission(
        user=f"agent:{agent_id}",
        relation="viewer",
        object="document:doc2"
    )

    # 3. Agent 可以编辑文档 doc1（但不能编辑 doc2）
    # 注意：只有用户可以是 editor，所以我们授予用户权限
    await permission_checker.grant_permission(
        user=f"user:{user_id}",
        relation="editor",
        object="document:doc1"
    )

    # 4. Agent 可以查询数据库
    await permission_checker.grant_permission(
        user=f"agent:{agent_id}",
        relation="reader",
        object="database:main"
    )

    # 5. 敏感操作需要 admin 权限（默认不授予）
    # 如果需要，可以授予用户 admin 权限
    # await permission_checker.grant_permission(
    #     user=f"user:{user_id}",
    #     relation="approver",
    #     object="sensitive_operation:delete_all"
    # )

    logger.info("权限设置完成")


async def create_agent(
    agent_id: str,
    user_id: str,
    permission_checker: OpenFGAPermissionChecker,
    documents: Optional[dict] = None
) -> AgentExecutor:
    """创建带权限检查的 LangChain Agent

    Args:
        agent_id: Agent ID
        user_id: 用户 ID
        permission_checker: 权限检查器
        documents: 文档存储（可选）

    Returns:
        AgentExecutor: Agent 执行器
    """
    logger.info(f"正在创建 Agent {agent_id}...")

    # 1. 创建 LLM
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # 2. 创建带权限检查的工具
    tools = create_protected_tools(permission_checker, documents)

    # 3. 创建 Prompt
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            f"""你是一个智能助手，Agent ID 是 {agent_id}，服务用户 {user_id}。

你可以使用以下工具来帮助用户：
- read_document: 读取文档内容（需要 viewer 权限）
- write_document: 编辑文档内容（需要 editor 权限）
- query_database: 查询数据库（需要 db_reader 权限）
- sensitive_operation: 执行敏感操作（需要 admin 权限）

重要提示：
1. 在调用工具时，必须提供你的 Agent ID: {agent_id}
2. 如果权限被拒绝，请礼貌地告知用户，并说明需要什么权限
3. 不要尝试绕过权限检查
4. 所有操作都会被审计记录

请始终遵守权限规则，确保用户数据安全。"""
        ),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # 4. 创建 Agent
    agent = create_openai_functions_agent(llm, tools, prompt)

    # 5. 创建 Agent Executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5
    )

    logger.info(f"Agent {agent_id} 创建完成")
    return agent_executor


async def run_example_scenarios(
    agent_executor: AgentExecutor,
    permission_checker: OpenFGAPermissionChecker,
    agent_id: str
):
    """运行示例场景

    Args:
        agent_executor: Agent 执行器
        permission_checker: 权限检查器
        agent_id: Agent ID
    """
    print("\n" + "=" * 80)
    print("LangChain + OpenFGA 集成示例")
    print("=" * 80)

    # 场景 1：读取有权限的文档
    print("\n" + "-" * 80)
    print("场景 1：读取有权限的文档 (doc1)")
    print("-" * 80)
    result = await agent_executor.ainvoke({
        "input": f"请读取文档 doc1 的内容。我的 Agent ID 是 {agent_id}"
    })
    print(f"\n结果: {result['output']}")

    # 场景 2：尝试读取无权限的文档
    print("\n" + "-" * 80)
    print("场景 2：尝试读取无权限的文档 (doc3)")
    print("-" * 80)
    result = await agent_executor.ainvoke({
        "input": f"请读取文档 doc3 的内容。我的 Agent ID 是 {agent_id}"
    })
    print(f"\n结果: {result['output']}")

    # 场景 3：编辑有权限的文档
    print("\n" + "-" * 80)
    print("场景 3：编辑有权限的文档 (doc1)")
    print("-" * 80)
    result = await agent_executor.ainvoke({
        "input": (
            f"请将文档 doc1 的内容更新为 '这是更新后的 AI 技术文档'。"
            f"我的 Agent ID 是 {agent_id}"
        )
    })
    print(f"\n结果: {result['output']}")

    # 场景 4：尝试编辑无权限的文档
    print("\n" + "-" * 80)
    print("场景 4：尝试编辑无权限的文档 (doc2)")
    print("-" * 80)
    result = await agent_executor.ainvoke({
        "input": (
            f"请将文档 doc2 的内容更新为 '这是更新后的权限管理文档'。"
            f"我的 Agent ID 是 {agent_id}"
        )
    })
    print(f"\n结果: {result['output']}")

    # 场景 5：查询数据库
    print("\n" + "-" * 80)
    print("场景 5：查询数据库")
    print("-" * 80)
    result = await agent_executor.ainvoke({
        "input": (
            f"请查询数据库 main，执行 SQL: SELECT * FROM users。"
            f"我的 Agent ID 是 {agent_id}"
        )
    })
    print(f"\n结果: {result['output']}")

    # 场景 6：尝试执行敏感操作（无权限）
    print("\n" + "-" * 80)
    print("场景 6：尝试执行敏感操作（无权限）")
    print("-" * 80)
    result = await agent_executor.ainvoke({
        "input": (
            f"请执行敏感操作 delete_all。"
            f"我的 Agent ID 是 {agent_id}"
        )
    })
    print(f"\n结果: {result['output']}")

    # 场景 7：动态授予权限后再次尝试
    print("\n" + "-" * 80)
    print("场景 7：动态授予权限后读取 doc3")
    print("-" * 80)
    print("正在授予权限...")
    await permission_checker.grant_permission(
        user=f"agent:{agent_id}",
        relation="viewer",
        object="document:doc3"
    )
    result = await agent_executor.ainvoke({
        "input": f"现在请读取文档 doc3 的内容。我的 Agent ID 是 {agent_id}"
    })
    print(f"\n结果: {result['output']}")

    # 显示审计日志
    print("\n" + "-" * 80)
    print("审计日志（最近 10 条）")
    print("-" * 80)
    logs = permission_checker.get_audit_logs(
        user=f"agent:{agent_id}",
        limit=10
    )
    for i, log in enumerate(logs, 1):
        print(f"\n{i}. {log['timestamp']}")
        print(f"   操作: {log['action']}")
        print(f"   用户: {log['user']}")
        print(f"   关系: {log['relation']}")
        print(f"   对象: {log['object']}")
        print(f"   结果: {'✅ 允许' if log['allowed'] else '❌ 拒绝'}")


async def main():
    """主函数"""
    try:
        # 1. 初始化 OpenFGA 权限检查器
        permission_checker = OpenFGAPermissionChecker(
            api_url=os.getenv("OPENFGA_API_URL", "http://localhost:8080"),
            store_id=os.getenv("OPENFGA_STORE_ID"),
            model_id=os.getenv("OPENFGA_MODEL_ID"),
            enable_audit=os.getenv("ENABLE_AUDIT_LOG", "true").lower() == "true"
        )

        # 2. 准备测试数据
        agent_id = "assistant"
        user_id = "alice"
        documents = {
            "doc1": "这是一份关于 AI 的技术文档。",
            "doc2": "这是一份关于权限管理的文档。",
            "doc3": "这是一份敏感的财务报告。"
        }

        # 3. 设置权限
        await setup_permissions(permission_checker, agent_id, user_id)

        # 4. 创建 Agent
        agent_executor = await create_agent(
            agent_id=agent_id,
            user_id=user_id,
            permission_checker=permission_checker,
            documents=documents
        )

        # 5. 运行示例场景
        await run_example_scenarios(
            agent_executor=agent_executor,
            permission_checker=permission_checker,
            agent_id=agent_id
        )

        # 6. 清理
        await permission_checker.close()

        print("\n" + "=" * 80)
        print("示例运行完成！")
        print("=" * 80)

    except Exception as e:
        logger.error(f"运行示例时发生错误: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
