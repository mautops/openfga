/**
 * 权限检查 Hook
 * 提供基于 OpenFGA 的权限检查功能
 */

import { useState, useEffect, useCallback } from 'react'
import {
  checkPermission,
  checkBatchPermissions,
  clearPermissionCache,
  type PermissionCheckRequest,
} from '../services/permissions'

interface UsePermissionReturn {
  hasPermission: boolean
  isLoading: boolean
  error: Error | null
  refetch: () => Promise<void>
}

/**
 * 单个权限检查 Hook
 * @param request 权限检查请求参数
 * @param options 选项
 * @returns 权限检查结果
 */
export function usePermission(
  request: PermissionCheckRequest | null,
  options: {
    enabled?: boolean // 是否启用自动检查
    useCache?: boolean // 是否使用缓存
  } = {}
): UsePermissionReturn {
  const { enabled = true, useCache = true } = options

  const [hasPermission, setHasPermission] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  // 执行权限检查
  const checkPerm = useCallback(async () => {
    if (!request || !enabled) {
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const result = await checkPermission(request, useCache)
      setHasPermission(result.allowed)
    } catch (err) {
      const error = err instanceof Error ? err : new Error('权限检查失败')
      setError(error)
      setHasPermission(false)
      console.error('权限检查失败:', error)
    } finally {
      setIsLoading(false)
    }
  }, [request, enabled, useCache])

  // 手动刷新
  const refetch = useCallback(async () => {
    await checkPerm()
  }, [checkPerm])

  // 自动执行权限检查
  useEffect(() => {
    checkPerm()
  }, [checkPerm])

  return {
    hasPermission,
    isLoading,
    error,
    refetch,
  }
}

interface UseBatchPermissionsReturn {
  permissions: Record<string, boolean>
  isLoading: boolean
  error: Error | null
  refetch: () => Promise<void>
}

/**
 * 批量权限检查 Hook
 * @param requests 权限检查请求数组
 * @param options 选项
 * @returns 批量权限检查结果
 */
export function useBatchPermissions(
  requests: PermissionCheckRequest[],
  options: {
    enabled?: boolean
    useCache?: boolean
  } = {}
): UseBatchPermissionsReturn {
  const { enabled = true, useCache = true } = options

  const [permissions, setPermissions] = useState<Record<string, boolean>>({})
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  // 执行批量权限检查
  const checkPerms = useCallback(async () => {
    if (!requests.length || !enabled) {
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const results = await checkBatchPermissions(requests, useCache)

      // 将结果转换为对象格式
      const permsMap: Record<string, boolean> = {}
      results.forEach((result, index) => {
        const req = requests[index]
        const key = `${req.object.type}:${req.object.id}:${req.relation}`
        permsMap[key] = result.allowed
      })

      setPermissions(permsMap)
    } catch (err) {
      const error = err instanceof Error ? err : new Error('批量权限检查失败')
      setError(error)
      console.error('批量权限检查失败:', error)
    } finally {
      setIsLoading(false)
    }
  }, [requests, enabled, useCache])

  // 手动刷新
  const refetch = useCallback(async () => {
    await checkPerms()
  }, [checkPerms])

  // 自动执行权限检查
  useEffect(() => {
    checkPerms()
  }, [checkPerms])

  return {
    permissions,
    isLoading,
    error,
    refetch,
  }
}

/**
 * 资源权限 Hook
 * 检查当前用户对特定资源的多个权限
 * @param resourceType 资源类型
 * @param resourceId 资源 ID
 * @param relations 要检查的关系列表
 * @returns 权限检查结果
 */
export function useResourcePermissions(
  resourceType: string,
  resourceId: string,
  relations: string[]
): {
  permissions: Record<string, boolean>
  isLoading: boolean
  error: Error | null
  refetch: () => Promise<void>
  clearCache: () => void
} {
  // 构建批量检查请求
  const requests: PermissionCheckRequest[] = relations.map((relation) => ({
    object: {
      type: resourceType,
      id: resourceId,
    },
    relation,
  }))

  const result = useBatchPermissions(requests)

  // 清除该资源的权限缓存
  const clearCache = useCallback(() => {
    relations.forEach((relation) => {
      clearPermissionCache(resourceType, resourceId, relation)
    })
  }, [resourceType, resourceId, relations])

  // 将数组格式的权限结果转换为按 relation 索引的对象
  const permissions: Record<string, boolean> = {}
  relations.forEach((relation) => {
    const key = `${resourceType}:${resourceId}:${relation}`
    permissions[relation] = result.permissions[key] || false
  })

  return {
    permissions,
    isLoading: result.isLoading,
    error: result.error,
    refetch: result.refetch,
    clearCache,
  }
}
