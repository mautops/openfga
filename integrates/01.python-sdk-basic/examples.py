"""
OpenFGA Python SDK 完整使用示例

本文件展示了 OpenFGA Python SDK 的各种使用场景，包括：
- 写入和删除关系元组
- 权限检查
- 批量权限检查
- 列出对象和用户
- 使用上下文元组和条件

作者: OpenFGA 集成示例
日期: 2026-02-05
"""

import asyncio
from typing import List
from client import create_client
from openfga_sdk.client.models import ClientTuple, ClientCheckRequest
from openfga_sdk.models import RelationshipCondition


async def example_1_write_tuples():
    """
    示例 1: 写入关系元组

    演示如何创建用户与对象之间的关系。
    """
    print("\n" + "=" * 60)
    print("示例 1: 写入关系元组")
    print("=" * 60)

    async with create_client() as client:
        # 创建多个关系元组
        writes = [
            # Anne 是 document:budget 的查看者
            ClientTuple(
                user="user:anne",
                relation="viewer",
                object="document:budget"
            ),
            # Bob 是 document:budget 的编辑者
            ClientTuple(
                user="user:bob",
                relation="editor",
                object="document:budget"
            ),
            # Charlie 是 document:roadmap 的所有者
            ClientTuple(
                user="user:charlie",
                relation="owner",
                object="document:roadmap"
            ),
        ]

        result = await client.write_tuples(writes=writes)

        if result['success']:
            print("✓ 成功写入关系元组")
            print(f"  写入了 {len(writes)} 个元组")
        else:
            print(f"✗ 写入失败: {result['error']}")


async def example_2_write_with_condition():
    """
    示例 2: 写入带条件的关系元组

    演示如何创建带有条件的关系，条件可以基于上下文数据进行评估。
    """
    print("\n" + "=" * 60)
    print("示例 2: 写入带条件的关系元组")
    print("=" * 60)

    async with create_client() as client:
        # 创建带条件的元组
        writes = [
            ClientTuple(
                user="user:david",
                relation="viewer",
                object="document:budget",
                # 只有当 ViewCount < 200 时才允许访问
                condition=RelationshipCondition(
                    name='ViewCountLessThan200',
                    context={
                        'Name': 'Budget',
                        'Type': 'Document',
                    }
                )
            ),
        ]

        result = await client.write_tuples(writes=writes)

        if result['success']:
            print("✓ 成功写入带条件的关系元组")
            print("  条件: ViewCountLessThan200")
        else:
            print(f"✗ 写入失败: {result['error']}")


async def example_3_delete_tuples():
    """
    示例 3: 删除关系元组

    演示如何删除已存在的关系。
    """
    print("\n" + "=" * 60)
    print("示例 3: 删除关系元组")
    print("=" * 60)

    async with create_client() as client:
        # 要删除的元组
        deletes = [
            ClientTuple(
                user="user:anne",
                relation="viewer",
                object="document:budget"
            ),
        ]

        result = await client.write_tuples(deletes=deletes)

        if result['success']:
            print("✓ 成功删除关系元组")
            print(f"  删除了 {len(deletes)} 个元组")
        else:
            print(f"✗ 删除失败: {result['error']}")


async def example_4_write_and_delete():
    """
    示例 4: 同时写入和删除元组（事务模式）

    演示如何在一个事务中同时执行写入和删除操作。
    """
    print("\n" + "=" * 60)
    print("示例 4: 事务模式 - 同时写入和删除")
    print("=" * 60)

    async with create_client() as client:
        writes = [
            # 添加 Bob 作为 viewer
            ClientTuple(
                user="user:bob",
                relation="viewer",
                object="document:roadmap"
            ),
        ]

        deletes = [
            # 移除 Bob 的 editor 权限
            ClientTuple(
                user="user:bob",
                relation="editor",
                object="document:budget"
            ),
        ]

        result = await client.write_tuples(writes=writes, deletes=deletes)

        if result['success']:
            print("✓ 事务执行成功")
            print(f"  写入: {len(writes)} 个元组")
            print(f"  删除: {len(deletes)} 个元组")
        else:
            print(f"✗ 事务失败: {result['error']}")


async def example_5_check_permission():
    """
    示例 5: 检查权限

    演示如何检查用户是否有权限访问特定对象。
    """
    print("\n" + "=" * 60)
    print("示例 5: 检查权限")
    print("=" * 60)

    async with create_client() as client:
        # 检查 Bob 是否可以查看 document:budget
        result = await client.check_permission(
            user="user:bob",
            relation="viewer",
            object="document:budget"
        )

        if result['success']:
            allowed = result['allowed']
            print(f"✓ 权限检查完成")
            print(f"  用户: user:bob")
            print(f"  关系: viewer")
            print(f"  对象: document:budget")
            print(f"  结果: {'✓ 允许' if allowed else '✗ 拒绝'}")
        else:
            print(f"✗ 检查失败: {result['error']}")


