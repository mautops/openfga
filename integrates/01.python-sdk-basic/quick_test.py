"""
快速测试脚本

用于快速验证 OpenFGA 连接和基本功能。
运行此脚本可以检查配置是否正确。

使用方法:
    python quick_test.py
"""

import asyncio
import sys
from client import create_client
from openfga_sdk.client.models import ClientTuple


async def test_connection():
    """测试连接"""
    print("=" * 60)
    print("OpenFGA 连接测试")
    print("=" * 60)

    try:
        async with create_client() as client:
            print("✓ 客户端初始化成功")
            print(f"  API URL: {client.api_url}")
            print(f"  Store ID: {client.store_id}")
            print(f"  认证方式: {client.auth_method}")
            return True
    except Exception as e:
        print(f"✗ 客户端初始化失败: {str(e)}")
        return False


async def test_read_models():
    """测试读取授权模型"""
    print("\n" + "=" * 60)
    print("测试读取授权模型")
    print("=" * 60)

    try:
        async with create_client() as client:
            result = await client.read_authorization_models()

            if result['success']:
                models = result['models']
                print(f"✓ 成功读取授权模型")
                print(f"  找到 {len(models)} 个模型")

                if models:
                    print("\n前 3 个模型:")
                    for i, model in enumerate(models[:3], 1):
                        model_id = model.id if hasattr(model, 'id') else 'N/A'
                        print(f"  {i}. Model ID: {model_id}")
                else:
                    print("\n  提示: Store 中还没有授权模型")
                    print("  请先创建授权模型后再进行其他操作")

                return True
            else:
                print(f"✗ 读取失败: {result['error']}")
                return False
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        return False


async def test_write_and_check():
    """测试写入和检查"""
    print("\n" + "=" * 60)
    print("测试写入和检查权限")
    print("=" * 60)

    try:
        async with create_client() as client:
            # 写入测试元组
            print("\n1. 写入测试元组...")
            writes = [
                ClientTuple(
                    user="user:test_user",
                    relation="viewer",
                    object="document:test_doc"
                ),
            ]

            write_result = await client.write_tuples(writes=writes)

            if write_result['success']:
                print("✓ 写入成功")
            else:
                print(f"✗ 写入失败: {write_result['error']}")
                return False

            # 检查权限
            print("\n2. 检查权限...")
            check_result = await client.check_permission(
                user="user:test_user",
                relation="viewer",
                object="document:test_doc"
            )

            if check_result['success']:
                allowed = check_result['allowed']
                print(f"✓ 检查成功")
                print(f"  结果: {'允许访问' if allowed else '拒绝访问'}")

                if allowed:
                    print("\n✓ 基本功能测试通过")
                else:
                    print("\n⚠ 权限检查返回拒绝，可能是授权模型配置问题")
            else:
                print(f"✗ 检查失败: {check_result['error']}")
                return False

            # 清理测试数据
            print("\n3. 清理测试数据...")
            delete_result = await client.write_tuples(deletes=writes)

            if delete_result['success']:
                print("✓ 清理成功")
            else:
                print(f"⚠ 清理失败: {delete_result['error']}")

            return True

    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        return False


async def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("OpenFGA Python SDK 快速测试")
    print("=" * 60)
    print()

    # 测试 1: 连接
    connection_ok = await test_connection()
    if not connection_ok:
        print("\n" + "=" * 60)
        print("测试失败: 无法连接到 OpenFGA 服务器")
        print("=" * 60)
        print("\n请检查:")
        print("1. OpenFGA 服务器是否正在运行")
        print("2. .env 文件配置是否正确")
        print("3. 网络连接是否正常")
        sys.exit(1)

    # 测试 2: 读取模型
    models_ok = await test_read_models()
    if not models_ok:
        print("\n" + "=" * 60)
        print("测试失败: 无法读取授权模型")
        print("=" * 60)
        sys.exit(1)

    # 测试 3: 写入和检查
    write_check_ok = await test_write_and_check()
    if not write_check_ok:
        print("\n" + "=" * 60)
        print("测试失败: 写入或检查操作失败")
        print("=" * 60)
        sys.exit(1)

    # 所有测试通过
    print("\n" + "=" * 60)
    print("✓ 所有测试通过！")
    print("=" * 60)
    print("\n你可以开始使用 OpenFGA Python SDK 了！")
    print("运行完整示例: python examples.py")
    print()


if __name__ == "__main__":
    asyncio.run(main())
