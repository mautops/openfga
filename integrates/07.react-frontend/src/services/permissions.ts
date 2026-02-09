/**
 * 权限服务模块
 * 封装 OpenFGA 权限检查逻辑
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * 获取认证 token
 */
function getAuthToken(): string | null {
  return localStorage.getItem(import.meta.env.VITE_AUTH_TOKEN_KEY || 'auth_token')
}

/**
 * 权限检查请求接口
 */
export interface PermissionCheckRequest {
  object: {
    type: string
    id: string
  }
  relation: string
}

/**
 * 权限检查响应接口
 */
export interface PermissionCheckResponse {
  allowed: boolean
}

/**
 * 权限缓存类
 */
class PermissionCache {
  private cache = new Map<string, { result: boolean; timestamp: number }>()
  private readonly TTL = 5 * 60 * 1000 // 5分钟缓存

  /**
   * 生成缓存键
   */
  private getKey(objectType: string, objectId: string, relation: string): string {
    return `${objectType}:${objectId}:${relation}`
  }

  /**
   * 获取缓存
   */
  get(objectType: string, objectId: string, relation: string): boolean | null {
    const key = this.getKey(objectType, objectId, relation)
    const cached = this.cache.get(key)

    if (!cached) return null

    // 检查是否过期
    if (Date.now() - cached.timestamp > this.TTL) {
      this.cache.delete(key)
      return null
    }

    return cached.result
  }

  /**
   * 设置缓存
   */
  set(objectType: string, objectId: string, relation: string, result: boolean): void {
    const key = this.getKey(objectType, objectId, relation)
    this.cache.set(key, {
      result,
      timestamp: Date.now(),
    })
  }

  /**
   * 清除缓存
   */
  clear(objectType?: string, objectId?: string, relation?: string): void {
    if (!objectType && !objectId && !relation) {
      this.cache.clear()
      return
    }

    // 清除匹配的缓存项
    for (const [key] of this.cache) {
      const [type, id, rel] = key.split(':')
      let shouldDelete = true

      if (objectType && objectType !== type) shouldDelete = false
      if (objectId && objectId !== id) shouldDelete = false
      if (relation && relation !== rel) shouldDelete = false

      if (shouldDelete) {
        this.cache.delete(key)
      }
    }
  }
}

// 创建全局权限缓存实例
const permissionCache = new PermissionCache()

/**
 * 检查单个权限
 */
export async function checkPermission(
  request: PermissionCheckRequest,
  useCache: boolean = true
): Promise<PermissionCheckResponse> {
  const { object, relation } = request

  // 先检查缓存
  if (useCache) {
    const cached = permissionCache.get(object.type, object.id, relation)
    if (cached !== null) {
      return { allowed: cached }
    }
  }

  // 发送请求
  const token = getAuthToken()
  const response = await fetch(`${API_BASE_URL}/api/permissions/check`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    throw new Error('Failed to check permission')
  }

  const data: PermissionCheckResponse = await response.json()

  // 更新缓存
  if (useCache) {
    permissionCache.set(object.type, object.id, relation, data.allowed)
  }

  return data
}

/**
 * 批量检查权限
 */
export async function checkBatchPermissions(
  requests: PermissionCheckRequest[],
  useCache: boolean = true
): Promise<PermissionCheckResponse[]> {
  // 分离已缓存和未缓存的请求
  const results: (PermissionCheckResponse | null)[] = requests.map((req) => {
    if (!useCache) return null
    const cached = permissionCache.get(req.object.type, req.object.id, req.relation)
    return cached !== null ? { allowed: cached } : null
  })

  const uncachedRequests = requests.filter((_, index) => results[index] === null)
  const uncachedIndices = results
    .map((result, index) => (result === null ? index : -1))
    .filter((index) => index !== -1)

  // 如果全部都已缓存，直接返回
  if (uncachedRequests.length === 0) {
    return results as PermissionCheckResponse[]
  }

  // 批量请求未缓存的权限
  const token = getAuthToken()
  const response = await fetch(`${API_BASE_URL}/api/permissions/batch-check`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    },
    body: JSON.stringify({ checks: uncachedRequests }),
  })

  if (!response.ok) {
    throw new Error('Failed to check permissions')
  }

  const data: { results: PermissionCheckResponse[] } = await response.json()

  // 更新缓存
  if (useCache) {
    uncachedRequests.forEach((req, index) => {
      permissionCache.set(
        req.object.type,
        req.object.id,
        req.relation,
        data.results[index].allowed
      )
    })
  }

  // 合并结果
  uncachedIndices.forEach((originalIndex, dataIndex) => {
    results[originalIndex] = data.results[dataIndex]
  })

  return results as PermissionCheckResponse[]
}

/**
 * 清除权限缓存
 */
export function clearPermissionCache(
  objectType?: string,
  objectId?: string,
  relation?: string
): void {
  permissionCache.clear(objectType, objectId, relation)
}
