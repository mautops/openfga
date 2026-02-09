"""
单元测试

测试权限检查和工具功能。
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

from agent_permissions import OpenFGAPermissionChecker, PermissionCache
from tools import (
    ProtectedDocumentReadTool,
    ProtectedDocumentWriteTool,
    ProtectedDatabaseQueryTool,
    ProtectedSensitiveOperationTool
)


@pytest.fixture
def mock_permission_checker():
    """创建模拟的权限检查器"""
    checker = Mock(spec=OpenFGAPermissionChecker)
    checker.check_permission = AsyncMock()
    return checker


@pytest.fixture
def documents():
    """测试文档"""
    return {
        "doc1": "测试文档 1",
        "doc2": "测试文档 2",
        "doc3": "测试文档 3"
    }


class TestPermissionCache:
    """测试权限缓存"""

    def test_cache_set_and_get(self):
        """测试缓存设置和获取"""
        cache = PermissionCache(ttl_seconds=60)
        key = PermissionCache.make_key("agent:test", "viewer", "document:doc1")

        # 设置缓存
        cache.set(key, True)

        # 获取缓存
        result = cache.get(key)
        assert result is True

    def test_cache_expiration(self):
        """测试缓存过期"""
        cache = PermissionCache(ttl_seconds=0)  # 立即过期
        key = PermissionCache.make_key("agent:test", "viewer", "document:doc1")

        # 设置缓存
        cache.set(key, True)

        # 等待过期
        import time
        time.sleep(0.1)

        # 获取缓存（应该已过期）
        result = cache.get(key)
        assert result is None

    def test_cache_clear(self):
        """测试清空缓存"""
        cache = PermissionCache(ttl_seconds=60)
        key = PermissionCache.make_key("agent:test", "viewer", "document:doc1")

        # 设置缓存
        cache.set(key, True)

        # 清空缓存
        cache.clear()

        # 获取缓存（应该为空）
        result = cache.get(key)
        assert result is None


class TestProtectedDocumentReadTool:
    """测试文档读取工具"""

    @pytest.mark.asyncio
    async def test_read_with_permission(
        self,
        mock_permission_checker,
        documents
    ):
        """测试有权限时读取文档"""
        # 设置模拟返回值
        mock_permission_checker.check_permission.return_value = True

        # 创建工具
        tool = ProtectedDocumentReadTool(
            permission_checker=mock_permission_checker,
            documents=documents
        )

        # 执行工具
        result = await tool._arun(
            agent_id="test_agent",
            document_id="doc1"
        )

        # 验证结果
        assert "✅" in result
        assert "测试文档 1" in result

        # 验证权限检查被调用
        mock_permission_checker.check_permission.assert_called_once_with(
            user="agent:test_agent",
            relation="can_read",
            object="document:doc1"
        )

    @pytest.mark.asyncio
    async def test_read_without_permission(
        self,
        mock_permission_checker,
        documents
    ):
        """测试无权限时读取文档"""
        # 设置模拟返回值
        mock_permission_checker.check_permission.return_value = False

        # 创建工具
        tool = ProtectedDocumentReadTool(
            permission_checker=mock_permission_checker,
            documents=documents
        )

        # 执行工具
        result = await tool._arun(
            agent_id="test_agent",
            document_id="doc1"
        )

        # 验证结果
        assert "❌" in result
        assert "权限被拒绝" in result

    @pytest.mark.asyncio
    async def test_read_nonexistent_document(
        self,
        mock_permission_checker,
        documents
    ):
        """测试读取不存在的文档"""
        # 设置模拟返回值
        mock_permission_checker.check_permission.return_value = True

        # 创建工具
        tool = ProtectedDocumentReadTool(
            permission_checker=mock_permission_checker,
            documents=documents
        )

        # 执行工具
        result = await tool._arun(
            agent_id="test_agent",
            document_id="nonexistent"
        )

        # 验证结果
        assert "❌" in result
        assert "不存在" in result


class TestProtectedDocumentWriteTool:
    """测试文档编辑工具"""

    @pytest.mark.asyncio
    async def test_write_with_permission(
        self,
        mock_permission_checker,
        documents
    ):
        """测试有权限时编辑文档"""
        # 设置模拟返回值
        mock_permission_checker.check_permission.return_value = True

        # 创建工具
        tool = ProtectedDocumentWriteTool(
            permission_checker=mock_permission_checker,
            documents=documents
        )

        # 执行工具
        result = await tool._arun(
            agent_id="test_agent",
            document_id="doc1",
            content="新内容"
        )

        # 验证结果
        assert "✅" in result
        assert "已更新" in result
        assert documents["doc1"] == "新内容"

    @pytest.mark.asyncio
    async def test_write_without_permission(
        self,
        mock_permission_checker,
        documents
    ):
        """测试无权限时编辑文档"""
        # 设置模拟返回值
        mock_permission_checker.check_permission.return_value = False

        # 创建工具
        tool = ProtectedDocumentWriteTool(
            permission_checker=mock_permission_checker,
            documents=documents
        )

        # 执行工具
        result = await tool._arun(
            agent_id="test_agent",
            document_id="doc1",
            content="新内容"
        )

        # 验证结果
        assert "❌" in result
        assert "权限被拒绝" in result
        assert documents["doc1"] == "测试文档 1"  # 内容未改变


class TestProtectedDatabaseQueryTool:
    """测试数据库查询工具"""

    @pytest.mark.asyncio
    async def test_query_with_permission(self, mock_permission_checker):
        """测试有权限时查询数据库"""
        # 设置模拟返回值
        mock_permission_checker.check_permission.return_value = True

        # 创建工具
        tool = ProtectedDatabaseQueryTool(
            permission_checker=mock_permission_checker
        )

        # 执行工具
        result = await tool._arun(
            agent_id="test_agent",
            database_id="main",
            query="SELECT * FROM users"
        )

        # 验证结果
        assert "✅" in result
        assert "查询结果" in result

    @pytest.mark.asyncio
    async def test_query_with_dangerous_sql(self, mock_permission_checker):
        """测试执行危险 SQL"""
        # 设置模拟返回值
        mock_permission_checker.check_permission.return_value = True

        # 创建工具
        tool = ProtectedDatabaseQueryTool(
            permission_checker=mock_permission_checker
        )

        # 执行工具
        result = await tool._arun(
            agent_id="test_agent",
            database_id="main",
            query="DELETE FROM users"
        )

        # 验证结果
        assert "❌" in result
        assert "只允许 SELECT 查询" in result

    def test_is_safe_query(self):
        """测试 SQL 安全检查"""
        tool = ProtectedDatabaseQueryTool()

        # 安全的查询
        assert tool._is_safe_query("SELECT * FROM users")
        assert tool._is_safe_query("select id, name from users where id = 1")

        # 危险的查询
        assert not tool._is_safe_query("DELETE FROM users")
        assert not tool._is_safe_query("UPDATE users SET name = 'test'")
        assert not tool._is_safe_query("INSERT INTO users VALUES (1, 'test')")
        assert not tool._is_safe_query("DROP TABLE users")


class TestProtectedSensitiveOperationTool:
    """测试敏感操作工具"""

    @pytest.mark.asyncio
    async def test_execute_with_permission(self, mock_permission_checker):
        """测试有权限时执行敏感操作"""
        # 设置模拟返回值
        mock_permission_checker.check_permission.return_value = True

        # 创建工具
        tool = ProtectedSensitiveOperationTool(
            permission_checker=mock_permission_checker
        )

        # 执行工具
        result = await tool._arun(
            agent_id="test_agent",
            operation_id="delete_all",
            params={"confirm": True}
        )

        # 验证结果
        assert "✅" in result
        assert "已执行" in result

    @pytest.mark.asyncio
    async def test_execute_without_permission(self, mock_permission_checker):
        """测试无权限时执行敏感操作"""
        # 设置模拟返回值
        mock_permission_checker.check_permission.return_value = False

        # 创建工具
        tool = ProtectedSensitiveOperationTool(
            permission_checker=mock_permission_checker
        )

        # 执行工具
        result = await tool._arun(
            agent_id="test_agent",
            operation_id="delete_all",
            params={"confirm": True}
        )

        # 验证结果
        assert "❌" in result
        assert "权限被拒绝" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
