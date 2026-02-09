/**
 * 认证 Hook
 * 管理用户认证状态和相关操作
 */

import { useState, useEffect, useCallback } from 'react'
import * as api from '../services/api'
import type { User, LoginRequest } from '../types'

interface UseAuthReturn {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (credentials: LoginRequest) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

/**
 * 认证 Hook
 * 提供用户认证相关的状态和操作
 */
export function useAuth(): UseAuthReturn {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // 获取当前用户信息
  const refreshUser = useCallback(async () => {
    try {
      setIsLoading(true)
      const currentUser = await api.getCurrentUser()
      setUser(currentUser)
    } catch (error) {
      console.error('获取用户信息失败:', error)
      setUser(null)
      api.clearAuthToken()
    } finally {
      setIsLoading(false)
    }
  }, [])

  // 登录
  const login = useCallback(async (credentials: LoginRequest) => {
    setIsLoading(true)
    try {
      const response = await api.login(credentials)
      api.setAuthToken(response.token)
      setUser(response.user)
    } catch (error) {
      console.error('登录失败:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [])

  // 登出
  const logout = useCallback(() => {
    api.clearAuthToken()
    setUser(null)
  }, [])

  // 组件挂载时检查认证状态
  useEffect(() => {
    const token = api.getAuthToken()
    if (token) {
      refreshUser()
    } else {
      setIsLoading(false)
    }
  }, [refreshUser])

  return {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    refreshUser,
  }
}
