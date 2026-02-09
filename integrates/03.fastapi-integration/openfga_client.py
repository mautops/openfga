"""
OpenFGA 客户端封装

提供与 OpenFGA 服务交互的统一接口
"""

from openfga_sdk import OpenFgaClient, ClientConfiguration
from openfga_sdk.client.models import ClientCheckRequest, ClientWriteRequest, ClientTuple
from typing import List, Dict, Optional
import logging

from config import settings

logger = logging.getLogger(__name__)


class OpenFGAService:
    """
    OpenFGA 服务封装类

    提供权限检查、写入、删除等操作的统一接口
    """

    def __init__(self):
        """初始化 OpenFGA 客户端"""
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """初始化 OpenFGA 客户端配置"""
        try:
            configuration = ClientConfiguration(
                api_url=settings.OPENFGA_API_URL,
                store_id=settings.OPENFGA_STORE_ID,
                authorization_model_id=settings.OPENFGA_MODEL_ID
            )

            self.client = OpenFgaClient(configuration)
            logger.info(f"OpenFGA 客户端初始化成功: {settings.OPENFGA_API_URL}")

        except Exception as e:
            logger.error(f"OpenFGA 客户端初始化失败: {e}")
            raise

    async def check_permission(
        self,
        user: str,
        relation: str,
        object_id: str,
        contextual_tuples: Optional[List[Dict]] = None
    ) -> bool:
        """
        检查用户是否有指定的权限

        Args:
            user: 用户标识（格式：user:user_id）
            relation: 权限关系（如 viewer, editor, owner）
            object_id: 对象标识（格式：type:id，如 document:doc_1）
            contextual_tuples: 上下文元组（可选），用于临时权限检查

        Returns:
            是否有权限

        示例:
            allowed = await openfga_service.check_permission(
                user="user:alice",
                relation="viewer",
                object_id="document:doc_1"
            )
        """
        try:
            request = ClientCheckRequest(
                user=user,
                relation=relation,
                object=object_id
            )

            if contextual_tuples:
                request.contextual_tuples = [
                    ClientTuple(**tuple_data) for tuple_data in contextual_tuples
                ]

            response = await self.client.check(request)

            logger.debug(
                f"权限检查: user={user}, relation={relation}, "
                f"object={object_id}, allowed={response.allowed}"
            )

            return response.allowed

        except Exception as e:
            logger.error(f"权限检查失败: {e}", exc_info=True)
            raise

    async def write_tuples(self, tuples: List[Dict]) -> bool:
        """
        写入权限关系元组

        Args:
            tuples: 权限关系元组列表，每个元组包含 user, relation, object

        Returns:
            是否写入成功

        示例:
            await openfga_service.write_tuples([
                {
                    "user": "user:alice",
                    "relation": "owner",
                    "object": "document:doc_1"
                },
                {
                    "user": "user:bob",
                    "relation": "viewer",
                    "object": "document:doc_1"
                }
            ])
        """
        try:
            # 转换为 ClientTuple 对象
            client_tuples = [
                ClientTuple(
                    user=t["user"],
                    relation=t["relation"],
                    object=t["object"]
                )
                for t in tuples
            ]

            request = ClientWriteRequest(
                writes=client_tuples
            )

            await self.client.write(request)

            logger.info(f"成功写入 {len(tuples)} 个权限关系")
            for t in tuples:
                logger.debug(f"  - {t['user']} -> {t['relation']} -> {t['object']}")

            return True

        except Exception as e:
            logger.error(f"写入权限关系失败: {e}", exc_info=True)
            raise

    async def delete_tuples(self, tuples: List[Dict]) -> bool:
        """
        删除权限关系元组

        Args:
            tuples: 要删除的权限关系元组列表

        Returns:
            是否删除成功

        示例:
            await openfga_service.delete_tuples([
                {
                    "user": "user:bob",
                    "relation": "viewer",
                    "object": "document:doc_1"
                }
            ])
        """
        try:
            # 转换为 ClientTuple 对象
            client_tuples = [
                ClientTuple(
                    user=t["user"],
                    relation=t["relation"],
                    object=t["object"]
                )
                for t in tuples
            ]

            request = ClientWriteRequest(
                deletes=client_tuples
            )

            await self.client.write(request)

            logger.info(f"成功删除 {len(tuples)} 个权限关系")
            for t in tuples:
                logger.debug(f"  - {t['user']} -> {t['relation']} -> {t['object']}")

            return True

        except Exception as e:
            logger.error(f"删除权限关系失败: {e}", exc_info=True)
            raise

    async def list_objects(
        self,
        user: str,
        relation: str,
        object_type: str
    ) -> List[str]:
        """
        列出用户有权限访问的所有对象

        Args:
            user: 用户标识（格式：user:user_id）
            relation: 权限关系
            object_type: 对象类型（如 document, folder）

        Returns:
            对象 ID 列表（格式：type:id）

        示例:
            objects = await openfga_service.list_objects(
                user="user:alice",
                relation="viewer",
                object_type="document"
            )
            # 返回: ["document:doc_1", "document:doc_2"]
        """
        try:
            response = await self.client.list_objects(
                user=user,
                relation=relation,
                type=object_type
            )

            objects = response.objects or []

            logger.debug(
                f"列出对象: user={user}, relation={relation}, "
                f"type={object_type}, count={len(objects)}"
            )

            return objects

        except Exception as e:
            logger.error(f"列出对象失败: {e}", exc_info=True)
            raise

    async def read_tuples(
        self,
        user: Optional[str] = None,
        relation: Optional[str] = None,
        object_id: Optional[str] = None
    ) -> List[Dict]:
        """
        读取权限关系元组

        可以根据 user, relation, object 进行过滤查询。

        Args:
            user: 用户标识（可选）
            relation: 权限关系（可选）
            object_id: 对象标识（可选）

        Returns:
            权限关系元组列表

        示例:
            # 查询某个文档的所有权限关系
            tuples = await openfga_service.read_tuples(
                object_id="document:doc_1"
            )
        """
        try:
            # 构建查询参数
            query = {}
            if user:
                query["user"] = user
            if relation:
                query["relation"] = relation
            if object_id:
                query["object"] = object_id

            response = await self.client.read(**query)

            tuples = []
            if response.tuples:
                tuples = [
                    {
                        "user": t.key.user,
                        "relation": t.key.relation,
                        "object": t.key.object
                    }
                    for t in response.tuples
                ]

            logger.debug(f"读取元组: query={query}, count={len(tuples)}")

            return tuples

        except Exception as e:
            logger.error(f"读取元组失败: {e}", exc_info=True)
            raise

    async def expand(self, relation: str, object_id: str) -> Dict:
        """
        展开对象的权限树

        显示哪些用户通过哪些路径有权限访问该对象。

        Args:
            relation: 权限关系
            object_id: 对象标识

        Returns:
            权限树结构

        示例:
            tree = await openfga_service.expand(
                relation="viewer",
                object_id="document:doc_1"
            )
        """
        try:
            response = await self.client.expand(
                relation=relation,
                object=object_id
            )

            logger.debug(f"展开权限树: relation={relation}, object={object_id}")

            return response.tree

        except Exception as e:
            logger.error(f"展开权限树失败: {e}", exc_info=True)
            raise