async def example_6_check_with_contextual_tuples():
    """
    示例 6: 使用上下文元组检查权限

    演示如何使用临时的上下文元组进行权限检查，而不实际写入数据库。
    """
    print("\n" + "=" * 60)
    print("示例 6: 使用上下文元组检查权限")
    print("=" * 60)

    async with create_client() as client:
        # 临时授予 Eve 编辑权限进行检查
        contextual_tuples = [
            ClientTuple(
                user="user:eve",
                relation="editor",
                object="document:budget"
            ),
        ]

        result = await client.check_permission(
            user="user:eve",
            relation="editor",
            object="document:budget",
            contextual_tuples=contextual_tuples
        )

        if result['success']:
            allowed = result['allowed']
            print(f"✓ 上下文权限检查完成")
            print(f"  使用了 {len(contextual_tuples)} 个上下文元组")
            print(f"  结果: {'✓ 允许' if allowed else '✗ 拒绝'}")
            print(f"  注意: 上下文元组不会被持久化到数据库")
        else:
            print(f"✗ 检查失败: {result['error']}")


async def example_7_check_with_context():
    """
    示例 7: 使用上下文数据检查权限

    演示如何传递上下文数据用于条件评估。
    """
    print("\n" + "=" * 60)
    print("示例 7: 使用上下文数据检查权限")
    print("=" * 60)

    async with create_client() as client:
        # 传递上下文数据用于条件评估
        context = {
            'ViewCount': 150,  # 当前查看次数
            'Name': 'Budget',
            'Type': 'Document'
        }

        result = await client.check_permission(
            user="user:david",
            relation="viewer",
            object="document:budget",
            context=context
        )

        if result['success']:
            allowed = result['allowed']
            print(f"✓ 条件权限检查完成")
            print(f"  上下文: ViewCount={context['ViewCount']}")
            print(f"  结果: {'✓ 允许' if allowed else '✗ 拒绝'}")
        else:
            print(f"✗ 检查失败: {result['error']}")


async def example_8_batch_check():
    """
    示例 8: 批量检查权限

    演示如何在一次请求中检查多个权限，提高性能。
    """
    print("\n" + "=" * 60)
    print("示例 8: 批量检查权限")
    print("=" * 60)

    async with create_client() as client:
        # 创建多个检查请求
        checks = [
            ClientCheckRequest(
                user="user:bob",
                relation="viewer",
                object="document:budget"
            ),
            ClientCheckRequest(
                user="user:bob",
                relation="editor",
                object="document:budget"
            ),
            ClientCheckRequest(
                user="user:charlie",
                relation="owner",
                object="document:roadmap"
            ),
            ClientCheckRequest(
                user="user:anne",
                relation="viewer",
                object="document:roadmap"
            ),
        ]

        result = await client.batch_check(checks)

        if result['success']:
            print(f"✓ 批量检查完成，共 {len(checks)} 个检查")
            print("\n检查结果:")
            for item in result['results']:
                status = '✓ 允许' if item['allowed'] else '✗ 拒绝'
                print(f"  {item['user']} -> {item['relation']} -> {item['object']}: {status}")
        else:
            print(f"✗ 批量检查失败: {result['error']}")


async def example_9_batch_check_with_context():
    """
    示例 9: 批量检查权限（带上下文元组）

    演示如何在批量检查中使用上下文元组。
    """
    print("\n" + "=" * 60)
    print("示例 9: 批量检查权限（带上下文元组）")
    print("=" * 60)

    async with create_client() as client:
        # 创建带上下文元组的检查请求
        checks = [
            ClientCheckRequest(
                user="user:frank",
                relation="viewer",
                object="document:budget",
                contextual_tuples=[
                    ClientTuple(
                        user="user:frank",
                        relation="editor",
                        object="document:budget"
                    ),
                ]
            ),
            ClientCheckRequest(
                user="user:frank",
                relation="editor",
                object="document:budget",
                contextual_tuples=[
                    ClientTuple(
                        user="user:frank",
                        relation="editor",
                        object="document:budget"
                    ),
                ]
            ),
        ]

        result = await client.batch_check(checks)

        if result['success']:
            print(f"✓ 批量检查完成（使用上下文元组）")
            print("\n检查结果:")
            for item in result['results']:
                status = '✓ 允许' if item['allowed'] else '✗ 拒绝'
                print(f"  {item['user']} -> {item['relation']} -> {item['object']}: {status}")
        else:
            print(f"✗ 批量检查失败: {result['error']}")


