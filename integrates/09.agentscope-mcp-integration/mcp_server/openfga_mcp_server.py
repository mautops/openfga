#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenFGA MCP Server

这个 MCP 服务器将 OpenFGA 的权限管理功能暴露为 MCP 工具，
允许 AgentScope 等 AI Agent 框架通过 MCP 协议调用 OpenFGA。

主要功能：
- check_permission: 检查用户是否有权限
- write_tuples: 写入关系元组
- read_tuples: 读取关系元组
- delete_tuples: 删除关系元组
- list_objects: 列出用户有权限的对象
- batch_check: 批量检查权限
"""

import asyncio
import os
from typing import List, Dict, Any, Optional

from mcp.server.fastmcp import FastMCP
from openfga_sdk import OpenFgaClient, ClientConfiguration
from openfga_sdk.client.models import ClientTuple, ClientCheckRequest


# 初始化 FastMCP 服务器
mcp = FastMCP("OpenFGA Permission Service")


# 全局 OpenFGA 客户端
_openfga_client: Optional[OpenFgaClient] = None


async def get_openfga_client() -> OpenFgaClient:
    """获取或创建 OpenFGA 客户端"""
    global _openfga_client

    if _openfga_client is None:
        config = ClientConfiguration(
            api_url=os.getenv("OPENFGA_API_URL", "http://localhost:8080"),
            store_id=os.getenv("OPENFGA_STORE_ID"),
            authorization_model_id=os.getenv("OPENFGA_MODEL_ID"),
        )
        _openfga_client = OpenFgaClient(config)

    return _openfga_client


@mcp.tool()
async def check_permission(
    user: str,
    relation: str,
    object_type: str,
    object_id: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    检查用户是否对指定对象有特定权限

    Args:
        user: 用户标识，格式如 "user:alice"
        relation: 关系类型，如 "viewer", "editor", "owner"
        object_type: 对象类型，如 "document", "folder"
        object_id: 对象ID
        context: 可选的上下文信息，用于条件权限判断

    Returns:
        包含权限检查结果的字典

    Example:
        check_permission(
            user="user:alice",
            relation="viewer",
            object_type="document",
            object_id="doc1"
        )
    """
    client = await get_openfga_client()

    try:
        response = await client.check(
            ClientCheckRequest(
                user=user,
                relation=relation,
                object=f"{object_type}:{object_id}",
                context=context or {}
            )
        )

        return {
            "allowed": response.allowed,
            "user": user,
            "relation": relation,
            "object": f"{object_type}:{object_id}",
        }
    except Exception as e:
        return {
            "error": str(e),
            "allowed": False
        }


@mcp.tool()
async def write_tuples(
    tuples: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    写入关系元组到 OpenFGA

    Args:
        tuples: 关系元组列表，每个元组包含 user, relation, object

    Returns:
        写入结果

    Example:
        write_tuples([
            {"user": "user:alice", "relation": "owner", "object": "document:doc1"},
            {"user": "user:bob", "relation": "viewer", "object": "document:doc1"}
        ])
    """
    client = await get_openfga_client()

    try:
        client_tuples = [
            ClientTuple(
                user=t["user"],
                relation=t["relation"],
                object=t["object"]
            )
            for t in tuples
        ]

        await client.write(writes=client_tuples)

        return {
            "success": True,
            "tuples_written": len(tuples),
            "tuples": tuples
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
async def delete_tuples(
    tuples: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    删除关系元组

    Args:
        tuples: 要删除的关系元组列表

    Returns:
        删除结果

    Example:
        delete_tuples([
            {"user": "user:bob", "relation": "viewer", "object": "document:doc1"}
        ])
    """
    client = await get_openfga_client()

    try:
        client_tuples = [
            ClientTuple(
                user=t["user"],
                relation=t["relation"],
                object=t["object"]
            )
            for t in tuples
        ]

        await client.write(deletes=client_tuples)

        return {
            "success": True,
            "tuples_deleted": len(tuples),
            "tuples": tuples
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
async def list_objects(
    user: str,
    relation: str,
    object_type: str,
    max_results: int = 100
) -> Dict[str, Any]:
    """
    列出用户有权限访问的所有对象

    Args:
        user: 用户标识
        relation: 关系类型
        object_type: 对象类型
        max_results: 最大返回结果数

    Returns:
        用户有权限的对象列表

    Example:
        list_objects(
            user="user:alice",
            relation="viewer",
            object_type="document"
        )
    """
    client = await get_openfga_client()

    try:
        response = await client.list_objects(
            user=user,
            relation=relation,
            type=object_type
        )

        objects = response.objects[:max_results] if response.objects else []

        return {
            "success": True,
            "user": user,
            "relation": relation,
            "object_type": object_type,
            "objects": objects,
            "count": len(objects)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "objects": []
        }


@mcp.tool()
async def batch_check(
    checks: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    批量检查多个权限

    Args:
        checks: 权限检查列表，每个包含 user, relation, object

    Returns:
        批量检查结果

    Example:
        batch_check([
            {"user": "user:alice", "relation": "viewer", "object": "document:doc1"},
            {"user": "user:alice", "relation": "editor", "object": "document:doc1"}
        ])
    """
    client = await get_openfga_client()

    results = []
    for check in checks:
        try:
            response = await client.check(
                ClientCheckRequest(
                    user=check["user"],
                    relation=check["relation"],
                    object=check["object"]
                )
            )
            results.append({
                "user": check["user"],
                "relation": check["relation"],
                "object": check["object"],
                "allowed": response.allowed
            })
        except Exception as e:
            results.append({
                "user": check["user"],
                "relation": check["relation"],
                "object": check["object"],
                "allowed": False,
                "error": str(e)
            })

    return {
        "success": True,
        "total_checks": len(checks),
        "results": results
    }


if __name__ == "__main__":
    # 运行 MCP 服务器
    mcp.run(transport="stdio")
