#!/usr/bin/env python3
"""
OpenFGA 设置脚本

帮助用户快速设置 OpenFGA Store 和 Authorization Model。
"""

import asyncio
import json
import os
import sys
from typing import Optional
import aiohttp
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class OpenFGASetup:
    """OpenFGA 设置助手"""

    def __init__(self, api_url: str):
        """初始化

        Args:
            api_url: OpenFGA API 地址
        """
        self.api_url = api_url.rstrip("/")

    async def create_store(self, store_name: str) -> Optional[str]:
        """创建 Store

        Args:
            store_name: Store 名称

        Returns:
            Optional[str]: Store ID，失败返回 None
        """
        url = f"{self.api_url}/stores"
        payload = {"name": store_name}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload) as response:
                    if response.status == 201:
                        data = await response.json()
                        store_id = data.get("id")
                        print(f"✅ Store 创建成功: {store_id}")
                        return store_id
                    else:
                        error = await response.text()
                        print(f"❌ 创建 Store 失败: {error}")
                        return None
            except Exception as e:
                print(f"❌ 创建 Store 时发生错误: {e}")
                return None

    async def upload_model(
        self,
        store_id: str,
        model_file: str
    ) -> Optional[str]:
        """上传授权模型

        Args:
            store_id: Store ID
            model_file: 模型文件路径

        Returns:
            Optional[str]: Model ID，失败返回 None
        """
        # 读取模型文件
        try:
            with open(model_file, "r", encoding="utf-8") as f:
                model_content = f.read()
        except Exception as e:
            print(f"❌ 读取模型文件失败: {e}")
            return None

        # 转换为 JSON 格式
        model_json = self._fga_to_json(model_content)

        url = f"{self.api_url}/stores/{store_id}/authorization-models"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=model_json) as response:
                    if response.status == 201:
                        data = await response.json()
                        model_id = data.get("authorization_model_id")
                        print(f"✅ 授权模型上传成功: {model_id}")
                        return model_id
                    else:
                        error = await response.text()
                        print(f"❌ 上传授权模型失败: {error}")
                        return None
            except Exception as e:
                print(f"❌ 上传授权模型时发生错误: {e}")
                return None

    def _fga_to_json(self, fga_content: str) -> dict:
        """将 FGA 格式转换为 JSON 格式

        Args:
            fga_content: FGA 格式的模型内容

        Returns:
            dict: JSON 格式的模型
        """
        # 这是一个简化的转换，实际应用中可能需要更复杂的解析
        # 这里我们直接返回一个预定义的 JSON 结构

        return {
            "schema_version": "1.1",
            "type_definitions": [
                {
                    "type": "user"
                },
                {
                    "type": "agent",
                    "relations": {
                        "owner": {
                            "this": {}
                        }
                    },
                    "metadata": {
                        "relations": {
                            "owner": {
                                "directly_related_user_types": [
                                    {"type": "user"}
                                ]
                            },
                            "can_act_as": {
                                "directly_related_user_types": [
                                    {"type": "user"}
                                ]
                            }
                        }
                    }
                },
                {
                    "type": "document",
                    "relations": {
                        "owner": {
                            "this": {}
                        },
                        "viewer": {
                            "union": {
                                "child": [
                                    {"this": {}},
                                    {"computedUserset": {"relation": "owner"}}
                                ]
                            }
                        },
                        "editor": {
                            "union": {
                                "child": [
                                    {"this": {}},
                                    {"computedUserset": {"relation": "owner"}}
                                ]
                            }
                        },
                        "can_read": {
                            "computedUserset": {"relation": "viewer"}
                        },
                        "can_write": {
                            "computedUserset": {"relation": "editor"}
                        }
                    },
                    "metadata": {
                        "relations": {
                            "owner": {
                                "directly_related_user_types": [
                                    {"type": "user"}
                                ]
                            },
                            "viewer": {
                                "directly_related_user_types": [
                                    {"type": "user"},
                                    {"type": "agent"}
                                ]
                            },
                            "editor": {
                                "directly_related_user_types": [
                                    {"type": "user"}
                                ]
                            }
                        }
                    }
                },
                {
                    "type": "database",
                    "relations": {
                        "owner": {
                            "this": {}
                        },
                        "reader": {
                            "union": {
                                "child": [
                                    {"this": {}},
                                    {"computedUserset": {"relation": "owner"}}
                                ]
                            }
                        },
                        "admin": {
                            "union": {
                                "child": [
                                    {"this": {}},
                                    {"computedUserset": {"relation": "owner"}}
                                ]
                            }
                        },
                        "can_query": {
                            "computedUserset": {"relation": "reader"}
                        },
                        "can_manage": {
                            "computedUserset": {"relation": "admin"}
                        }
                    },
                    "metadata": {
                        "relations": {
                            "owner": {
                                "directly_related_user_types": [
                                    {"type": "user"}
                                ]
                            },
                            "reader": {
                                "directly_related_user_types": [
                                    {"type": "user"},
                                    {"type": "agent"}
                                ]
                            },
                            "admin": {
                                "directly_related_user_types": [
                                    {"type": "user"}
                                ]
                            }
                        }
                    }
                },
                {
                    "type": "sensitive_operation",
                    "relations": {
                        "owner": {
                            "this": {}
                        },
                        "approver": {
                            "this": {}
                        },
                        "can_execute": {
                            "computedUserset": {"relation": "approver"}
                        }
                    },
                    "metadata": {
                        "relations": {
                            "owner": {
                                "directly_related_user_types": [
                                    {"type": "user"}
                                ]
                            },
                            "approver": {
                                "directly_related_user_types": [
                                    {"type": "user"}
                                ]
                            }
                        }
                    }
                }
            ]
        }

    def save_env_file(self, store_id: str, model_id: str):
        """保存环境变量到 .env 文件

        Args:
            store_id: Store ID
            model_id: Model ID
        """
        env_content = f"""# OpenFGA 配置
OPENFGA_API_URL={self.api_url}
OPENFGA_STORE_ID={store_id}
OPENFGA_MODEL_ID={model_id}

# OpenAI 配置（用于 LangChain Agent）
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4

# 应用配置
LOG_LEVEL=INFO
ENABLE_AUDIT_LOG=true
"""

        try:
            with open(".env", "w", encoding="utf-8") as f:
                f.write(env_content)
            print(f"✅ 环境变量已保存到 .env 文件")
        except Exception as e:
            print(f"❌ 保存环境变量失败: {e}")


