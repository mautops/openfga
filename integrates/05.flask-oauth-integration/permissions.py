"""
OpenFGA 权限检查装饰器和工具函数

提供便捷的权限检查装饰器，用于保护 API 端点
"""

from functools import wraps
from flask import session, jsonify, request
from openfga_sdk.client import OpenFgaClient
from openfga_sdk.client.models import ClientConfiguration, ClientCheckRequest, ClientWriteRequest, ClientTuple
import os
from typing import Optional, List
import asyncio


# 初始化 OpenFGA 客户端
def get_openfga_client():
    """获取 OpenFGA 客户端实例"""
    config = ClientConfiguration(
        api_url=os.getenv('OPENFGA_API_URL', 'http://localhost:8080'),
        store_id=os.getenv('OPENFGA_STORE_ID'),
        authorization_model_id=os.getenv('OPENFGA_MODEL_ID')
    )
    return OpenFgaClient(config)


def check_permission_sync(user_id: str, relation: str, object_id: str) -> bool:
    """
    同步检查权限

    参数:
        user_id: 用户 ID
        relation: 关系类型 (viewer, editor, owner)
        object_id: 对象 ID (例如: document:123)

    返回:
        bool: 是否有权限
    """
    try:
        client = get_openfga_client()

        # 创建新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # 执行权限检查
            response = loop.run_until_complete(
                client.check(ClientCheckRequest(
                    user=f"user:{user_id}",
                    relation=relation,
                    object=object_id
                ))
            )
            return response.allowed
        finally:
            loop.close()

    except Exception as e:
        print(f"权限检查失败: {e}")
        return False


async def check_permission_async(user_id: str, relation: str, object_id: str) -> bool:
    """
    异步检查权限

    参数:
        user_id: 用户 ID
        relation: 关系类型
        object_id: 对象 ID

    返回:
        bool: 是否有权限
    """
    try:
        client = get_openfga_client()
        response = await client.check(ClientCheckRequest(
            user=f"user:{user_id}",
            relation=relation,
            object=object_id
        ))
        return response.allowed
    except Exception as e:
        print(f"权限检查失败: {e}")
        return False


def write_tuples_sync(tuples: List[dict]) -> bool:
    """
    同步写入权限关系

    参数:
        tuples: 权限关系列表
            [
                {
                    'user': 'user:alice',
                    'relation': 'owner',
                    'object': 'document:123'
                }
            ]

    返回:
        bool: 是否成功
    """
    try:
        client = get_openfga_client()

        # 转换为 ClientTuple 对象
        client_tuples = [
            ClientTuple(
                user=t['user'],
                relation=t['relation'],
                object=t['object']
            )
            for t in tuples
        ]

        # 创建新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(
                client.write(ClientWriteRequest(
                    writes=client_tuples
                ))
            )
            return True
        finally:
            loop.close()

    except Exception as e:
        print(f"写入权限关系失败: {e}")
        return False


def delete_tuples_sync(tuples: List[dict]) -> bool:
    """
    同步删除权限关系

    参数:
        tuples: 要删除的权限关系列表

    返回:
        bool: 是否成功
    """
    try:
        client = get_openfga_client()

        # 转换为 ClientTuple 对象
        client_tuples = [
            ClientTuple(
                user=t['user'],
                relation=t['relation'],
                object=t['object']
            )
            for t in tuples
        ]

        # 创建新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(
                client.write(ClientWriteRequest(
                    deletes=client_tuples
                ))
            )
            return True
        finally:
            loop.close()

    except Exception as e:
        print(f"删除权限关系失败: {e}")
        return False


