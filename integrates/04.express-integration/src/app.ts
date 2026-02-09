import express, { Express, Request, Response, NextFunction } from 'express';
import dotenv from 'dotenv';
import authRoutes from './routes/auth';
import documentRoutes from './routes/documents';

// 加载环境变量
dotenv.config();

/**
 * 创建 Express 应用实例
 */
const app: Express = express();
const PORT = process.env.PORT || 3000;

/**
 * 内置中间件
 * - express.json(): 解析 JSON 请求体
 * - express.urlencoded(): 解析 URL 编码的请求体
 */
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

/**
 * 自定义日志中间件
 * 记录每个请求的方法、路径和时间戳
 */
app.use((req: Request, res: Response, next: NextFunction) => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] ${req.method} ${req.url}`);
  next();
});

/**
 * 健康检查接口
 * GET /health
 */
app.get('/health', (req: Request, res: Response) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
  });
});

/**
 * 根路径
 * GET /
 */
app.get('/', (req: Request, res: Response) => {
  res.json({
    message: 'Express + OpenFGA 集成示例 API',
    version: '1.0.0',
    endpoints: {
      health: 'GET /health',
      auth: {
        login: 'POST /auth/login',
        profile: 'GET /auth/profile',
      },
      documents: {
        create: 'POST /documents',
        list: 'GET /documents',
        get: 'GET /documents/:id',
        update: 'PUT /documents/:id',
        delete: 'DELETE /documents/:id',
      },
    },
  });
});

/**
 * 注册路由
 */
app.use('/auth', authRoutes);
app.use('/documents', documentRoutes);

/**
 * 404 处理中间件
 * 捕获所有未定义的路由
 */
app.use((req: Request, res: Response) => {
  res.status(404).json({
    error: 'Not Found',
    message: `路由 ${req.method} ${req.url} 不存在`,
  });
});

/**
 * 全局错误处理中间件
 *
 * 必须有 4 个参数 (err, req, res, next) 才能被识别为错误处理中间件
 * 必须定义在所有其他中间件和路由之后
 *
 * 功能：
 * 1. 捕获所有错误
 * 2. 记录错误日志
 * 3. 返回统一格式的错误响应
 * 4. 开发环境下返回错误堆栈
 */
app.use((err: any, req: Request, res: Response, next: NextFunction) => {
  console.error('错误:', err.message);
  console.error('堆栈:', err.stack);

  const statusCode = err.statusCode || err.status || 500;
  const message = err.message || '服务器内部错误';

  res.status(statusCode).json({
    error: message,
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack }),
  });
});

/**
 * 启动服务器
 */
app.listen(PORT, () => {
  console.log(`✨ 服务器运行在 http://localhost:${PORT}`);
  console.log(`📝 环境: ${process.env.NODE_ENV || 'development'}`);
  console.log(`🔐 OpenFGA API: ${process.env.FGA_API_URL}`);
  console.log(`\n📚 API 文档:`);
  console.log(`   - 健康检查: GET http://localhost:${PORT}/health`);
  console.log(`   - 登录: POST http://localhost:${PORT}/auth/login`);
  console.log(`   - 文档管理: http://localhost:${PORT}/documents`);
});

export default app;
