/**
 * API 服务模块
 * 封装所有后端 API 请求
 */

import type { User, Document, LoginRequest, LoginResponse } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * 获取认证 token
 */
function getAuthToken(): string | null {
  return localStorage.getItem(import.meta.env.VITE_AUTH_TOKEN_KEY || 'auth_token')
}

/**
 * 设置认证 token
 */
export function setAuthToken(token: string): void {
  localStorage.setItem(import.meta.env.VITE_AUTH_TOKEN_KEY || 'auth_token', token)
}

/**
 * 清除认证 token
 */
export function clearAuthToken(): void {
  localStorage.removeItem(import.meta.env.VITE_AUTH_TOKEN_KEY || 'auth_token')
}

/**
 * 获取认证 token（导出版本）
 */
export function getAuthToken(): string | null {
  return localStorage.getItem(import.meta.env.VITE_AUTH_TOKEN_KEY || 'auth_token')
}

/**
 * 通用请求函数
 */
async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken()

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      message: 'An error occurred',
    }))
    throw new Error(error.message || `HTTP ${response.status}`)
  }

  return response.json()
}

// ===== 认证 API =====

/**
 * 用户登录
 */
export async function login(credentials: LoginRequest): Promise<LoginResponse> {
  return fetchAPI<LoginResponse>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  })
}

/**
 * 用户注册
 */
export async function register(userData: LoginRequest): Promise<LoginResponse> {
  return fetchAPI<LoginResponse>('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify(userData),
  })
}

/**
 * 获取当前用户信息
 */
export async function getCurrentUser(): Promise<User> {
  return fetchAPI<User>('/api/auth/me')
}

/**
 * 用户登出
 */
export async function logout(): Promise<void> {
  await fetchAPI('/api/auth/logout', {
    method: 'POST',
  })
  clearAuthToken()
}

// ===== 文档 API =====

/**
 * 获取文档列表
 */
export async function getDocuments(): Promise<Document[]> {
  return fetchAPI<Document[]>('/api/documents')
}

/**
 * 获取单个文档
 */
export async function getDocument(id: string): Promise<Document> {
  return fetchAPI<Document>(`/api/documents/${id}`)
}

/**
 * 创建文档
 */
export async function createDocument(
  document: Omit<Document, 'id' | 'ownerId' | 'createdAt' | 'updatedAt'>
): Promise<Document> {
  return fetchAPI<Document>('/api/documents', {
    method: 'POST',
    body: JSON.stringify(document),
  })
}

/**
 * 更新文档
 */
export async function updateDocument(
  id: string,
  updates: Partial<Document>
): Promise<Document> {
  return fetchAPI<Document>(`/api/documents/${id}`, {
    method: 'PUT',
    body: JSON.stringify(updates),
  })
}

/**
 * 删除文档
 */
export async function deleteDocument(id: string): Promise<void> {
  await fetchAPI(`/api/documents/${id}`, {
    method: 'DELETE',
  })
}

/**
 * 分享文档
 */
export async function shareDocument(
  documentId: string,
  userId: string,
  permission: 'viewer' | 'editor'
): Promise<void> {
  await fetchAPI(`/api/documents/${documentId}/share`, {
    method: 'POST',
    body: JSON.stringify({ userId, permission }),
  })
}

/**
 * 取消文档分享
 */
export async function unshareDocument(
  documentId: string,
  userId: string
): Promise<void> {
  await fetchAPI(`/api/documents/${documentId}/share/${userId}`, {
    method: 'DELETE',
  })
}
