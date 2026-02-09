"""
带权限检查的 LangChain 工具定义

提供各种带权限检查的工具，用于 LangChain Agent。
"""

import asyncio
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from agent_permissions import OpenFGAPermissionChecker, PermissionDeniedError
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# 工具输入模型定义
# ============================================================================

class DocumentReadInput(BaseModel):
    """文档读取工具的输入模型"""
    agent_id: str = Field(description="Agent ID，用于权限检查")
    document_id: str = Field(description="文档 ID")


class DocumentWriteInput(BaseModel):
    """文档编辑工具的输入模型"""
    agent_id: str = Field(description="Agent ID，用于权限检查")
    document_id: str = Field(description="文档 ID")
    content: str = Field(description="要写入的内容")


class DatabaseQueryInput(BaseModel):
    """数据库查询工具的输入模型"""
    agent_id: str = Field(description="Agent ID，用于权限检查")
    database_id: str = Field(description="数据库 ID")
    query: str = Field(description="SQL 查询语句")


class SensitiveOperationInput(BaseModel):
    """敏感操作工具的输入模型"""
    agent_id: str = Field(description="Agent ID，用于权限检查")
    operation_id: str = Field(description="操作 ID")
    params: Dict[str, Any] = Field(description="操作参数")


# ============================================================================
# 带权限检查的工具实现
# ============================================================================

class ProtectedDocumentReadTool(BaseTool):
    """带权限检查的文档读取工具

    需要 viewer 权限才能读取文档。
    """

    name: str = "read_document"
    description: str = (
        "读取文档内容。需要提供 Agent ID 和文档 ID。"
        "Agent 必须有 viewer 权限才能读取文档。"
    )
    args_schema: type[BaseModel] = DocumentReadInput

    # 依赖注入
    permission_checker: Optional[OpenFGAPermissionChecker] = None
    documents: Dict[str, str] = {}  # 模拟文档存储

    def _run(
        self,
        agent_id: str,
        document_id: str
    ) -> str:
        """同步执行（LangChain 要求实现）"""
        return asyncio.run(self._arun(agent_id, document_id))

    async def _arun(
        self,
        agent_id: str,
        document_id: str
    ) -> str:
        """异步执行（实际实现）"""
        try:
            # 1. 权限检查
            allowed = await self.permission_checker.check_permission(
                user=f"agent:{agent_id}",
                relation="can_read",
                object=f"document:{document_id}"
            )

            if not allowed:
                error_msg = (
                    f"❌ 权限被拒绝: Agent {agent_id} 无权读取文档 {document_id}。"
                    f"需要 viewer 权限。"
                )
                logger.warning(error_msg)
                return error_msg

            # 2. 检查文档是否存在
            if document_id not in self.documents:
                return f"❌ 文档 {document_id} 不存在"

            # 3. 读取文档内容
            content = self.documents[document_id]

            # 4. 返回结果
            logger.info(f"✅ Agent {agent_id} 成功读取文档 {document_id}")
            return f"✅ 文档内容:\n{content}"

        except Exception as e:
            error_msg = f"❌ 读取文档时发生错误: {str(e)}"
            logger.error(error_msg)
            return error_msg


class ProtectedDocumentWriteTool(BaseTool):
    """带权限检查的文档编辑工具

    需要 editor 权限才能编辑文档。
    """

    name: str = "write_document"
    description: str = (
        "编辑文档内容。需要提供 Agent ID、文档 ID 和新内容。"
        "Agent 必须有 editor 权限才能编辑文档。"
    )
    args_schema: type[BaseModel] = DocumentWriteInput

    # 依赖注入
    permission_checker: Optional[OpenFGAPermissionChecker] = None
    documents: Dict[str, str] = {}  # 模拟文档存储

    def _run(
        self,
        agent_id: str,
        document_id: str,
        content: str
    ) -> str:
        """同步执行"""
        return asyncio.run(self._arun(agent_id, document_id, content))

    async def _arun(
        self,
        agent_id: str,
        document_id: str,
        content: str
    ) -> str:
        """异步执行"""
        try:
            # 1. 权限检查
            allowed = await self.permission_checker.check_permission(
                user=f"agent:{agent_id}",
                relation="can_write",
                object=f"document:{document_id}"
            )

            if not allowed:
                error_msg = (
                    f"❌ 权限被拒绝: Agent {agent_id} 无权编辑文档 {document_id}。"
                    f"需要 editor 权限。"
                )
                logger.warning(error_msg)
                return error_msg

            # 2. 编辑文档
            self.documents[document_id] = content

            # 3. 返回结果
            logger.info(f"✅ Agent {agent_id} 成功编辑文档 {document_id}")
            return f"✅ 文档 {document_id} 已更新"

        except Exception as e:
            error_msg = f"❌ 编辑文档时发生错误: {str(e)}"
            logger.error(error_msg)
            return error_msg


