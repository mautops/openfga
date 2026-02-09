#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 AgentScope MCP 集成

这个测试文件验证 MCP 服务器和 AgentScope 客户端的功能。
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentscope_client.permission_agent import PermissionAgent


async def test_mcp_connection():
    """测试 MCP 连接"""
    print("测试 1: MCP 连接")
    try:
        agent = PermissionAgent(
            mcp_server_url=os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp"),
            agent_name="测试Agent"
        )
        await agent.initialize()
        print("✅ MCP 连接成功")
        return True
    except Exception as e:
        print(f"❌ MCP 连接失败: {e}")
        return False


async def test_check_permission():
    """测试权限检查"""
    print("\n测试 2: 权限检查")
    try:
        agent = PermissionAgent(
            mcp_server_url=os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp"),
            agent_name="测试Agent"
        )
        await agent.initialize()

        # 先写入一个权限
        await agent.write_tuples([
            {"user": "user:test", "relation": "owner", "object": "document:test_doc"}
        ])

        # 检查权限
        result = await agent.check_permission(
            user="user:test",
            relation="owner",
            object_type="document",
            object_id="test_doc"
        )

        if result.get("allowed"):
            print("✅ 权限检查成功")
            return True
        else:
            print("❌ 权限检查失败")
            return False
    except Exception as e:
        print(f"❌ 权限检查异常: {e}")
        return False


async def test_write_tuples():
    """测试写入元组"""
    print("\n测试 3: 写入元组")
    try:
        agent = PermissionAgent(
            mcp_server_url=os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp"),
            agent_name="测试Agent"
        )
        await agent.initialize()

        result = await agent.write_tuples([
            {"user": "user:alice", "relation": "owner", "object": "document:test1"},
            {"user": "user:bob", "relation": "viewer", "object": "document:test1"}
        ])

        if result.get("success"):
            print(f"✅ 写入元组成功: {result.get('tuples_written')} 个")
            return True
        else:
            print("❌ 写入元组失败")
            return False
    except Exception as e:
        print(f"❌ 写入元组异常: {e}")
        return False


async def test_list_objects():
    """测试列出对象"""
    print("\n测试 4: 列出对象")
    try:
        agent = PermissionAgent(
            mcp_server_url=os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp"),
            agent_name="测试Agent"
        )
        await agent.initialize()

        # 先写入一些权限
        await agent.write_tuples([
            {"user": "user:alice", "relation": "owner", "object": "document:doc1"},
            {"user": "user:alice", "relation": "owner", "object": "document:doc2"}
        ])

        # 列出对象
        result = await agent.list_objects(
            user="user:alice",
            relation="owner",
            object_type="document"
        )

        if result.get("success"):
            print(f"✅ 列出对象成功: {result.get('count')} 个")
            print(f"   对象列表: {result.get('objects')}")
            return True
        else:
            print("❌ 列出对象失败")
            return False
    except Exception as e:
        print(f"❌ 列出对象异常: {e}")
        return False


async def test_batch_check():
    """测试批量检查"""
    print("\n测试 5: 批量检查")
    try:
        agent = PermissionAgent(
            mcp_server_url=os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp"),
            agent_name="测试Agent"
        )
        await agent.initialize()

        # 先写入一些权限
        await agent.write_tuples([
            {"user": "user:alice", "relation": "owner", "object": "document:doc1"},
            {"user": "user:bob", "relation": "viewer", "object": "document:doc1"}
        ])

        # 批量检查
        func = await agent.mcp_client.get_callable_function(
            func_name="batch_check",
            wrap_tool_result=False
        )

        result = await func(checks=[
            {"user": "user:alice", "relation": "owner", "object": "document:doc1"},
            {"user": "user:bob", "relation": "viewer", "object": "document:doc1"},
            {"user": "user:charlie", "relation": "viewer", "object": "document:doc1"}
        ])

        if result.get("success"):
            print(f"✅ 批量检查成功: {result.get('total_checks')} 个")
            for r in result.get("results", []):
                status = "✅" if r.get("allowed") else "❌"
                print(f"   {status} {r.get('user')} - {r.get('relation')}")
            return True
        else:
            print("❌ 批量检查失败")
            return False
    except Exception as e:
        print(f"❌ 批量检查异常: {e}")
        return False


async def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("AgentScope MCP 集成测试")
    print("=" * 60)

    tests = [
        test_mcp_connection,
        test_check_permission,
        test_write_tuples,
        test_list_objects,
        test_batch_check
    ]

    results = []
    for test in tests:
        result = await test()
        results.append(result)

    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")
    print(f"失败: {total - passed}/{total}")

    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n⚠️ 部分测试失败")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
