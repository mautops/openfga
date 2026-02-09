/**
 * 权限门控组件
 * 根据用户权限决定是否渲染子组件
 */

import { usePermission } from '../hooks/usePermissions'

interface PermissionGateProps {
  /** 资源类型（如 'document'） */
  objectType: string
  /** 资源 ID */
  objectId: string
  /** 权限关系（如 'can_view', 'can_edit'） */
  relation: string
  /** 无权限时显示的内容（可选） */
  fallback?: React.ReactNode
  /** 加载中显示的内容（可选） */
  loading?: React.ReactNode
  /** 有权限时渲染的子组件 */
  children: React.ReactNode
}

/**
 * 权限门控组件
 * 检查用户是否有指定权限，有权限则渲染子组件，否则渲染 fallback
 */
export function PermissionGate({
  objectType,
  objectId,
  relation,
  fallback = null,
  loading = null,
  children,
}: PermissionGateProps) {
  const { hasPermission, isLoading } = usePermission({
    object: {
      type: objectType,
      id: objectId,
    },
    relation,
  })

  // 加载中
  if (isLoading) {
    return <>{loading}</>
  }

  // 有权限则渲染子组件，否则渲染 fallback
  return <>{hasPermission ? children : fallback}</>
}

interface PermissionButtonProps {
  /** 资源类型 */
  objectType: string
  /** 资源 ID */
  objectId: string
  /** 权限关系 */
  relation: string
  /** 按钮点击事件 */
  onClick: () => void
  /** 按钮样式类名 */
  className?: string
  /** 按钮文本 */
  children: React.ReactNode
}

/**
 * 基于权限的按钮组件
 * 只有当用户有指定权限时才显示按钮
 */
export function PermissionButton({
  objectType,
  objectId,
  relation,
  onClick,
  className = '',
  children,
}: PermissionButtonProps) {
  return (
    <PermissionGate objectType={objectType} objectId={objectId} relation={relation}>
      <button onClick={onClick} className={className}>
        {children}
      </button>
    </PermissionGate>
  )
}
