import { Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { AuthRequest, JwtPayload } from '../types';

/**
 * JWT 认证中间件
 *
 * 功能：
 * 1. 从请求头中提取 JWT token
 * 2. 验证 token 的有效性
 * 3. 解析 token 中的用户信息
 * 4. 将用户信息附加到 req.user
 *
 * 使用方式：
 * - 在需要认证的路由上使用：router.get('/path', authenticateToken, handler)
 * - 在路由处理器中通过 req.user 访问当前用户信息
 */
export const authenticateToken = (
  req: AuthRequest,
  res: Response,
  next: NextFunction
): void => {
  try {
    // 从 Authorization 头中提取 token
    // 格式：Authorization: Bearer <token>
    const authHeader = req.headers.authorization;
    const token = authHeader && authHeader.split(' ')[1];

    // 如果没有 token，返回 401 未授权
    if (!token) {
      res.status(401).json({
        error: 'Unauthorized',
        message: '缺少认证 token，请先登录',
      });
      return;
    }

    // 验证 token 并解析
    const jwtSecret = process.env.JWT_SECRET;
    if (!jwtSecret) {
      throw new Error('JWT_SECRET 未配置');
    }

    const decoded = jwt.verify(token, jwtSecret) as JwtPayload;

    // 将用户信息附加到请求对象
    req.user = decoded;

    // 继续下一个中间件
    next();
  } catch (error) {
    // token 无效或已过期
    if (error instanceof jwt.JsonWebTokenError) {
      res.status(401).json({
        error: 'Unauthorized',
        message: 'Token 无效',
      });
      return;
    }

    if (error instanceof jwt.TokenExpiredError) {
      res.status(401).json({
        error: 'Unauthorized',
        message: 'Token 已过期，请重新登录',
      });
      return;
    }

    // 其他错误
    next(error);
  }
};

/**
 * 生成 JWT token
 *
 * @param payload - 用户信息
 * @returns JWT token 字符串
 */
export const generateToken = (payload: Omit<JwtPayload, 'iat' | 'exp'>): string => {
  const jwtSecret = process.env.JWT_SECRET;
  const expiresIn = process.env.JWT_EXPIRES_IN || '24h';

  if (!jwtSecret) {
    throw new Error('JWT_SECRET 未配置');
  }

  return jwt.sign(payload, jwtSecret, { expiresIn });
};