# 创建全局单例
openfga_service = OpenFGAService()


# ==================== 辅助函数 ====================

async def grant_permission(
    user_id: str,
    relation: str,
    object_type: str,
    object_id: str
) -> bool:
    """
    授予用户权限的便捷函数

    Args:
        user_id: 用户 ID（不带前缀）
        relation: 权限关系
        object_type: 对象类型
        object_id: 对象 ID（不带前缀）

    Returns:
        是否成功

    示例:
        await grant_permission("alice", "viewer", "document", "doc_1")
    """
    return await openfga_service.write_tuples([
        {
            "user": f"user:{user_id}",
            "relation": relation,
            "object": f"{object_type}:{object_id}"
        }
    ])


async def revoke_permission(
    user_id: str,
    relation: str,
    object_type: str,
    object_id: str
) -> bool:
    """
    撤销用户权限的便捷函数

    Args:
        user_id: 用户 ID（不带前缀）
        relation: 权限关系
        object_type: 对象类型
        object_id: 对象 ID（不带前缀）

    Returns:
        是否成功

    示例:
        await revoke_permission("bob", "viewer", "document", "doc_1")
    """
    return await openfga_service.delete_tuples([
        {
            "user": f"user:{user_id}",
            "relation": relation,
            "object": f"{object_type}:{object_id}"
        }
    ])
