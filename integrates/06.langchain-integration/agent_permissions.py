"""
AI Agent 权限控制封装模块

提供 OpenFGA 权限检查的封装，用于 LangChain Agent 的权限管理。
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from openfga_sdk import OpenFgaClient, ClientConfiguration
from openfga_sdk.client.models import ClientWriteRequest, ClientTuple, ClientCheckRequest

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PermissionDeniedError(Exception):
    """权限被拒绝异常"""
    pass


class OpenFGAPermissionChecker:
    """OpenFGA 权限检查器

    封装 OpenFGA 客户端，提供权限检查、授予、撤销等功能。
    """

    def __init__(
        self,
        api_url: str,
        store_id: str,
        model_id: str,
        enable_audit: bool = True
    ):
        """初始化权限检查器

        Args:
            api_url: OpenFGA API 地址
            store_id: Store ID
            model_id: Authorization Model ID
            enable_audit: 是否启用审计日志
        """
        configuration = ClientConfiguration(
            api_url=api_url,
            store_id=store_id,
            authorization_model_id=model_id
        )
        self.client = OpenFgaClient(configuration)
        self.enable_audit = enable_audit
        self.audit_logs: List[Dict[str, Any]] = []

        logger.info(f"OpenFGA 权限检查器已初始化: {api_url}")

    async def check_permission(
        self,
        user: str,
        relation: str,
        object: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """检查权限

        Args:
            user: 用户标识（如 "agent:assistant" 或 "user:alice"）
            relation: 关系类型（如 "can_read", "can_write"）
            object: 对象标识（如 "document:doc1"）
            context: 上下文信息（可选）

        Returns:
            bool: 是否有权限
        """
        try:
            # 执行权限检查
            response = await self.client.check(
                ClientCheckRequest(
                    user=user,
                    relation=relation,
                    object=object,
                    contextual_tuples=context.get("tuples", []) if context else []
                )
            )

            allowed = response.allowed

            # 记录审计日志
            if self.enable_audit:
                self._log_audit(
                    action="check_permission",
                    user=user,
                    relation=relation,
                    object=object,
                    allowed=allowed,
                    context=context
                )

            logger.info(
                f"权限检查: user={user}, relation={relation}, "
                f"object={object}, allowed={allowed}"
            )

            return allowed

        except Exception as e:
            logger.error(f"权限检查失败: {e}")
            # 默认拒绝原则：出错时拒绝访问
            return False

    async def grant_permission(
        self,
        user: str,
        relation: str,
        object: str
    ) -> bool:
        """授予权限

        Args:
            user: 用户标识
            relation: 关系类型
            object: 对象标识

        Returns:
            bool: 是否成功
        """
        try:
            await self.client.write(
                ClientWriteRequest(
                    writes=[
                        ClientTuple(
                            user=user,
                            relation=relation,
                            object=object
                        )
                    ]
                )
            )

            # 记录审计日志
            if self.enable_audit:
                self._log_audit(
                    action="grant_permission",
                    user=user,
                    relation=relation,
                    object=object,
                    allowed=True
                )

            logger.info(
                f"权限已授予: user={user}, relation={relation}, object={object}"
            )

            return True

        except Exception as e:
            logger.error(f"授予权限失败: {e}")
            return False

    async def revoke_permission(
        self,
        user: str,
        relation: str,
        object: str
    ) -> bool:
        """撤销权限

        Args:
            user: 用户标识
            relation: 关系类型
            object: 对象标识

        Returns:
            bool: 是否成功
        """
        try:
            await self.client.write(
                ClientWriteRequest(
                    deletes=[
                        ClientTuple(
                            user=user,
                            relation=relation,
                            object=object
                        )
                    ]
                )
            )

            # 记录审计日志
            if self.enable_audit:
                self._log_audit(
                    action="revoke_permission",
                    user=user,
                    relation=relation,
                    object=object,
                    allowed=True
                )

            logger.info(
                f"权限已撤销: user={user}, relation={relation}, object={object}"
            )

            return True

        except Exception as e:
            logger.error(f"撤销权限失败: {e}")
            return False

    async def batch_check_permissions(
        self,
        checks: List[Dict[str, str]]
    ) -> List[bool]:
        """批量检查权限

        Args:
            checks: 权限检查列表，每项包含 user, relation, object

        Returns:
            List[bool]: 权限检查结果列表
        """
        tasks = [
            self.check_permission(
                user=check["user"],
                relation=check["relation"],
                object=check["object"]
            )
            for check in checks
        ]

        results = await asyncio.gather(*tasks)
        return list(results)

    def _log_audit(
        self,
        action: str,
        user: str,
        relation: str,
        object: str,
        allowed: bool,
        context: Optional[Dict[str, Any]] = None
    ):
        """记录审计日志

        Args:
            action: 操作类型
            user: 用户标识
            relation: 关系类型
            object: 对象标识
            allowed: 是否允许
            context: 上下文信息
        """
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "user": user,
            "relation": relation,
            "object": object,
            "allowed": allowed,
            "context": context or {}
        }

        self.audit_logs.append(audit_entry)

        # 在实际应用中，应该将审计日志持久化到数据库或日志系统
        logger.debug(f"审计日志: {audit_entry}")

    def get_audit_logs(
        self,
        user: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取审计日志

        Args:
            user: 用户标识（可选，用于过滤）
            limit: 返回的日志数量限制

        Returns:
            List[Dict]: 审计日志列表
        """
        logs = self.audit_logs

        # 按用户过滤
        if user:
            logs = [log for log in logs if log["user"] == user]

        # 返回最新的 N 条日志
        return logs[-limit:]

    async def close(self):
        """关闭客户端连接"""
        # OpenFGA SDK 会自动管理连接
        logger.info("OpenFGA 权限检查器已关闭")


class PermissionCache:
    """权限缓存

    用于缓存权限检查结果，提升性能。
    """

    def __init__(self, ttl_seconds: int = 300):
        """初始化权限缓存

        Args:
            ttl_seconds: 缓存过期时间（秒）
        """
        self.cache: Dict[str, tuple[bool, datetime]] = {}
        self.ttl_seconds = ttl_seconds

    def get(self, key: str) -> Optional[bool]:
        """获取缓存的权限结果

        Args:
            key: 缓存键

        Returns:
            Optional[bool]: 权限结果，如果缓存不存在或已过期则返回 None
        """
        if key not in self.cache:
            return None

        result, timestamp = self.cache[key]

        # 检查是否过期
        if (datetime.now() - timestamp).total_seconds() > self.ttl_seconds:
            del self.cache[key]
            return None

        return result

    def set(self, key: str, value: bool):
        """设置缓存

        Args:
            key: 缓存键
            value: 权限结果
        """
        self.cache[key] = (value, datetime.now())

    def clear(self):
        """清空缓存"""
        self.cache.clear()

    @staticmethod
    def make_key(user: str, relation: str, object: str) -> str:
        """生成缓存键

        Args:
            user: 用户标识
            relation: 关系类型
            object: 对象标识

        Returns:
            str: 缓存键
        """
        return f"{user}:{relation}:{object}"
