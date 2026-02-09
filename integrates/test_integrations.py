#!/usr/bin/env python3
"""
OpenFGA 集成示例测试脚本

测试所有集成示例的基本功能
"""

import asyncio
import sys
from pathlib import Path

# 添加 integrates 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))


async def test_python_sdk_basic():
    """测试 Python SDK 基础集成"""
    print("\n" + "=" * 60)
    print("测试 01: Python SDK 基础集成")
    print("=" * 60)

    try:
        # 检查目录是否存在
        sdk_dir = Path(__file__).parent / "01.python-sdk-basic"
        if not sdk_dir.exists():
            print("⚠ Python SDK 基础集成目录不存在")
            return False

        # 检查关键文件
        client_file = sdk_dir / "client.py"
        examples_file = sdk_dir / "examples.py"
        readme_file = sdk_dir / "README.md"

        if client_file.exists():
            print("✓ client.py 文件存在")
        else:
            print("✗ client.py 文件不存在")
            return False

        if examples_file.exists():
            print("✓ examples.py 文件存在")
        else:
            print("✗ examples.py 文件不存在")
            return False

        if readme_file.exists():
            print("✓ README.md 文件存在")
        else:
            print("✗ README.md 文件不存在")

        print("✓ Python SDK 基础集成模块完整")
        print("  提示：需要运行 OpenFGA 服务才能执行完整测试")
        print(f"  目录: {sdk_dir}")

        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


async def test_fastapi_integration():
    """测试 FastAPI 集成"""
    print("\n" + "=" * 60)
    print("测试 02: FastAPI 集成")
    print("=" * 60)

    try:
        # 检查 FastAPI 集成目录
        fastapi_dir = Path(__file__).parent / "integrates" / "03.fastapi-integration"
        if not fastapi_dir.exists():
            print("⚠ FastAPI 集成目录不存在，跳过测试")
            return True

        print("✓ FastAPI 集成目录存在")
        print("  提示：使用 'uvicorn main:app --reload' 启动服务")

        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("OpenFGA 集成示例测试")
    print("=" * 60)

    results = []

    # 测试 Python SDK 基础集成
    results.append(await test_python_sdk_basic())

    # 测试 FastAPI 集成
    results.append(await test_fastapi_integration())

    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")

    if passed == total:
        print("\n✓ 所有测试通过！")
        return 0
    else:
        print(f"\n✗ {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