async def example_10_list_objects():
    """
    示例 10: 列出用户可访问的对象

    演示如何查询用户有权限访问的所有对象。
    """
    print("\n" + "=" * 60)
    print("示例 10: 列出用户可访问的对象")
    print("=" * 60)

    async with create_client() as client:
        # 列出 Bob 可以查看的所有文档
        result = await client.list_objects(
            user="user:bob",
            relation="viewer",
            type="document"
        )

        if result['success']:
            objects = result['objects']
            print(f"✓ 查询完成")
            print(f"  用户: user:bob")
            print(f"  关系: viewer")
            print(f"  对象类型: document")
            print(f"  找到 {len(objects)} 个对象:")
            for obj in objects:
                print(f"    - {obj}")
        else:
            print(f"✗ 查询失败: {result['error']}")


async def example_11_list_objects_with_context():
    """
    示例 11: 列出对象（带上下文元组）

    演示如何使用上下文元组来列出对象。
    """
    print("\n" + "=" * 60)
    print("示例 11: 列出对象（带上下文元组）")
    print("=" * 60)

    async with create_client() as client:
        # 使用上下文元组临时授权
        contextual_tuples = [
            ClientTuple(
                user="user:grace",
                relation="viewer",
                object="document:roadmap"
            ),
        ]

        result = await client.list_objects(
            user="user:grace",
            relation="viewer",
            type="document",
            contextual_tuples=contextual_tuples
        )

        if result['success']:
            objects = result['objects']
            print(f"✓ 查询完成（使用上下文元组）")
            print(f"  找到 {len(objects)} 个对象:")
            for obj in objects:
                print(f"    - {obj}")
        else:
            print(f"✗ 查询失败: {result['error']}")


async def example_12_list_users():
    """
    示例 12: 列出有权限访问对象的用户

    演示如何查询有权限访问特定对象的所有用户。
    """
    print("\n" + "=" * 60)
    print("示例 12: 列出有权限访问对象的用户")
    print("=" * 60)

    async with create_client() as client:
        # 列出所有可以查看 document:budget 的用户
        result = await client.list_users(
            object="document:budget",
            relation="viewer",
            user_filters=[
                {"type": "user"}  # 只返回用户类型
            ]
        )

        if result['success']:
            users = result['users']
            print(f"✓ 查询完成")
            print(f"  对象: document:budget")
            print(f"  关系: viewer")
            print(f"  找到 {len(users)} 个用户:")
            for user in users:
                print(f"    - {user}")
        else:
            print(f"✗ 查询失败: {result['error']}")


async def example_13_read_models():
    """
    示例 13: 读取授权模型

    演示如何读取 Store 中的所有授权模型。
    """
    print("\n" + "=" * 60)
    print("示例 13: 读取授权模型")
    print("=" * 60)

    async with create_client() as client:
        result = await client.read_authorization_models()

        if result['success']:
            models = result['models']
            print(f"✓ 查询完成")
            print(f"  找到 {len(models)} 个授权模型")
            for model in models[:3]:  # 只显示前 3 个
                model_id = model.id if hasattr(model, 'id') else 'N/A'
                print(f"    - Model ID: {model_id}")
        else:
            print(f"✗ 查询失败: {result['error']}")


async def example_14_error_handling():
    """
    示例 14: 错误处理

    演示如何处理各种错误情况。
    """
    print("\n" + "=" * 60)
    print("示例 14: 错误处理")
    print("=" * 60)

    async with create_client() as client:
        # 尝试检查一个不存在的对象
        result = await client.check_permission(
            user="user:nonexistent",
            relation="viewer",
            object="document:nonexistent"
        )

        if result['success']:
            print(f"✓ 检查完成: {'允许' if result['allowed'] else '拒绝'}")
        else:
            print(f"✗ 检查失败")
            print(f"  错误信息: {result['error']}")
            if 'status' in result:
                print(f"  HTTP 状态码: {result['status']}")


async def run_all_examples():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("OpenFGA Python SDK 完整示例")
    print("=" * 60)

    examples = [
        example_1_write_tuples,
        example_2_write_with_condition,
        example_3_delete_tuples,
        example_4_write_and_delete,
        example_5_check_permission,
        example_6_check_with_contextual_tuples,
        example_7_check_with_context,
        example_8_batch_check,
        example_9_batch_check_with_context,
        example_10_list_objects,
        example_11_list_objects_with_context,
        example_12_list_users,
        example_13_read_models,
        example_14_error_handling,
    ]

    for example in examples:
        try:
            await example()
        except Exception as e:
            print(f"\n✗ 示例执行出错: {example.__name__}")
            print(f"  错误: {str(e)}")

    print("\n" + "=" * 60)
    print("所有示例执行完成")
    print("=" * 60)


async def main():
    """主函数"""
    # 可以选择运行所有示例或单个示例
    await run_all_examples()

    # 或者运行单个示例:
    # await example_1_write_tuples()
    # await example_5_check_permission()
    # await example_8_batch_check()


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())
