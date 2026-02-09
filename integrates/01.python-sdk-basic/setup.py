#!/usr/bin/env python3
"""
OpenFGA 环境设置脚本

此脚本帮助你快速设置 OpenFGA 开发环境，包括：
1. 创建 Store
2. 上传授权模型
3. 生成 .env 配置文件

使用方法:
    python setup.py --api-url http://localhost:8080
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

try:
    import aiohttp
except ImportError:
    print("错误: 需要安装 aiohttp")
    print("运行: pip install aiohttp")
    sys.exit(1)


async def create_store(api_url: str, store_name: str) -> dict:
    """创建 Store"""
    print(f"\n创建 Store: {store_name}")

    async with aiohttp.ClientSession() as session:
        url = f"{api_url}/stores"
        payload = {"name": store_name}

        try:
            async with session.post(url, json=payload) as response:
                if response.status == 201:
                    data = await response.json()
                    store_id = data.get('id')
                    print(f"✓ Store 创建成功")
                    print(f"  Store ID: {store_id}")
                    return {'success': True, 'store_id': store_id}
                else:
                    error = await response.text()
                    print(f"✗ Store 创建失败: {error}")
                    return {'success': False, 'error': error}
        except Exception as e:
            print(f"✗ 请求失败: {str(e)}")
            return {'success': False, 'error': str(e)}


async def create_authorization_model(api_url: str, store_id: str, model_file: str) -> dict:
    """创建授权模型"""
    print(f"\n上传授权模型: {model_file}")

    # 读取模型文件
    try:
        with open(model_file, 'r', encoding='utf-8') as f:
            model_data = json.load(f)
    except FileNotFoundError:
        print(f"✗ 模型文件不存在: {model_file}")
        return {'success': False, 'error': 'File not found'}
    except json.JSONDecodeError as e:
        print(f"✗ 模型文件格式错误: {str(e)}")
        return {'success': False, 'error': str(e)}

    async with aiohttp.ClientSession() as session:
        url = f"{api_url}/stores/{store_id}/authorization-models"

        try:
            async with session.post(url, json=model_data) as response:
                if response.status == 201:
                    data = await response.json()
                    model_id = data.get('authorization_model_id')
                    print(f"✓ 授权模型创建成功")
                    print(f"  Model ID: {model_id}")
                    return {'success': True, 'model_id': model_id}
                else:
                    error = await response.text()
                    print(f"✗ 授权模型创建失败: {error}")
                    return {'success': False, 'error': error}
        except Exception as e:
            print(f"✗ 请求失败: {str(e)}")
            return {'success': False, 'error': str(e)}


def create_env_file(api_url: str, store_id: str, model_id: str, env_file: str = '.env'):
    """创建 .env 文件"""
    print(f"\n创建配置文件: {env_file}")

    env_content = f"""# OpenFGA 服务器配置
FGA_API_URL={api_url}
FGA_STORE_ID={store_id}
FGA_MODEL_ID={model_id}

# 认证方式 1: API Token（推荐用于开发环境）
# FGA_API_TOKEN=your_api_token_here

# 认证方式 2: Client Credentials（推荐用于生产环境）
# FGA_API_TOKEN_ISSUER=https://your-auth-server.com
# FGA_API_AUDIENCE=https://api.fga.example
# FGA_CLIENT_ID=your_client_id
# FGA_CLIENT_SECRET=your_client_secret

# 认证方式选择: api_token 或 client_credentials
# 注意: 本地开发环境通常不需要认证，可以注释掉 FGA_AUTH_METHOD
# FGA_AUTH_METHOD=api_token
"""

    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print(f"✓ 配置文件创建成功: {env_file}")
        return True
    except Exception as e:
        print(f"✗ 配置文件创建失败: {str(e)}")
        return False


async def check_server(api_url: str) -> bool:
    """检查服务器是否可访问"""
    print(f"检查 OpenFGA 服务器: {api_url}")

    async with aiohttp.ClientSession() as session:
        try:
            # 尝试访问健康检查端点
            async with session.get(f"{api_url}/healthz", timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    print("✓ 服务器连接成功")
                    return True
                else:
                    print(f"⚠ 服务器响应异常: {response.status}")
                    return False
        except aiohttp.ClientConnectorError:
            print(f"✗ 无法连接到服务器: {api_url}")
            print("\n请确保 OpenFGA 服务器正在运行:")
            print("  docker run -p 8080:8080 openfga/openfga run")
            return False
        except asyncio.TimeoutError:
            print(f"✗ 连接超时: {api_url}")
            return False
        except Exception as e:
            print(f"✗ 连接失败: {str(e)}")
            return False


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='OpenFGA 环境设置脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用默认配置
  python setup.py

  # 指定 API URL
  python setup.py --api-url http://localhost:8080

  # 指定 Store 名称
  python setup.py --store-name my-app

  # 使用自定义授权模型
  python setup.py --model-file my_model.json
        """
    )

    parser.add_argument(
        '--api-url',
        default='http://localhost:8080',
        help='OpenFGA API URL (默认: http://localhost:8080)'
    )
    parser.add_argument(
        '--store-name',
        default='python-sdk-demo',
        help='Store 名称 (默认: python-sdk-demo)'
    )
    parser.add_argument(
        '--model-file',
        default='authorization_model.json',
        help='授权模型文件路径 (默认: authorization_model.json)'
    )
    parser.add_argument(
        '--env-file',
        default='.env',
        help='输出的环境变量文件 (默认: .env)'
    )
    parser.add_argument(
        '--skip-model',
        action='store_true',
        help='跳过创建授权模型'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("OpenFGA 环境设置")
    print("=" * 60)

    # 1. 检查服务器
    server_ok = await check_server(args.api_url)
    if not server_ok:
        sys.exit(1)

    # 2. 创建 Store
    store_result = await create_store(args.api_url, args.store_name)
    if not store_result['success']:
        print("\n设置失败: 无法创建 Store")
        sys.exit(1)

    store_id = store_result['store_id']
    model_id = None

    # 3. 创建授权模型
    if not args.skip_model:
        model_result = await create_authorization_model(
            args.api_url,
            store_id,
            args.model_file
        )
        if model_result['success']:
            model_id = model_result['model_id']
        else:
            print("\n⚠ 授权模型创建失败，但 Store 已创建")
            print("你可以稍后手动创建授权模型")
    else:
        print("\n跳过创建授权模型")

    # 4. 创建 .env 文件
    if model_id:
        env_ok = create_env_file(args.api_url, store_id, model_id, args.env_file)
        if not env_ok:
            print("\n⚠ 配置文件创建失败，但 Store 和模型已创建")
    else:
        print("\n⚠ 未创建配置文件（缺少 Model ID）")

    # 5. 完成
    print("\n" + "=" * 60)
    print("✓ 设置完成！")
    print("=" * 60)
    print("\n下一步:")
    print("1. 检查 .env 文件配置")
    print("2. 运行快速测试: python quick_test.py")
    print("3. 运行完整示例: python examples.py")
    print()


if __name__ == "__main__":
    asyncio.run(main())
