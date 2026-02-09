import { Router, Response } from 'express';
import jwt from 'jsonwebtoken';
import { AuthRequest } from '../types';
import { authenticateToken } from '../middleware/auth';

const router = Router();

/**
 * 登录接口
 * POST /auth/login
 *
 * 功能：
 * 1. 验证用户凭证（简化示例，实际应查询数据库）
 * 2. 生成 JWT token
 * 3. 返回 token 给客户端
 *
 * 请求体：
 * {
 *   "email": "user@example.com",
 *   "password": "password123"
 * }
 */
router.post('/login', async (req: AuthRequest, res: Response) => {
  try {
    const { email, password } = req.body;

    // 验证必填字段
    if (!email || !password) {
      res.status(400).json({
        error: 'Missing credentials',
        message: '邮箱和密码不能为空'
      });
      return;
    }

    // 简化的用户验证（实际应用中应该查询数据库并验证密码哈希）
    // 这里使用硬编码的测试用户
    const testUsers = [
      { userId: 'user:alice', email: 'alice@example.com', password: 'password123' },
      { userId: 'user:bob', email: 'bob@example.com', password: 'password123' },
      { userId: 'user:charlie', email: 'charlie@example.com', password: 'password123' }
    ];

    const user = testUsers.find(u => u.email === email && u.password === password);

    if (!user) {
      res.status(401).json({
        error: 'Invalid credentials',
        message: '邮箱或密码错误'
      });
      return;
    }

    // 生成 JWT token
    const jwtSecret = process.env.JWT_SECRET || 'default-secret-key';
    const expiresIn = process.env.JWT_EXPIRES_IN || '24h';

    const token = jwt.sign(
      {
        userId: user.userId,
        email: user.email
      },
      jwtSecret,
      { expiresIn }
    );

    // 返回成功响应
    res.json({
      message: '登录成功',
      token,
      user: {
        userId: user.userId,
        email: user.email
      }
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: '登录失败，请稍后重试'
    });
  }
});

/**
 * 获取当前用户信息
 * GET /auth/me
 *
 * 需要认证：是
 *
 * 功能：
 * 1. 通过 JWT token 获取当前登录用户信息
 * 2. 返回用户基本信息
 */
router.get('/me', authenticateToken, (req: AuthRequest, res: Response) => {
  // authenticateToken 中间件已经验证了 token 并将用户信息附加到 req.user
  res.json({
    message: '获取用户信息成功',
    user: req.user
  });
});

/**
 * 刷新 token
 * POST /auth/refresh
 *
 * 需要认证：是
 *
 * 功能：
 * 1. 使用现有的有效 token 生成新的 token
 * 2. 延长用户登录时间
 */
router.post('/refresh', authenticateToken, (req: AuthRequest, res: Response) => {
  try {
    const user = req.user!;

    // 生成新的 JWT token
    const jwtSecret = process.env.JWT_SECRET || 'default-secret-key';
    const expiresIn = process.env.JWT_EXPIRES_IN || '24h';

    const newToken = jwt.sign(
      {
        userId: user.userId,
        email: user.email
      },
      jwtSecret,
      { expiresIn }
    );

    res.json({
      message: 'Token 刷新成功',
      token: newToken,
      user: {
        userId: user.userId,
        email: user.email
      }
    });
  } catch (error) {
    console.error('Token refresh error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'Token 刷新失败'
    });
  }
});

export default router;
