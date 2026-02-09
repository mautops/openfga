"""
API 视图函数

提供文档 CRUD 和分享功能的 API 端点
"""

from flask import Blueprint, jsonify, request, session
from auth import require_auth, get_current_user
from permissions import (
    require_permission,
    require_any_permission,
    grant_permission,
    revoke_permission,
    list_user_objects
)
from models import Document, Share
import uuid


# 创建蓝图
api_bp = Blueprint('api', __name__)


@api_bp.route('/documents', methods=['GET'])
@require_auth
def list_documents():
    """
    列出当前用户可访问的文档

    需要认证

    返回:
        文档列表
    """
    user = get_current_user()
    user_id = user['user_id']

    # 从 OpenFGA 获取用户可访问的文档列表
    accessible_objects = list_user_objects(
        user_id=user_id,
        relation='viewer',
        object_type='document'
    )

    # 提取文档 ID
    document_ids = [obj.split(':')[1] for obj in accessible_objects if ':' in obj]

    # 从数据库获取文档详情
    if document_ids:
        documents = Document.list_by_ids(document_ids)
    else:
        documents = []

    return jsonify({
        'documents': documents,
        'total': len(documents)
    })


@api_bp.route('/documents', methods=['POST'])
@require_auth
def create_document():
    """
    创建文档

    需要认证

    请求体:
        {
            "title": "文档标题",
            "content": "文档内容"
        }

    返回:
        创建的文档信息
    """
    user = get_current_user()
    user_id = user['user_id']

    data = request.get_json()

    # 验证输入
    if not data or 'title' not in data:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Title is required'
        }), 400

    title = data['title']
    content = data.get('content', '')

    # 生成文档 ID
    document_id = str(uuid.uuid4())

    # 创建文档
    document = Document.create(
        document_id=document_id,
        title=title,
        content=content,
        owner_id=user_id
    )

    # 在 OpenFGA 中授予所有者权限
    # owner 关系会自动继承 editor 和 viewer 权限
    success = grant_permission(
        user_id=user_id,
        relation='owner',
        object_id=f"document:{document_id}"
    )

    if not success:
        # 如果授权失败，删除文档
        Document.delete(document_id)
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Failed to grant permissions'
        }), 500

    return jsonify({
        'message': 'Document created successfully',
        'document': document
    }), 201


@api_bp.route('/documents/<document_id>', methods=['GET'])
@require_auth
@require_permission('viewer', 'document', 'document_id')
def get_document(document_id):
    """
    获取文档详情

    需要认证和 viewer 权限

    参数:
        document_id: 文档 ID

    返回:
        文档详情
    """
    document = Document.get(document_id)

    if not document:
        return jsonify({
            'error': 'Not Found',
            'message': 'Document not found'
        }), 404

    return jsonify({
        'document': document
    })


@api_bp.route('/documents/<document_id>', methods=['PUT'])
@require_auth
@require_permission('editor', 'document', 'document_id')
def update_document(document_id):
    """
    更新文档

    需要认证和 editor 权限

    参数:
        document_id: 文档 ID

    请求体:
        {
            "title": "新标题",
            "content": "新内容"
        }

    返回:
        更新后的文档
    """
    data = request.get_json()

    if not data:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Request body is required'
        }), 400

    title = data.get('title')
    content = data.get('content')

    # 更新文档
    success = Document.update(
        document_id=document_id,
        title=title,
        content=content
    )

    if not success:
        return jsonify({
            'error': 'Not Found',
            'message': 'Document not found'
        }), 404

    # 获取更新后的文档
    document = Document.get(document_id)

    return jsonify({
        'message': 'Document updated successfully',
        'document': document
    })


@api_bp.route('/documents/<document_id>', methods=['DELETE'])
@require_auth
@require_permission('owner', 'document', 'document_id')
def delete_document(document_id):
    """
    删除文档

    需要认证和 owner 权限

    参数:
        document_id: 文档 ID

    返回:
        删除结果
    """
    success = Document.delete(document_id)

    if not success:
        return jsonify({
            'error': 'Not Found',
            'message': 'Document not found'
        }), 404

    # 注意：OpenFGA 中的权限关系会在文档删除后仍然存在
    # 在生产环境中，应该同时删除 OpenFGA 中的相关权限关系
    # 这里为了简化示例，暂不处理

    return jsonify({
        'message': 'Document deleted successfully'
    })


@api_bp.route('/documents/<document_id>/share', methods=['POST'])
@require_auth
@require_permission('owner', 'document', 'document_id')
def share_document(document_id):
    """
    分享文档给其他用户

    需要认证和 owner 权限

    参数:
        document_id: 文档 ID

    请求体:
        {
            "user_id": "目标用户 ID",
            "permission": "viewer" 或 "editor"
        }

    返回:
        分享结果
    """
    user = get_current_user()
    current_user_id = user['user_id']

    data = request.get_json()

    # 验证输入
    if not data or 'user_id' not in data or 'permission' not in data:
        return jsonify({
            'error': 'Bad Request',
            'message': 'user_id and permission are required'
        }), 400

    target_user_id = data['user_id']
    permission = data['permission']

    # 验证权限类型
    if permission not in ['viewer', 'editor']:
        return jsonify({
            'error': 'Bad Request',
            'message': 'permission must be "viewer" or "editor"'
        }), 400

    # 不能分享给自己
    if target_user_id == current_user_id:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Cannot share document with yourself'
        }), 400

    # 检查文档是否存在
    document = Document.get(document_id)
    if not document:
        return jsonify({
            'error': 'Not Found',
            'message': 'Document not found'
        }), 404

    # 在 OpenFGA 中授予权限
    success = grant_permission(
        user_id=target_user_id,
        relation=permission,
        object_id=f"document:{document_id}"
    )

    if not success:
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Failed to grant permissions'
        }), 500

    # 记录分享
    share = Share.create(
        document_id=document_id,
        user_id=target_user_id,
        permission=permission,
        shared_by=current_user_id
    )

    return jsonify({
        'message': 'Document shared successfully',
        'share': share
    }), 201


@api_bp.route('/documents/<document_id>/share/<user_id>', methods=['DELETE'])
@require_auth
@require_permission('owner', 'document', 'document_id')
def unshare_document(document_id, user_id):
    """
    取消分享

    需要认证和 owner 权限

    参数:
        document_id: 文档 ID
        user_id: 目标用户 ID

    返回:
        取消分享结果
    """
    # 撤销 viewer 和 editor 权限
    revoke_permission(user_id, 'viewer', f"document:{document_id}")
    revoke_permission(user_id, 'editor', f"document:{document_id}")

    # 删除分享记录
    Share.delete(document_id, user_id)

    return jsonify({
        'message': 'Share removed successfully'
    })


@api_bp.route('/documents/<document_id>/shares', methods=['GET'])
@require_auth
@require_permission('owner', 'document', 'document_id')
def list_shares(document_id):
    """
    列出文档的所有分享记录

    需要认证和 owner 权限

    参数:
        document_id: 文档 ID

    返回:
        分享记录列表
    """
    shares = Share.get_by_document(document_id)

    return jsonify({
        'shares': shares,
        'total': len(shares)
    })
