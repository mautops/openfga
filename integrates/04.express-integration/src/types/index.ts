import { Request } from 'express';

/**
 * JWT Payload 接口
 * 定义 JWT token 中包含的用户信息
 */
export interface JwtPayload {
  userId: string;
  email: string;
  iat?: number;
  exp?: number;
}

/**
 * 扩展 Express Request 接口
 * 添加 user 属性，用于在中间件之间传递认证用户信息
 */
export interface AuthRequest extends Request {
  user?: JwtPayload;
}

/**
 * 文档接口
 * 定义文档的数据结构
 */
export interface Document {
  id: string;
  title: string;
  content: string;
  ownerId: string;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * 创建文档请求体
 */
export interface CreateDocumentRequest {
  title: string;
  content: string;
}

/**
 * 更新文档请求体
 */
export interface UpdateDocumentRequest {
  title?: string;
  content?: string;
}

/**
 * 登录请求体
 */
export interface LoginRequest {
  email: string;
  password: string;
}

/**
 * 登录响应
 */
export interface LoginResponse {
  token: string;
  user: {
    userId: string;
    email: string;
  };
}

/**
 * API 错误响应
 */
export interface ApiError {
  error: string;
  message: string;
  details?: any;
}

/**
 * OpenFGA 权限检查选项
 */
export interface PermissionCheckOptions {
  relation: 'owner' | 'editor' | 'viewer';
  objectType: 'document';
}
