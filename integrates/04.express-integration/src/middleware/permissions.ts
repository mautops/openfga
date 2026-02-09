import { Response, NextFunction } from 'express';
import { AuthRequest } from '../types';
import { fgaClient } from '../config/openfga';

/**
 * OpenFGA 权限检查中间件工厂函数
 *
 * 这是一个高阶函数，返回一个中间件函数
 * 使用工厂模式的好处：
 * 1. 可以传入不同的权限要求（relation）
 * 2. 可以动态获取资源 ID（从路由参数）
 * 3. 灵活配置不同的权限检查策略
 *
 * @param relation - 需要检查的关系类型（如 'viewer', 'editor', 'owner'）
 * @param getObjectId - 从请求中获取对象 ID 的函数（默认从 req.params.id）
 * @returns Express 中间件函数
 *
 * 使用示例：
 * ```typescript
 * // 检查是否有 viewer 权限
 * router.get('/documents/:id',
 *   authenticateToken,
 *   checkPermission('viewer'),
 *   getDocument
 * );
 *
 * // 检查是否有 editor 权限
 * router.put('/documents/:id',
 *   authenticateToken,
 *   checkPermission('editor'),
 *   updateDocument
 * );
 * ```
 */
export const checkPermission = (
  relation: 'viewer' | 'editor' | 'owner',
  getObjectId?: (req: AuthRequest) => string
) => {
  return async (
    req: AuthRequest,
    res: Response,
    next: NextFunction
  ): Promise<void> => {
    try {
      // 确保用户已认证
      if (!req.user) {
        res.status(401).json({
          error: 'Unauthorized',
          message: '用户未认证',
        });
        return;
      }

      // 获取资源 ID（默认从 URL 参数中获取）
      const objectId = getObjectId
        ? getObjectId(req)
        : req.params.id;

      if (!objectId) {
        res.status(400).json({
          error: 'Bad Request',
          message: '缺少资源 ID',
        });
        return;
      }

      // 构造 OpenFGA 检查请求
      const checkRequest = {
        user: `user:${req.user.userId}`,
        relation: relation,
        object: `document:${objectId}`,
      };

      console.log('[Permission Check]', checkRequest);

      // 调用 OpenFGA API 检查权限
      const { allowed } = await fgaClient.check(checkRequest);

      console.log('[Permission Result]', { allowed, relation, objectId });

      // 如果没有权限，返回 403 禁止访问
      if (!allowed) {
        res.status(403).json({
          error: 'Forbidden',
          message: `您没有权限执行此操作（需要 ${relation} 权限）`,
          required: relation,
          user: req.user.userId,
          resource: objectId,
        });
        return;
      }

      // 权限检查通过，继续下一个中间件
      next();
    } catch (error) {
      console.error('[Permission Check Error]', error);

      // 将错误传递给错误处理中间件
      next(error);
    }
  };
};

/**
 * 批量权限检查中间件
 *
 * 用于检查用户是否对多个资源具有特定权限
 * 适用于批量操作场景
 *
 * @param relation - 需要检查的关系类型
 * @param getObjectIds - 从请求中获取对象 ID 列表的函数
 */
export const checkBatchPermissions = (
  relation: 'viewer' | 'editor' | 'owner',
  getObjectIds: (req: AuthRequest) => string[]
) => {
  return async (
    req: AuthRequest,
    res: Response,
    next: NextFunction
  ): Promise<void> => {
    try {
      if (!req.user) {
        res.status(401).json({
          error: 'Unauthorized',
          message: '用户未认证',
        });
        return;
      }

      const objectIds = getObjectIds(req);

      if (!objectIds || objectIds.length === 0) {
        res.status(400).json({
          error: 'Bad Request',
          message: '缺少资源 ID 列表',
        });
        return;
      }

      // 并行检查所有资源的权限
      const checkPromises = objectIds.map(async (objectId) => {
        const { allowed } = await fgaClient.check({
          user: `user:${req.user!.userId}`,
          relation: relation,
          object: `document:${objectId}`,
        });
        return { objectId, allowed };
      });

      const results = await Promise.all(checkPromises);

      // 找出没有权限的资源
      const deniedResources = results
        .filter(r => !r.allowed)
        .map(r => r.objectId);

      if (deniedResources.length > 0) {
        res.status(403).json({
          error: 'Forbidden',
          message: '您对部分资源没有权限',
          deniedResources,
          required: relation,
        });
        return;
      }

      // 所有权限检查通过
      next();
    } catch (error) {
      console.error('[Batch Permission Check Error]', error);
      next(error);
    }
  };
};
