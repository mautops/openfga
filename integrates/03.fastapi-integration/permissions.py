"""
OpenFGA 权限检查装饰器

提供基于 OpenFGA 的细粒度权限控制
"""

from fastapi import Depends, HTTPException, status, Request
from functools import wraps
from typing import Callable
import logging

from auth import get_current_user
from openfga_client import openfga_service

logger = logging.getLogger(__name__)


def require_permission(relation: str, object_type: str = "document"):
    """
    权限检查装饰器工厂

    创建一个 FastAPI 依赖函数，用于检查用户是否有指定的权限。

    Args:
        relation: 需要的权限关系（如 "viewer", "editor", "owner"）
        object_type: 对象类型（如 "document", "folder"）

    Returns:
        FastAPI 依赖函数

    使用示例:
        @app.get("/api/documents/{document_id}")
        async def get_document(
            document_id: str,
            current_user: dict = Depends(get_current_user),
            _: bool = Depends(require_permission("viewer", "document"))
        ):
            # 如果用户没有权限，会在这之前抛出 403 错误
            return {"document_id": document_id}
    """

    async def permission_checker(
        request: Request,
        current_user: dict = Depends(get_current_user)
    ) -> bool:
        """
        实际的权限检查函数

        从请求路径中提取资源 ID，然后调用 OpenFGA 检查权限。
        """
        user_id = current_user["user_id"]

        # 从路径参数中提取资源 ID
        # 支持多种命名方式：document_id, id, folder_id 等
        path_params = request.path_params
        resource_id = None

        # 尝试不同的参数名
        for param_name in [f"{object_type}_id", "id", "resource_id"]:
            if param_name in path_params:
                resource_id = path_params[param_name]
                break

        if not resource_id:
            logger.error(f"无法从路径参数中提取资源 ID: {path_params}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的请求：缺少资源 ID"
            )

        # 构造 OpenFGA 对象 ID
        object_id = f"{object_type}:{resource_id}"

        logger.debug(
            f"检查权限: user={user_id}, relation={relation}, object={object_id}"
        )

        # 调用 OpenFGA 检查权限
        try:
            allowed = await openfga_service.check_permission(
                user=f"user:{user_id}",
                relation=relation,
                object_id=object_id
            )

            if not allowed:
                logger.warning(
                    f"权限被拒绝: user={user_id}, relation={relation}, "
                    f"object={object_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"您没有对该{object_type}的{relation}权限"
                )

            logger.debug(f"权限检查通过: user={user_id}, object={object_id}")
            return True

        except HTTPException:
            # 重新抛出 HTTP 异常
            raise
        except Exception as e:
            logger.error(f"权限检查失败: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="权限检查失败"
            )

    return permission_checker


def require_any_permission(relations: list[str], object_type: str = "document"):
    """
    检查用户是否有任意一个指定的权限

    只要用户有列表中的任意一个权限，就允许访问。

    Args:
        relations: 权限关系列表（如 ["viewer", "editor", "owner"]）
        object_type: 对象类型

    Returns:
        FastAPI 依赖函数

    使用示例:
        @app.get("/api/documents/{document_id}/metadata")
        async def get_metadata(
            document_id: str,
            current_user: dict = Depends(get_current_user),
            _: bool = Depends(require_any_permission(["viewer", "editor", "owner"]))
        ):
            return {"metadata": "..."}
    """

    async def permission_checker(
        request: Request,
        current_user: dict = Depends(get_current_user)
    ) -> bool:
        user_id = current_user["user_id"]

        # 提取资源 ID
        path_params = request.path_params
        resource_id = None

        for param_name in [f"{object_type}_id", "id", "resource_id"]:
            if param_name in path_params:
                resource_id = path_params[param_name]
                break

        if not resource_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的请求：缺少资源 ID"
            )

        object_id = f"{object_type}:{resource_id}"

        # 检查是否有任意一个权限
        for relation in relations:
            try:
                allowed = await openfga_service.check_permission(
                    user=f"user:{user_id}",
                    relation=relation,
                    object_id=object_id
                )

                if allowed:
                    logger.debug(
                        f"权限检查通过: user={user_id}, relation={relation}, "
                        f"object={object_id}"
                    )
                    return True

            except Exception as e:
                logger.error(f"权限检查失败: {e}")
                continue

        # 所有权限都不满足
        logger.warning(
            f"权限被拒绝: user={user_id}, relations={relations}, "
            f"object={object_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"您没有访问该{object_type}的权限"
        )

    return permission_checker


async def check_permission_direct(
    user_id: str,
    relation: str,
    object_id: str
) -> bool:
    """
    直接检查权限（不作为依赖使用）

    在业务逻辑中需要手动检查权限时使用。

    Args:
        user_id: 用户 ID
        relation: 权限关系
        object_id: 对象 ID（完整格式，如 "document:doc_1"）

    Returns:
        是否有权限

    使用示例:
        async def some_business_logic(user_id: str, document_id: str):
            # 检查权限
            has_permission = await check_permission_direct(
                user_id=user_id,
                relation="editor",
                object_id=f"document:{document_id}"
            )

            if not has_permission:
                raise HTTPException(status_code=403, detail="无权限")

            # 执行业务逻辑
            ...
    """
    try:
        allowed = await openfga_service.check_permission(
            user=f"user:{user_id}",
            relation=relation,
            object_id=object_id
        )
        return allowed
    except Exception as e:
        logger.error(f"权限检查失败: {e}")
        return False


async def get_user_permissions(user_id: str, object_id: str) -> list[str]:
    """
    获取用户对某个对象的所有权限

    Args:
        user_id: 用户 ID
        object_id: 对象 ID（完整格式）

    Returns:
        用户拥有的权限关系列表

    使用示例:
        permissions = await get_user_permissions("user_1", "document:doc_1")
        # 返回: ["viewer", "editor"]
    """
    # 常见的权限关系
    common_relations = ["viewer", "editor", "owner", "admin"]

    user_permissions = []

    for relation in common_relations:
        try:
            allowed = await openfga_service.check_permission(
                user=f"user:{user_id}",
                relation=relation,
                object_id=object_id
            )

            if allowed:
                user_permissions.append(relation)

        except Exception as e:
            logger.error(f"检查权限 {relation} 失败: {e}")
            continue

    return user_permissions


# ==================== 批量权限检查 ====================

async def filter_accessible_objects(
    user_id: str,
    relation: str,
    object_ids: list[str]
) -> list[str]:
    """
    从对象列表中过滤出用户有权限访问的对象

    注意：这个方法会对每个对象进行单独的权限检查，性能较差。
    如果可能，应该使用 OpenFGA 的 ListObjects API。

    Args:
        user_id: 用户 ID
        relation: 权限关系
        object_ids: 对象 ID 列表（完整格式）

    Returns:
        用户有权限访问的对象 ID 列表
    """
    accessible = []

    for object_id in object_ids:
        try:
            allowed = await openfga_service.check_permission(
                user=f"user:{user_id}",
                relation=relation,
                object_id=object_id
            )

            if allowed:
                accessible.append(object_id)

        except Exception as e:
            logger.error(f"检查对象 {object_id} 权限失败: {e}")
            continue

    return accessible
