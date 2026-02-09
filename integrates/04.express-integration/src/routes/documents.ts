import { Router, Response } from 'express';
import { v4 as uuidv4 } from 'uuid';
import { AuthRequest, Document } from '../types';
import { authenticateToken } from '../middleware/auth';
import { checkPermission } from '../middleware/permissions';
import { fgaClient } from '../config/openfga';

const router = Router();

/**
 * 内存数据库（简化示例）
 * 实际应用中应使用真实的数据库（如 PostgreSQL, MongoDB 等）
 */
const documentsDB: Map<string, Document> = new Map();

/**
 * 创建文档
 * POST /documents
 *
 * 需要认证：是
 * 需要权限：无（任何认证用户都可以创建文档）
 *
 * 功能：
 * 1. 创建新文档
 * 2. 自动将创建者设置为文档所有者
 * 3. 在 OpenFGA 中写入所有者关系
 *
 * 请求体：
 * {
 *   "title": "文档标题",
 *   "content": "文档内容"
 * }
 */
router.post('/', authenticateToken, async (req: AuthRequest, res: Response) => {
  try {
    const { title, content } = req.body;
    const user = req.user!;

    // 验证必填字段
    if (!title || !content) {
      res.status(400).json({
        error: 'Missing required fields',
        message: '标题和内容不能为空'
      });
      return;
    }

    // 创建文档
    const documentId = uuidv4();
    const document: Document = {
      id: documentId,
      title,
      content,
      createdAt: new Date(),
      updatedAt: new Date(),
      ownerId: user.userId
    };

    documentsDB.set(documentId, document);

    // 在 OpenFGA 中写入所有者关系
    // 这样创建者就拥有文档的所有权限（owner, editor, viewer）
    try {
      await fgaClient.write({
        writes: [
          {
            user: user.userId,
            relation: 'owner',
            object: `document:${documentId}`
          }
        ]
      });
    } catch (fgaError) {
      console.error('OpenFGA write error:', fgaError);
      // 如果 OpenFGA 写入失败，回滚文档创建
      documentsDB.delete(documentId);
      throw fgaError;
    }

    res.status(201).json({
      message: '文档创建成功',
      document: {
        id: document.id,
        title: document.title,
        content: document.content,
        createdAt: document.createdAt,
        updatedAt: document.updatedAt
      }
    });
  } catch (error) {
    console.error('Create document error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: '创建文档失败'
    });
  }
});

/**
 * 获取文档列表
 * GET /documents
 *
 * 需要认证：是
 *
 * 功能：
 * 1. 返回用户有权限查看的所有文档
 * 2. 简化示例：返回所有文档（实际应该通过 OpenFGA 过滤）
 */
router.get('/', authenticateToken, async (req: AuthRequest, res: Response) => {
  try {
    const documents = Array.from(documentsDB.values()).map(doc => ({
      id: doc.id,
      title: doc.title,
      createdAt: doc.createdAt,
      updatedAt: doc.updatedAt
    }));

    res.json({
      message: '获取文档列表成功',
      documents,
      total: documents.length
    });
  } catch (error) {
    console.error('List documents error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: '获取文档列表失败'
    });
  }
});

/**
 * 获取文档详情
 * GET /documents/:id
 *
 * 需要认证：是
 * 需要权限：viewer（查看者权限）
 *
 * 功能：
 * 1. 检查用户是否有 viewer 权限
 * 2. 返回文档详细内容
 */
router.get(
  '/:id',
  authenticateToken,
  checkPermission('viewer'),
  (req: AuthRequest, res: Response) => {
    try {
      const { id } = req.params;
      const document = documentsDB.get(id);

      if (!document) {
        res.status(404).json({
          error: 'Not found',
          message: '文档不存在'
        });
        return;
      }

      res.json({
        message: '获取文档成功',
        document: {
          id: document.id,
          title: document.title,
          content: document.content,
          createdAt: document.createdAt,
          updatedAt: document.updatedAt
        }
      });
    } catch (error) {
      console.error('Get document error:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: '获取文档失败'
      });
    }
  }
);

/**
 * 更新文档
 * PUT /documents/:id
 *
 * 需要认证：是
 * 需要权限：editor（编辑者权限）
 *
 * 功能：
 * 1. 检查用户是否有 editor 权限
 * 2. 更新文档内容
 *
 * 请求体：
 * {
 *   "title": "新标题",
 *   "content": "新内容"
 * }
 */
router.put(
  '/:id',
  authenticateToken,
  checkPermission('editor'),
  (req: AuthRequest, res: Response) => {
    try {
      const { id } = req.params;
      const { title, content } = req.body;
      const document = documentsDB.get(id);

      if (!document) {
        res.status(404).json({
          error: 'Not found',
          message: '文档不存在'
        });
        return;
      }

      // 更新文档
      if (title !== undefined) document.title = title;
      if (content !== undefined) document.content = content;
      document.updatedAt = new Date();

      documentsDB.set(id, document);

      res.json({
        message: '文档更新成功',
        document: {
          id: document.id,
          title: document.title,
          content: document.content,
          createdAt: document.createdAt,
          updatedAt: document.updatedAt
        }
      });
    } catch (error) {
      console.error('Update document error:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: '更新文档失败'
      });
    }
  }
);