def require_permission(relation: str, object_type: str = 'document', object_id_param: str = 'document_id'):
    """
    权限检查装饰器

    参数:
        relation: 需要的关系类型 (viewer, editor, owner)
        object_type: 对象类型 (document, folder 等)
        object_id_param: URL 参数中对象 ID 的名称

    使用示例:
        @app.route('/documents/<document_id>')
        @require_permission('viewer', 'document', 'document_id')
        def get_document(document_id):
            ...

    注意:
        - 需要用户已登录（session 中有 user_id）
        - 会自动从 URL 参数中提取对象 ID
        - 权限检查失败返回 403
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 检查用户是否已登录
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({
                    'error': 'Unauthorized',
                    'message': 'Please login first'
                }), 401

            # 从 URL 参数中获取对象 ID
            object_id_value = kwargs.get(object_id_param)
            if not object_id_value:
                return jsonify({
                    'error': 'Bad Request',
                    'message': f'Missing parameter: {object_id_param}'
                }), 400

            # 构造完整的对象 ID
            full_object_id = f"{object_type}:{object_id_value}"

            # 检查权限
            has_permission = check_permission_sync(
                user_id=user_id,
                relation=relation,
                object_id=full_object_id
            )

            if not has_permission:
                return jsonify({
                    'error': 'Forbidden',
                    'message': f'You do not have {relation} permission for this {object_type}'
                }), 403

            # 权限检查通过，执行原函数
            return f(*args, **kwargs)

        return decorated_function
    return decorator


def require_any_permission(relations: List[str], object_type: str = 'document', object_id_param: str = 'document_id'):
    """
    多个权限之一的检查装饰器

    只要用户拥有列表中的任意一个权限即可通过

    参数:
        relations: 权限列表 ['viewer', 'editor', 'owner']
        object_type: 对象类型
        object_id_param: URL 参数名

    使用示例:
        @require_any_permission(['editor', 'owner'], 'document')
        def update_document(document_id):
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 检查用户是否已登录
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({
                    'error': 'Unauthorized',
                    'message': 'Please login first'
                }), 401

            # 从 URL 参数中获取对象 ID
            object_id_value = kwargs.get(object_id_param)
            if not object_id_value:
                return jsonify({
                    'error': 'Bad Request',
                    'message': f'Missing parameter: {object_id_param}'
                }), 400

            # 构造完整的对象 ID
            full_object_id = f"{object_type}:{object_id_value}"

            # 检查是否有任意一个权限
            has_permission = False
            for relation in relations:
                if check_permission_sync(user_id, relation, full_object_id):
                    has_permission = True
                    break

            if not has_permission:
                return jsonify({
                    'error': 'Forbidden',
                    'message': f'You do not have required permissions for this {object_type}'
                }), 403

            # 权限检查通过
            return f(*args, **kwargs)

        return decorated_function
    return decorator


def grant_permission(user_id: str, relation: str, object_id: str) -> bool:
    """
    授予权限

    参数:
        user_id: 用户 ID
        relation: 关系类型
        object_id: 对象 ID

    返回:
        bool: 是否成功
    """
    return write_tuples_sync([{
        'user': f"user:{user_id}",
        'relation': relation,
        'object': object_id
    }])


def revoke_permission(user_id: str, relation: str, object_id: str) -> bool:
    """
    撤销权限

    参数:
        user_id: 用户 ID
        relation: 关系类型
        object_id: 对象 ID

    返回:
        bool: 是否成功
    """
    return delete_tuples_sync([{
        'user': f"user:{user_id}",
        'relation': relation,
        'object': object_id
    }])


def list_user_objects(user_id: str, relation: str, object_type: str) -> List[str]:
    """
    列出用户可访问的对象

    参数:
        user_id: 用户 ID
        relation: 关系类型
        object_type: 对象类型

    返回:
        对象 ID 列表
    """
    try:
        client = get_openfga_client()

        # 创建新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            response = loop.run_until_complete(
                client.list_objects(
                    user=f"user:{user_id}",
                    relation=relation,
                    type=object_type
                )
            )
            return response.objects or []
        finally:
            loop.close()

    except Exception as e:
        print(f"列出对象失败: {e}")
        return []
