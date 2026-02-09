/**
 * 类型定义文件
 * 定义应用中使用的所有 TypeScript 类型和接口
 */

// ===== 用户相关类型 =====
export interface User {
  id: string
  username: string
  email: string
  name?: string
}

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
}

// ===== 文档相关类型 =====
export interface Document {
  id: string
  title: string
  content: string
  ownerId: string
  createdAt: string
  updatedAt: string
}

export interface DocumentListItem {
  id: string
  title: string
  ownerId: string
  createdAt: string
  canView: boolean
  canEdit: boolean
  canDelete: boolean
  canShare: boolean
}

// ===== 权限相关类型 =====
export type PermissionRelation = 'owner' | 'editor' | 'viewer'

export interface Permission {
  userId: string
  documentId: string
  relation: PermissionRelation
}

export interface CheckPermissionRequest {
  user: string
  relation: string
  object: string
}

export interface CheckPermissionResponse {
  allowed: boolean
}

export interface PermissionCache {
  [key: string]: {
    allowed: boolean
    timestamp: number
  }
}

// ===== API 响应类型 =====
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  hasMore: boolean
}

// ===== 分享相关类型 =====
export interface ShareRequest {
  documentId: string
  userId: string
  relation: PermissionRelation
}

export interface ShareResponse {
  success: boolean
  message: string
}

// ===== 登录相关类型 =====
export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  token: string
  user: User
}
