"""
测试脚本

用于测试 FastAPI + OpenFGA 集成的各项功能
"""

import asyncio
import httpx
from auth import generate_test_token

# API 基础 URL
BASE_URL = "http://localhost:8000"


class APITester:
    """API 测试类"""

    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BASE_URL)
        self.tokens = {}

    async def close(self):
        """关闭客户端"""
        await self.client.aclose()

    def generate_tokens(self):
        """生成测试用户的 token"""
        users = [
            ("user_1", "alice@example.com", "Alice"),
            ("user_2", "bob@example.com", "Bob"),
            ("user_3", "charlie@example.com", "Charlie"),
        ]

        for user_id, email, name in users:
            token = generate_test_token(user_id, email)
            self.tokens[user_id] = {
                "token": token,
                "email": email,
                "name": name
            }

        print("✓ 已生成测试 Token")
        for user_id, data in self.tokens.items():
            print(f"  {user_id}: {data['email']}")

    async def test_health(self):
        """测试健康检查"""
        print("\n[测试] 健康检查")
        response = await self.client.get("/health")
        print(f"  状态码: {response.status_code}")
        print(f"  响应: {response.json()}")
        assert response.status_code == 200

    async def test_create_users(self):
        """测试创建用户"""
        print("\n[测试] 创建用户")

        for user_id, data in self.tokens.items():
            response = await self.client.post(
                "/api/users",
                json={
                    "email": data["email"],
                    "name": data["name"]
                }
            )
            print(f"  创建用户 {user_id}: {response.status_code}")

            if response.status_code == 200:
                print(f"    ✓ {response.json()}")
            else:
                print(f"    ✗ {response.json()}")

    async def test_create_document(self):
        """测试创建文档"""
        print("\n[测试] Alice 创建文档")

        token = self.tokens["user_1"]["token"]
        response = await self.client.post(
            "/api/documents",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Alice 的文档",
                "content": "这是 Alice 创建的文档内容"
            }
        )

        print(f"  状态码: {response.status_code}")
        if response.status_code == 200:
            doc = response.json()
            print(f"  ✓ 文档已创建: {doc['id']}")
            return doc["id"]
        else:
            print(f"  ✗ 创建失败: {response.json()}")
            return None

    async def test_get_document(self, doc_id: str, user_id: str):
        """测试获取文档"""
        print(f"\n[测试] {user_id} 查看文档 {doc_id}")

        token = self.tokens[user_id]["token"]
        response = await self.client.get(
            f"/api/documents/{doc_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        print(f"  状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✓ 查看成功")
        elif response.status_code == 403:
            print(f"  ✗ 权限被拒绝")
        else:
            print(f"  ✗ 错误: {response.json()}")

        return response.status_code == 200

    async def test_update_document(self, doc_id: str, user_id: str):
        """测试更新文档"""
        print(f"\n[测试] {user_id} 更新文档 {doc_id}")

        token = self.tokens[user_id]["token"]
        response = await self.client.put(
            f"/api/documents/{doc_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": f"由 {user_id} 更新的文档",
                "content": "更新后的内容"
            }
        )

        print(f"  状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✓ 更新成功")
        elif response.status_code == 403:
            print(f"  ✗ 权限被拒绝")
        else:
            print(f"  ✗ 错误: {response.json()}")

        return response.status_code == 200

    async def test_share_document(self, doc_id: str, owner_id: str, target_id: str, relation: str):
        """测试分享文档"""
        print(f"\n[测试] {owner_id} 将文档 {doc_id} 的 {relation} 权限分享给 {target_id}")

        token = self.tokens[owner_id]["token"]
        response = await self.client.post(
            f"/api/documents/{doc_id}/share",
            headers={"Authorization": f"Bearer {token}"},
            params={
                "target_user_id": target_id,
                "relation": relation
            }
        )

        print(f"  状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✓ 分享成功")
        else:
            print(f"  ✗ 分享失败: {response.json()}")

        return response.status_code == 200

    async def test_list_documents(self, user_id: str):
        """测试列出文档"""
        print(f"\n[测试] {user_id} 列出可访问的文档")

        token = self.tokens[user_id]["token"]
        response = await self.client.get(
            "/api/documents",
            headers={"Authorization": f"Bearer {token}"}
        )

        print(f"  状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ 共 {data['total']} 个文档")
            for doc in data["documents"]:
                print(f"    - {doc['id']}: {doc['title']}")
        else:
            print(f"  ✗ 错误: {response.json()}")

    async def test_delete_document(self, doc_id: str, user_id: str):
        """测试删除文档"""
        print(f"\n[测试] {user_id} 删除文档 {doc_id}")

        token = self.tokens[user_id]["token"]
        response = await self.client.delete(
            f"/api/documents/{doc_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        print(f"  状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✓ 删除成功")
        elif response.status_code == 403:
            print(f"  ✗ 权限被拒绝")
        else:
            print(f"  ✗ 错误: {response.json()}")

        return response.status_code == 200

    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("FastAPI + OpenFGA 集成测试")
        print("=" * 60)

        # 生成 token
        self.generate_tokens()

        # 测试健康检查
        await self.test_health()

        # 创建用户
        await self.test_create_users()

        # Alice 创建文档
        doc_id = await self.test_create_document()
        if not doc_id:
            print("\n✗ 文档创建失败，终止测试")
            return

        # Alice 查看自己的文档（应该成功）
        await self.test_get_document(doc_id, "user_1")

        # Bob 尝试查看文档（应该失败 - 没有权限）
        await self.test_get_document(doc_id, "user_2")

        # Alice 将 viewer 权限分享给 Bob
        await self.test_share_document(doc_id, "user_1", "user_2", "viewer")

        # Bob 再次查看文档（应该成功）
        await self.test_get_document(doc_id, "user_2")

        # Bob 尝试更新文档（应该失败 - 只有 viewer 权限）
        await self.test_update_document(doc_id, "user_2")

        # Alice 将 editor 权限分享给 Bob
        await self.test_share_document(doc_id, "user_1", "user_2", "editor")

        # Bob 再次尝试更新文档（应该成功）
        await self.test_update_document(doc_id, "user_2")

        # 列出各用户可访问的文档
        await self.test_list_documents("user_1")
        await self.test_list_documents("user_2")
        await self.test_list_documents("user_3")

        # Bob 尝试删除文档（应该失败 - 不是 owner）
        await self.test_delete_document(doc_id, "user_2")

        # Alice 删除文档（应该成功）
        await self.test_delete_document(doc_id, "user_1")

        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)


async def main():
    """主函数"""
    tester = APITester()

    try:
        await tester.run_all_tests()
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await tester.close()


if __name__ == "__main__":
    print("请确保:")
    print("1. OpenFGA 服务已启动（http://localhost:8080）")
    print("2. FastAPI 应用已启动（http://localhost:8000）")
    print("3. 已配置正确的 OPENFGA_STORE_ID")
    print()

    input("按 Enter 键开始测试...")

    asyncio.run(main())