async def main():
    """主函数"""
    print("=" * 80)
    print("OpenFGA 设置助手")
    print("=" * 80)

    # 获取 API 地址
    api_url = os.getenv("OPENFGA_API_URL", "http://localhost:8080")
    print(f"\nOpenFGA API 地址: {api_url}")

    # 创建设置助手
    setup = OpenFGASetup(api_url)

    # 创建 Store
    print("\n步骤 1: 创建 Store")
    store_name = "langchain-demo"
    store_id = await setup.create_store(store_name)

    if not store_id:
        print("\n❌ 设置失败：无法创建 Store")
        sys.exit(1)

    # 上传授权模型
    print("\n步骤 2: 上传授权模型")
    model_file = "authorization_model.fga"
    model_id = await setup.upload_model(store_id, model_file)

    if not model_id:
        print("\n❌ 设置失败：无法上传授权模型")
        sys.exit(1)

    # 保存环境变量
    print("\n步骤 3: 保存环境变量")
    setup.save_env_file(store_id, model_id)

    print("\n" + "=" * 80)
    print("✅ 设置完成！")
    print("=" * 80)
    print("\n下一步:")
    print("1. 编辑 .env 文件，填入你的 OPENAI_API_KEY")
    print("2. 运行示例: python example_agent.py")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
