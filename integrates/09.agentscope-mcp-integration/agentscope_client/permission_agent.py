#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentScope 权限管理 Agent

这个模块展示如何在 AgentScope 中使用 MCP 协议调用 OpenFGA 权限管理服务。

主要功能：
- 通过 MCP 协议连接到 OpenFGA 服务
- 使用 AgentScope 的 Toolkit 管理权限工具
- 创建具有权限管理能力的 AI Agent
"""

import asyncio
import os
from typing import List, Dict, Any, Optional

from agentscope.agents import DialogAgent
from agentscope.message import Msg
from agentscope.mcp import HttpStatelessClient
from agentscope.tools import Toolkit
import agentscope


class PermissionAgent:
    """
    权限管理 Agent

    这个 Agent 可以通过 MCP 协议调用 OpenFGA 服务，
    执行权限检查、关系管理等操作。
    """

    def __init__(
        self,
        mcp_server_url: str,
        agent_name: str = "PermissionAgent",
        model_config: Optional[Dict[str, Any]] = None
    ):
        """
        初始化权限管理 Agent

        Args:
            mcp_server_url: MCP 服务器 URL
            agent_name: Agent 名称
            model_config: 模型配置
        """
        self.mcp_server_url = mcp_server_url
        self.agent_name = agent_name
        self.model_config = model_config or {}

        # 初始化 MCP 客户端
        self.mcp_client = HttpStatelessClient(
            name="openfga_mcp",
            transport="streamable_http",
            url=mcp_server_url
        )

        # 初始化工具包
        self.toolkit = Toolkit()

        # Agent 实例
        self.agent = None

    async def initialize(self):
        """初始化 Agent 和工具"""
        # 注册 MCP 工具到 Toolkit
        await self.toolkit.register_mcp_client(
            self.mcp_client,
            group_name="openfga"
        )

        print(f"✅ 已注册 {len(self.toolkit.get_json_schemas())} 个 OpenFGA 工具")

        # 打印可用工具
        for tool in self.toolkit.get_json_schemas():
            print(f"  - {tool['function']['name']}: {tool['function']['description'][:60]}...")

        # 创建 DialogAgent
        self.agent = DialogAgent(
            name=self.agent_name,
            sys_prompt=self._get_system_prompt(),
            model_config_name=self.model_config.get("config_name", "default"),
            use_memory=True,
            tools=self.toolkit.get_json_schemas()
        )

    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个权限管理助手，可以帮助用户管理和检查 OpenFGA 权限系统。

你可以执行以下操作：
1. check_permission: 检查用户是否有特定权限
2. write_tuples: 添加权限关系
3. delete_tuples: 删除权限关系
4. list_objects: 列出用户有权限的对象
5. batch_check: 批量检查多个权限

请根据用户的需求，选择合适的工具来完成任务。
在执行操作前，请确认用户的意图，并清晰地说明你将要执行的操作。
"""

    async def check_permission(
        self,
        user: str,
        relation: str,
        object_type: str,
        object_id: str
    ) -> Dict[str, Any]:
        """
        检查权限（直接调用 MCP 工具）

        Args:
            user: 用户标识
            relation: 关系类型
            object_type: 对象类型
            object_id: 对象ID

        Returns:
            权限检查结果
        """
        func = await self.mcp_client.get_callable_function(
            func_name="check_permission",
            wrap_tool_result=False
        )

        result = await func(
            user=user,
            relation=relation,
            object_type=object_type,
            object_id=object_id
        )

        return result

    async def write_tuples(self, tuples: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        写入关系元组

        Args:
            tuples: 关系元组列表

        Returns:
            写入结果
        """
        func = await self.mcp_client.get_callable_function(
            func_name="write_tuples",
            wrap_tool_result=False
        )

        result = await func(tuples=tuples)
        return result

    async def list_objects(
        self,
        user: str,
        relation: str,
        object_type: str
    ) -> Dict[str, Any]:
        """
        列出用户有权限的对象

        Args:
            user: 用户标识
            relation: 关系类型
            object_type: 对象类型

        Returns:
            对象列表
        """
        func = await self.mcp_client.get_callable_function(
            func_name="list_objects",
            wrap_tool_result=False
        )

        result = await func(
            user=user,
            relation=relation,
            object_type=object_type
        )

        return result

    def chat(self, message: str) -> str:
        """
        与 Agent 对话

        Args:
            message: 用户消息

        Returns:
            Agent 回复
        """
        if self.agent is None:
            raise RuntimeError("Agent 未初始化，请先调用 initialize()")

        msg = Msg(
            name="user",
            content=message,
            role="user"
        )

        response = self.agent(msg)
        return response.content


async def main():
    """示例：使用 PermissionAgent"""
    # 初始化 AgentScope
    agentscope.init(
        model_configs=[
            {
                "config_name": "default",
                "model_type": "openai_chat",
                "model_name": "gpt-4",
                "api_key": os.getenv("OPENAI_API_KEY"),
            }
        ]
    )

    # 创建权限 Agent
    agent = PermissionAgent(
        mcp_server_url="http://localhost:8000/mcp",
        agent_name="OpenFGA助手"
    )

    # 初始化
    await agent.initialize()

    # 示例 1: 直接调用工具检查权限
    print("\n=== 示例 1: 检查权限 ===")
    result = await agent.check_permission(
        user="user:alice",
        relation="viewer",
        object_type="document",
        object_id="doc1"
    )
    print(f"权限检查结果: {result}")

    # 示例 2: 写入权限关系
    print("\n=== 示例 2: 添加权限 ===")
    result = await agent.write_tuples([
        {"user": "user:alice", "relation": "owner", "object": "document:doc1"},
        {"user": "user:bob", "relation": "viewer", "object": "document:doc1"}
    ])
    print(f"写入结果: {result}")

    # 示例 3: 列出用户有权限的对象
    print("\n=== 示例 3: 列出权限对象 ===")
    result = await agent.list_objects(
        user="user:alice",
        relation="owner",
        object_type="document"
    )
    print(f"Alice 拥有的文档: {result}")

    # 示例 4: 与 Agent 对话
    print("\n=== 示例 4: 对话式权限管理 ===")
    response = agent.chat("请检查 user:bob 是否可以查看 document:doc1")
    print(f"Agent 回复: {response}")


if __name__ == "__main__":
    asyncio.run(main())
