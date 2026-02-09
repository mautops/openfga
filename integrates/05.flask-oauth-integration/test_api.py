"""
API 测试脚本

测试 Flask + OAuth + OpenFGA 集成示例的各个功能
"""

import requests
import json
from typing import Optional


class FlaskOAuthTester:
    """Flask OAuth API 测试器"""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.user_id = None

    def test_health(self):
        """测试健康检查"""
        print("\n=== 测试健康检查 ===")
        response = self.session.get(f"{self.base_url}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        assert response.status_code == 200

    def test_index(self):
        """测试首页"""
        print("\n=== 测试首页 ===")
        response = self.session.get(f"{self.base_url}/")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        assert response.status_code == 200

    def simulate_login(self, user_id: str = "test-user-123"):
        """
        模拟登录（直接设置 session）

        注意：这是测试用的简化方法，生产环境需要真实的 OAuth 流程
        """
        print(f"\n=== 模拟登录 (user_id: {user_id}) ===")
        self.user_id = user_id

        # 在实际测试中，你需要：
        # 1. 访问 /auth/login?provider=google
        # 2. 完成 OAuth 流程
        # 3. 获取 session cookie

        # 这里我们直接设置 session（需要修改 app.py 添加测试端点）
        print("提示: 需要手动完成 OAuth 登录流程")
        print(f"访问: {self.base_url}/auth/login?provider=google")

    def test_create_document(self, title: str = "测试文档", content: str = "这是测试内容") -> Optional[str]:
        """测试创建文档"""
        print("\n=== 测试创建文档 ===")

        data = {
            "title": title,
            "content": content
        }

        response = self.session.post(
            f"{self.base_url}/api/documents",
            json=data
        )

        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        if response.status_code == 201:
            document_id = response.json()['document']['id']
            print(f"✓ 文档创建成功，ID: {document_id}")
            return document_id
        else:
            print(f"✗ 文档创建失败")
            return None

    def test_list_documents(self):
        """测试列出文档"""
        print("\n=== 测试列出文档 ===")

        response = self.session.get(f"{self.base_url}/api/documents")

        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        if response.status_code == 200:
            total = response.json()['total']
            print(f"✓ 找到 {total} 个文档")
        else:
            print(f"✗ 列出文档失败")

    def test_get_document(self, document_id: str):
        """测试获取文档"""
        print(f"\n=== 测试获取文档 (ID: {document_id}) ===")

        response = self.session.get(f"{self.base_url}/api/documents/{document_id}")

        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        if response.status_code == 200:
            print(f"✓ 文档获取成功")
        elif response.status_code == 403:
            print(f"✗ 权限不足")
        elif response.status_code == 404:
            print(f"✗ 文档不存在")
        else:
            print(f"✗ 获取文档失败")

    def test_update_document(self, document_id: str, title: str = "更新的标题", content: str = "更新的内容"):
        """测试更新文档"""
        print(f"\n=== 测试更新文档 (ID: {document_id}) ===")

        data = {
            "title": title,
            "content": content
        }

        response = self.session.put(
            f"{self.base_url}/api/documents/{document_id}",
            json=data
        )

        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        if response.status_code == 200:
            print(f"✓ 文档更新成功")
        elif response.status_code == 403:
            print(f"✗ 权限不足（需要 editor 权限）")
        else:
            print(f"✗ 更新文档失败")

    def test_share_document(self, document_id: str, target_user_id: str, permission: str = "viewer"):
        """测试分享文档"""
        print(f"\n=== 测试分享文档 (ID: {document_id}) ===")

        data = {
            "user_id": target_user_id,
            "permission": permission
        }

        response = self.session.post(
            f"{self.base_url}/api/documents/{document_id}/share",
            json=data
        )

        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        if response.status_code == 201:
            print(f"✓ 文档分享成功")
        elif response.status_code == 403:
            print(f"✗ 权限不足（需要 owner 权限）")
        else:
            print(f"✗ 分享文档失败")

    def test_list_shares(self, document_id: str):
        """测试列出分享记录"""
        print(f"\n=== 测试列出分享记录 (ID: {document_id}) ===")

        response = self.session.get(f"{self.base_url}/api/documents/{document_id}/shares")

        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        if response.status_code == 200:
            total = response.json()['total']
            print(f"✓ 找到 {total} 条分享记录")
        else:
            print(f"✗ 列出分享记录失败")

    def test_unshare_document(self, document_id: str, target_user_id: str):
        """测试取消分享"""
        print(f"\n=== 测试取消分享 (ID: {document_id}) ===")

        response = self.session.delete(
            f"{self.base_url}/api/documents/{document_id}/share/{target_user_id}"
        )

        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        if response.status_code == 200:
            print(f"✓ 取消分享成功")
        else:
            print(f"✗ 取消分享失败")

    def test_delete_document(self, document_id: str):
        """测试删除文档"""
        print(f"\n=== 测试删除文档 (ID: {document_id}) ===")

        response = self.session.delete(f"{self.base_url}/api/documents/{document_id}")

        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        if response.status_code == 200:
            print(f"✓ 文档删除成功")
        elif response.status_code == 403:
            print(f"✗ 权限不足（需要 owner 权限）")
        else:
            print(f"✗ 删除文档失败")

    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("Flask + OAuth + OpenFGA 集成测试")
        print("=" * 60)

        # 基础测试
        self.test_health()
        self.test_index()

        print("\n" + "=" * 60)
        print("注意: 以下测试需要先完成 OAuth 登录")
        print("请访问: http://localhost:5000/auth/login?provider=google")
        print("登录后，按 Enter 继续...")
        print("=" * 60)
        input()

        # 文档操作测试
        self.test_list_documents()

        document_id = self.test_create_document(
            title="测试文档",
            content="这是一个测试文档的内容"
        )

        if document_id:
            self.test_get_document(document_id)
            self.test_update_document(document_id, "更新后的标题", "更新后的内容")
            self.test_share_document(document_id, "another-user-456", "viewer")
            self.test_list_shares(document_id)
            self.test_unshare_document(document_id, "another-user-456")
            # self.test_delete_document(document_id)  # 取消注释以测试删除

        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)


def main():
    """主函数"""
    import sys

    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"

    tester = FlaskOAuthTester(base_url)
    tester.run_all_tests()


if __name__ == "__main__":
    main()
