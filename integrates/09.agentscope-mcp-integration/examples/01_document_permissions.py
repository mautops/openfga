#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
示例 1: 文档权限管理

这个示例展示如何使用 AgentScope + MCP 管理文档权限系统。

场景：
- 创建文档并设置所有者
- 分享文档给其他用户
- 检查用户权限
- 列出用户可访问的文档
"""

import asyncio
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentscope_client.permission_agent import PermissionAgent


async def document_permission_example():
    """文档权限管理示例"""
    print("=" * 60)
    print("文档权限管理示例")
    print("=" * 60)

    # 创建权限 Agent
    agent = PermissionAgent(
        mcp_server_url=os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp"),
        agent_name="文档权限助手"
    )

    await agent.initialize()

    # 场景 1: Alice 创建文档并成为所有者
    print("\n📝 场景 1: Alice 创建文档 doc1")
    result = await agent.write_tuples([
        {"user": "user:alice", "relation": "owner", "object": "document:doc1"}
    ])
    print(f"✅ 设置所有者: {result}")

    # 场景 2: Alice 分享文档给 Bob（查看权限）
    print("\n🔗 场景 2: Alice 分享文档给 Bob")
    result = await agent.write_tuples([
        {"user": "user:bob", "relation": "viewer", "object": "document:doc1"}
    ])
    print(f"✅ 添加查看权限: {result}")

    # 场景 3: Alice 分享文档给 Charlie（编辑权限）
    print("\n✏️ 场景 3: Alice 分享文档给 Charlie（编辑权限）")
    result = await agent.write_tuples([
        {"user": "user:charlie", "relation": "editor", "object": "document:doc1"}
    ])
    print(f"✅ 添加编辑权限: {result}")

    # 场景 4: 检查各用户的权限
    print("\n🔍 场景 4: 检查用户权限")

    users_to_check = [
        ("alice", "owner"),
        ("alice", "editor"),
        ("alice", "viewer"),
        ("bob", "viewer"),
        ("bob", "editor"),
        ("charlie", "editor"),
        ("charlie", "viewer"),
        ("david", "viewer"),
    ]

    for user, relation in users_to_check:
        result = await agent.check_permission(
            user=f"user:{user}",
            relation=relation,
            object_type="document",
            object_id="doc1"
        )
        status = "✅ 允许" if result.get("allowed") else "❌ 拒绝"
        print(f"  {status} - {user} 的 {relation} 权限")

    # 场景 5: 列出 Alice 拥有的所有文档
    print("\n📋 场景 5: 列出 Alice 拥有的文档")
    result = await agent.list_objects(
        user="user:alice",
        relation="owner",
        object_type="document"
    )
    print(f"Alice 拥有的文档: {result.get('objects', [])}")

    # 场景 6: 列出 Bob 可以查看的文档
    print("\n📋 场景 6: 列出 Bob 可以查看的文档")
    result = await agent.list_objects(
        user="user:bob",
        relation="viewer",
        object_type="document"
    )
    print(f"Bob 可以查看的文档: {result.get('objects', [])}")

    print("\n" + "=" * 60)
    print("示例完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(document_permission_example())
