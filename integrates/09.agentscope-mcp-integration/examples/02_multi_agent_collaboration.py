#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
示例 2: 多智能体协作权限管理

这个示例展示如何使用多个 AgentScope Agent 协作管理权限系统。

场景：
- 管理员 Agent：负责创建和管理权限
- 审计 Agent：负责检查和报告权限状态
- 用户 Agent：代表用户请求权限
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentscope_client.permission_agent import PermissionAgent


class AdminAgent:
    """管理员 Agent - 负责权限管理"""

    def __init__(self, permission_agent: PermissionAgent):
        self.agent = permission_agent

    async def create_document(self, doc_id: str, owner: str):
        """创建文档并设置所有者"""
        print(f"\n[管理员] 创建文档 {doc_id}，所有者: {owner}")
        result = await self.agent.write_tuples([
            {"user": owner, "relation": "owner", "object": f"document:{doc_id}"}
        ])
        return result

    async def grant_permission(self, user: str, relation: str, doc_id: str):
        """授予权限"""
        print(f"\n[管理员] 授予 {user} 对 {doc_id} 的 {relation} 权限")
        result = await self.agent.write_tuples([
            {"user": user, "relation": relation, "object": f"document:{doc_id}"}
        ])
        return result


class AuditorAgent:
    """审计 Agent - 负责权限检查和报告"""

    def __init__(self, permission_agent: PermissionAgent):
        self.agent = permission_agent

    async def audit_user_permissions(self, user: str, doc_id: str):
        """审计用户对文档的所有权限"""
        print(f"\n[审计员] 审计 {user} 对 document:{doc_id} 的权限")

        relations = ["owner", "editor", "viewer"]
        permissions = {}

        for relation in relations:
            result = await self.agent.check_permission(
                user=user,
                relation=relation,
                object_type="document",
                object_id=doc_id
            )
            permissions[relation] = result.get("allowed", False)
            status = "✅" if result.get("allowed") else "❌"
            print(f"  {status} {relation}")

        return permissions

    async def list_user_documents(self, user: str, relation: str):
        """列出用户有权限的文档"""
        print(f"\n[审计员] 列出 {user} 有 {relation} 权限的文档")
        result = await self.agent.list_objects(
            user=user,
            relation=relation,
            object_type="document"
        )
        docs = result.get("objects", [])
        print(f"  找到 {len(docs)} 个文档: {docs}")
        return docs


class UserAgent:
    """用户 Agent - 代表用户请求权限"""

    def __init__(self, permission_agent: PermissionAgent, user_id: str):
        self.agent = permission_agent
        self.user_id = user_id

    async def request_access(self, doc_id: str, relation: str):
        """请求访问权限"""
        print(f"\n[用户 {self.user_id}] 请求对 {doc_id} 的 {relation} 权限")

        # 检查当前权限
        result = await self.agent.check_permission(
            user=self.user_id,
            relation=relation,
            object_type="document",
            object_id=doc_id
        )

        if result.get("allowed"):
            print(f"  ✅ 已有权限")
        else:
            print(f"  ❌ 无权限，需要申请")

        return result.get("allowed", False)

    async def list_my_documents(self, relation: str):
        """列出我的文档"""
        print(f"\n[用户 {self.user_id}] 列出我有 {relation} 权限的文档")
        result = await self.agent.list_objects(
            user=self.user_id,
            relation=relation,
            object_type="document"
        )
        docs = result.get("objects", [])
        print(f"  找到 {len(docs)} 个文档: {docs}")
        return docs


async def multi_agent_collaboration():
    """多智能体协作示例"""
    print("=" * 60)
    print("多智能体协作权限管理示例")
    print("=" * 60)

    # 创建基础权限 Agent
    base_agent = PermissionAgent(
        mcp_server_url=os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp"),
        agent_name="权限管理系统"
    )
    await base_agent.initialize()

    # 创建专门的 Agent
    admin = AdminAgent(base_agent)
    auditor = AuditorAgent(base_agent)
    alice = UserAgent(base_agent, "user:alice")
    bob = UserAgent(base_agent, "user:bob")

    # 场景 1: 管理员创建文档
    print("\n" + "=" * 60)
    print("场景 1: 管理员创建文档")
    print("=" * 60)
    await admin.create_document("project_plan", "user:alice")
    await admin.create_document("meeting_notes", "user:alice")

    # 场景 2: 管理员授予权限
    print("\n" + "=" * 60)
    print("场景 2: 管理员授予权限")
    print("=" * 60)
    await admin.grant_permission("user:bob", "viewer", "project_plan")
    await admin.grant_permission("user:bob", "editor", "meeting_notes")

    # 场景 3: 审计员检查权限
    print("\n" + "=" * 60)
    print("场景 3: 审计员检查权限")
    print("=" * 60)
    await auditor.audit_user_permissions("user:alice", "project_plan")
    await auditor.audit_user_permissions("user:bob", "project_plan")
    await auditor.audit_user_permissions("user:bob", "meeting_notes")

    # 场景 4: 用户请求访问
    print("\n" + "=" * 60)
    print("场景 4: 用户请求访问")
    print("=" * 60)
    await alice.request_access("project_plan", "owner")
    await bob.request_access("project_plan", "viewer")
    await bob.request_access("project_plan", "editor")

    # 场景 5: 列出用户文档
    print("\n" + "=" * 60)
    print("场景 5: 列出用户文档")
    print("=" * 60)
    await alice.list_my_documents("owner")
    await bob.list_my_documents("viewer")
    await bob.list_my_documents("editor")

    # 场景 6: 审计员生成报告
    print("\n" + "=" * 60)
    print("场景 6: 审计员生成报告")
    print("=" * 60)
    await auditor.list_user_documents("user:alice", "owner")
    await auditor.list_user_documents("user:bob", "viewer")

    print("\n" + "=" * 60)
    print("多智能体协作示例完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(multi_agent_collaboration())