class ProtectedDatabaseQueryTool(BaseTool):
    """带权限检查的数据库查询工具

    需要 db_reader 权限才能查询数据库。
    """

    name: str = "query_database"
    description: str = (
        "查询数据库。需要提供 Agent ID、数据库 ID 和 SQL 查询语句。"
        "Agent 必须有 db_reader 权限才能查询数据库。"
        "只支持 SELECT 查询，不支持 INSERT/UPDATE/DELETE。"
    )
    args_schema: type[BaseModel] = DatabaseQueryInput

    # 依赖注入
    permission_checker: Optional[OpenFGAPermissionChecker] = None

    def _run(
        self,
        agent_id: str,
        database_id: str,
        query: str
    ) -> str:
        """同步执行"""
        return asyncio.run(self._arun(agent_id, database_id, query))

    async def _arun(
        self,
        agent_id: str,
        database_id: str,
        query: str
    ) -> str:
        """异步执行"""
        try:
            # 1. 权限检查
            allowed = await self.permission_checker.check_permission(
                user=f"agent:{agent_id}",
                relation="can_query",
                object=f"database:{database_id}"
            )

            if not allowed:
                error_msg = (
                    f"❌ 权限被拒绝: Agent {agent_id} 无权查询数据库 {database_id}。"
                    f"需要 db_reader 权限。"
                )
                logger.warning(error_msg)
                return error_msg

            # 2. 检查 SQL 安全性（只允许 SELECT）
            if not self._is_safe_query(query):
                error_msg = "❌ 只允许 SELECT 查询，不支持修改操作"
                logger.warning(error_msg)
                return error_msg

            # 3. 执行查询（模拟）
            result = self._execute_query(database_id, query)

            # 4. 返回结果
            logger.info(f"✅ Agent {agent_id} 成功查询数据库 {database_id}")
            return f"✅ 查询结果:\n{result}"

        except Exception as e:
            error_msg = f"❌ 查询数据库时发生错误: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def _is_safe_query(self, query: str) -> bool:
        """检查 SQL 查询是否安全

        Args:
            query: SQL 查询语句

        Returns:
            bool: 是否安全
        """
        query_upper = query.upper().strip()

        # 只允许 SELECT 查询
        if not query_upper.startswith("SELECT"):
            return False

        # 禁止的关键字
        dangerous_keywords = [
            "DELETE", "UPDATE", "INSERT", "DROP",
            "ALTER", "CREATE", "TRUNCATE", "EXEC"
        ]

        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return False

        return True

    def _execute_query(self, database_id: str, query: str) -> str:
        """执行查询（模拟）

        Args:
            database_id: 数据库 ID
            query: SQL 查询语句

        Returns:
            str: 查询结果
        """
        # 模拟查询结果
        return """
id | name      | email
---|-----------|------------------
1  | Alice     | alice@example.com
2  | Bob       | bob@example.com
3  | Charlie   | charlie@example.com
        """


class ProtectedSensitiveOperationTool(BaseTool):
    """带权限检查的敏感操作工具

    需要 admin 权限才能执行敏感操作。
    """

    name: str = "sensitive_operation"
    description: str = (
        "执行敏感操作。需要提供 Agent ID、操作 ID 和操作参数。"
        "Agent 必须有 admin 权限才能执行敏感操作。"
        "此操作会被严格审计。"
    )
    args_schema: type[BaseModel] = SensitiveOperationInput

    # 依赖注入
    permission_checker: Optional[OpenFGAPermissionChecker] = None

    def _run(
        self,
        agent_id: str,
        operation_id: str,
        params: Dict[str, Any]
    ) -> str:
        """同步执行"""
        return asyncio.run(self._arun(agent_id, operation_id, params))

    async def _arun(
        self,
        agent_id: str,
        operation_id: str,
        params: Dict[str, Any]
    ) -> str:
        """异步执行"""
        try:
            # 1. 权限检查
            allowed = await self.permission_checker.check_permission(
                user=f"agent:{agent_id}",
                relation="can_execute",
                object=f"sensitive_operation:{operation_id}"
            )

            if not allowed:
                error_msg = (
                    f"❌ 权限被拒绝: Agent {agent_id} 无权执行敏感操作 {operation_id}。"
                    f"需要 admin 权限。此操作已被记录。"
                )
                logger.warning(error_msg)
                return error_msg

            # 2. 执行敏感操作（模拟）
            result = self._execute_operation(operation_id, params)

            # 3. 返回结果
            logger.info(
                f"✅ Agent {agent_id} 成功执行敏感操作 {operation_id}，"
                f"参数: {params}"
            )
            return f"✅ 敏感操作已执行:\n{result}"

        except Exception as e:
            error_msg = f"❌ 执行敏感操作时发生错误: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def _execute_operation(
        self,
        operation_id: str,
        params: Dict[str, Any]
    ) -> str:
        """执行操作（模拟）

        Args:
            operation_id: 操作 ID
            params: 操作参数

        Returns:
            str: 操作结果
        """
        # 模拟操作结果
        return f"操作 {operation_id} 已完成，参数: {params}"


# ============================================================================
# 工具工厂函数
# ============================================================================

def create_protected_tools(
    permission_checker: OpenFGAPermissionChecker,
    documents: Optional[Dict[str, str]] = None
) -> list[BaseTool]:
    """创建带权限检查的工具列表

    Args:
        permission_checker: 权限检查器
        documents: 文档存储（可选）

    Returns:
        list[BaseTool]: 工具列表
    """
    # 默认文档
    if documents is None:
        documents = {
            "doc1": "这是一份关于 AI 的技术文档。",
            "doc2": "这是一份关于权限管理的文档。",
            "doc3": "这是一份敏感的财务报告。"
        }

    # 创建工具
    tools = [
        ProtectedDocumentReadTool(
            permission_checker=permission_checker,
            documents=documents
        ),
        ProtectedDocumentWriteTool(
            permission_checker=permission_checker,
            documents=documents
        ),
        ProtectedDatabaseQueryTool(
            permission_checker=permission_checker
        ),
        ProtectedSensitiveOperationTool(
            permission_checker=permission_checker
        )
    ]

    return tools