/**
 * 删除文档
 * DELETE /documents/:id
 *
 * 需要认证：是
 * 需要权限：owner（所有者权限）
 *
 * 功能：
 * 1. 检查用户是否有 owner 权限
 * 2. 删除文档
 * 3. 清理 OpenFGA 中的相关关系
 */
router.delete(
  '/:id',
  authenticateToken,
  checkPermission('owner'),
  async (req: AuthRequest, res: Response) => {
    try {
      const { id } = req.params;
      const document = documentsDB.get(id);

      if (!document) {
        res.status(404).json({
          error: 'Not found',
          message: '文档不存在'
        });
        return;
      }

      // 从数据库中删除文档
      documentsDB.delete(id);

      // 清理 OpenFGA 中的关系
      // 实际应用中应该读取所有相关关系并删除
      try {
        await fgaClient.write({
          deletes: [
            {
              user: document.ownerId,
              relation: 'owner',
              object: `document:${id}`
            }
          ]
        });
      } catch (fgaError) {
        console.error('OpenFGA delete error:', fgaError);
        // 即使 OpenFGA 清理失败，也不影响文档删除
      }

      res.json({
        message: '文档删除成功'
      });
    } catch (error) {
      console.error('Delete document error:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: '删除文档失败'
      });
    }
  }
);

/**
 * 分享文档（授予权限）
 * POST /documents/:id/share
 *
 * 需要认证：是
 * 需要权限：owner（所有者权限）
 *
 * 功能：
 * 1. 检查用户是否有 owner 权限
 * 2. 为其他用户授予指定权限（viewer 或 editor）
 * 3. 在 OpenFGA 中写入关系
 *
 * 请求体：
 * {
 *   "userId": "user:bob",
 *   "relation": "viewer" | "editor"
 * }
 */
router.post(
  '/:id/share',
  authenticateToken,
  checkPermission('owner'),
  async (req: AuthRequest, res: Response) => {
    try {
      const { id } = req.params;
      const { userId, relation } = req.body;

      // 验证必填字段
      if (!userId || !relation) {
        res.status(400).json({
          error: 'Missing required fields',
          message: '用户 ID 和权限类型不能为空'
        });
        return;
      }

      // 验证权限类型
      if (!['viewer', 'editor'].includes(relation)) {
        res.status(400).json({
          error: 'Invalid relation',
          message: '权限类型必须是 viewer 或 editor'
        });
        return;
      }

      // 检查文档是否存在
      const document = documentsDB.get(id);
      if (!document) {
        res.status(404).json({
          error: 'Not found',
          message: '文档不存在'
        });
        return;
      }

      // 在 OpenFGA 中写入关系
      await fgaClient.write({
        writes: [
          {
            user: userId,
            relation: relation,
            object: `document:${id}`
          }
        ]
      });

      res.json({
        message: '分享成功',
        share: {
          documentId: id,
          userId,
          relation
        }
      });
    } catch (error) {
      console.error('Share document error:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: '分享文档失败'
      });
    }
  }
);

/**
 * 撤销文档权限
 * DELETE /documents/:id/share
 *
 * 需要认证：是
 * 需要权限：owner（所有者权限）
 *
 * 功能：
 * 1. 检查用户是否有 owner 权限
 * 2. 撤销其他用户的权限
 * 3. 从 OpenFGA 中删除关系
 *
 * 请求体：
 * {
 *   "userId": "user:bob",
 *   "relation": "viewer" | "editor"
 * }
 */
router.delete(
  '/:id/share',
  authenticateToken,
  checkPermission('owner'),
  async (req: AuthRequest, res: Response) => {
    try {
      const { id } = req.params;
      const { userId, relation } = req.body;

      // 验证必填字段
      if (!userId || !relation) {
        res.status(400).json({
          error: 'Missing required fields',
          message: '用户 ID 和权限类型不能为空'
        });
        return;
      }

      // 检查文档是否存在
      const document = documentsDB.get(id);
      if (!document) {
        res.status(404).json({
          error: 'Not found',
          message: '文档不存在'
        });
        return;
      }

      // 从 OpenFGA 中删除关系
      await fgaClient.write({
        deletes: [
          {
            user: userId,
            relation: relation,
            object: `document:${id}`
          }
        ]
      });

      res.json({
        message: '权限撤销成功'
      });
    } catch (error) {
      console.error('Revoke permission error:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: '撤销权限失败'
      });
    }
  }
);

export default router;
