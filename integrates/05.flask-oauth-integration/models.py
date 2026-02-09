"""
数据模型

使用 SQLite 作为简单的数据存储
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict
import json


# 数据库文件路径
DB_PATH = os.getenv('DATABASE_PATH', 'documents.db')


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 创建文档表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT,
            owner_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')

    # 创建分享记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            permission TEXT NOT NULL,
            shared_by TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (document_id) REFERENCES documents (id)
        )
    ''')

    conn.commit()
    conn.close()


class Document:
    """文档模型"""

    @staticmethod
    def create(document_id: str, title: str, content: str, owner_id: str) -> Dict:
        """
        创建文档

        参数:
            document_id: 文档 ID
            title: 标题
            content: 内容
            owner_id: 所有者 ID

        返回:
            文档字典
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        now = datetime.utcnow().isoformat()

        cursor.execute('''
            INSERT INTO documents (id, title, content, owner_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (document_id, title, content, owner_id, now, now))

        conn.commit()
        conn.close()

        return {
            'id': document_id,
            'title': title,
            'content': content,
            'owner_id': owner_id,
            'created_at': now,
            'updated_at': now
        }

    @staticmethod
    def get(document_id: str) -> Optional[Dict]:
        """
        获取文档

        参数:
            document_id: 文档 ID

        返回:
            文档字典或 None
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM documents WHERE id = ?', (document_id,))
        row = cursor.fetchone()

        conn.close()

        if row:
            return dict(row)
        return None

    @staticmethod
    def update(document_id: str, title: Optional[str] = None, content: Optional[str] = None) -> bool:
        """
        更新文档

        参数:
            document_id: 文档 ID
            title: 新标题（可选）
            content: 新内容（可选）

        返回:
            是否成功
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        updates = []
        params = []

        if title is not None:
            updates.append('title = ?')
            params.append(title)

        if content is not None:
            updates.append('content = ?')
            params.append(content)

        if not updates:
            return False

        updates.append('updated_at = ?')
        params.append(datetime.utcnow().isoformat())

        params.append(document_id)

        query = f"UPDATE documents SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)

        conn.commit()
        success = cursor.rowcount > 0
        conn.close()

        return success

    @staticmethod
    def delete(document_id: str) -> bool:
        """
        删除文档

        参数:
            document_id: 文档 ID

        返回:
            是否成功
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        # 删除文档
        cursor.execute('DELETE FROM documents WHERE id = ?', (document_id,))

        # 删除相关的分享记录
        cursor.execute('DELETE FROM shares WHERE document_id = ?', (document_id,))

        conn.commit()
        success = cursor.rowcount > 0
        conn.close()

        return success

    @staticmethod
    def list_by_ids(document_ids: List[str]) -> List[Dict]:
        """
        根据 ID 列表获取文档

        参数:
            document_ids: 文档 ID 列表

        返回:
            文档列表
        """
        if not document_ids:
            return []

        conn = get_db_connection()
        cursor = conn.cursor()

        placeholders = ','.join('?' * len(document_ids))
        query = f'SELECT * FROM documents WHERE id IN ({placeholders})'

        cursor.execute(query, document_ids)
        rows = cursor.fetchall()

        conn.close()

        return [dict(row) for row in rows]

    @staticmethod
    def list_all() -> List[Dict]:
        """
        列出所有文档

        返回:
            文档列表
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM documents ORDER BY created_at DESC')
        rows = cursor.fetchall()

        conn.close()

        return [dict(row) for row in rows]


class Share:
    """分享记录模型"""

    @staticmethod
    def create(document_id: str, user_id: str, permission: str, shared_by: str) -> Dict:
        """
        创建分享记录

        参数:
            document_id: 文档 ID
            user_id: 被分享用户 ID
            permission: 权限类型 (viewer, editor)
            shared_by: 分享者 ID

        返回:
            分享记录字典
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        now = datetime.utcnow().isoformat()

        cursor.execute('''
            INSERT INTO shares (document_id, user_id, permission, shared_by, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (document_id, user_id, permission, shared_by, now))

        share_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return {
            'id': share_id,
            'document_id': document_id,
            'user_id': user_id,
            'permission': permission,
            'shared_by': shared_by,
            'created_at': now
        }

    @staticmethod
    def get_by_document(document_id: str) -> List[Dict]:
        """
        获取文档的所有分享记录

        参数:
            document_id: 文档 ID

        返回:
            分享记录列表
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM shares
            WHERE document_id = ?
            ORDER BY created_at DESC
        ''', (document_id,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    @staticmethod
    def delete(document_id: str, user_id: str) -> bool:
        """
        删除分享记录

        参数:
            document_id: 文档 ID
            user_id: 用户 ID

        返回:
            是否成功
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            DELETE FROM shares
            WHERE document_id = ? AND user_id = ?
        ''', (document_id, user_id))

        conn.commit()
        success = cursor.rowcount > 0
        conn.close()

        return success
