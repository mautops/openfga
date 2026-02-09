/**
 * 文档编辑器组件
 * 提供文档查看和编辑功能，根据权限显示不同的操作按钮
 */

import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import * as api from '../services/api'
import type { Document } from '../types'
import { PermissionGate, PermissionButton } from './PermissionGate'
import { useBatchPermissions } from '../hooks/usePermissions'

export function DocumentEditor() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [document, setDocument] = useState<Document | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [editedTitle, setEditedTitle] = useState('')
  const [editedContent, setEditedContent] = useState('')
  const [isSaving, setIsSaving] = useState(false)

  // 批量检查权限
  const { permissions, isLoading: permissionsLoading } = useBatchPermissions(
    id
      ? [
          { object: { type: 'document', id }, relation: 'can_view' },
          { object: { type: 'document', id }, relation: 'can_edit' },
          { object: { type: 'document', id }, relation: 'can_delete' },
          { object: { type: 'document', id }, relation: 'can_share' },
        ]
      : []
  )

  // 加载文档
  useEffect(() => {
    if (!id) {
      setError('文档 ID 不存在')
      setIsLoading(false)
      return
    }

    loadDocument()
  }, [id])

  const loadDocument = async () => {
    if (!id) return

    try {
      setIsLoading(true)
      setError(null)
      const doc = await api.getDocument(id)
      setDocument(doc)
      setEditedTitle(doc.title)
      setEditedContent(doc.content)
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载文档失败')
    } finally {
      setIsLoading(false)
    }
  }

  // 保存文档
  const handleSave = async () => {
    if (!id || !document) return

    try {
      setIsSaving(true)
      const updated = await api.updateDocument(id, {
        title: editedTitle,
        content: editedContent,
      })
      setDocument(updated)
      setIsEditing(false)
    } catch (err) {
      alert(err instanceof Error ? err.message : '保存失败')
    } finally {
      setIsSaving(false)
    }
  }

  // 取消编辑
  const handleCancel = () => {
    setEditedTitle(document?.title || '')
    setEditedContent(document?.content || '')
    setIsEditing(false)
  }

  // 删除文档
  const handleDelete = async () => {
    if (!id || !confirm('确定要删除这个文档吗？')) return

    try {
      await api.deleteDocument(id)
      navigate('/documents')
    } catch (err) {
      alert(err instanceof Error ? err.message : '删除失败')
    }
  }

  // 分享文档
  const handleShare = () => {
    // 这里可以实现分享功能，比如显示分享对话框
    alert('分享功能待实现')
  }

  if (isLoading || permissionsLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">加载中...</p>
        </div>
      </div>
    )
  }

  if (error || !document) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || '文档不存在'}</p>
          <button
            onClick={() => navigate('/documents')}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            返回列表
          </button>
        </div>
      </div>
    )
  }

  // 检查是否有查看权限
  const canView = permissions['document:' + id + ':can_view']
  const canEdit = permissions['document:' + id + ':can_edit']
  const canDelete = permissions['document:' + id + ':can_delete']
  const canShare = permissions['document:' + id + ':can_share']

  if (!canView) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-600 mb-4">您没有权限查看此文档</p>
          <button
            onClick={() => navigate('/documents')}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            返回列表
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* 头部操作栏 */}
      <div className="mb-6 flex items-center justify-between">
        <button
          onClick={() => navigate('/documents')}
          className="text-blue-600 hover:text-blue-700"
        >
          ← 返回列表
        </button>

        <div className="flex gap-2">
          {/* 编辑按钮 - 仅 editor 可见 */}
          {!isEditing && canEdit && (
            <button
              onClick={() => setIsEditing(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              编辑
            </button>
          )}

          {/* 分享按钮 - 仅 owner 可见 */}
          {canShare && (
            <button
              onClick={handleShare}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              分享
            </button>
          )}

          {/* 删除按钮 - 仅 owner 可见 */}
          {canDelete && (
            <button
              onClick={handleDelete}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              删除
            </button>
          )}
        </div>
      </div>

      {/* 文档内容 */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        {isEditing ? (
          // 编辑模式
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                标题
              </label>
              <input
                type="text"
                value={editedTitle}
                onChange={(e) => setEditedTitle(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                内容
              </label>
              <textarea
                value={editedContent}
                onChange={(e) => setEditedContent(e.target.value)}
                rows={15}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="flex gap-2">
              <button
                onClick={handleSave}
                disabled={isSaving}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
              >
                {isSaving ? '保存中...' : '保存'}
              </button>
              <button
                onClick={handleCancel}
                disabled={isSaving}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 disabled:opacity-50"
              >
                取消
              </button>
            </div>
          </div>
        ) : (
          // 查看模式
          <div>
            <h1 className="text-3xl font-bold mb-4">{document.title}</h1>
            <div className="text-gray-600 mb-4 text-sm">
              <p>创建者: {document.ownerId}</p>
              <p>创建时间: {new Date(document.createdAt).toLocaleString()}</p>
              <p>更新时间: {new Date(document.updatedAt).toLocaleString()}</p>
            </div>
            <div className="prose max-w-none">
              <pre className="whitespace-pre-wrap font-sans">{document.content}</pre>
            </div>
          </div>
        )}
      </div>

      {/* 权限信息（开发调试用） */}
      {process.env.NODE_ENV === 'development' && (
        <div className="mt-6 p-4 bg-gray-100 rounded">
          <h3 className="font-semibold mb-2">当前权限（开发模式）：</h3>
          <ul className="text-sm text-gray-600">
            <li>查看权限: {canView ? '✓' : '✗'}</li>
            <li>编辑权限: {canEdit ? '✓' : '✗'}</li>
            <li>删除权限: {canDelete ? '✓' : '✗'}</li>
            <li>分享权限: {canShare ? '✓' : '✗'}</li>
          </ul>
        </div>
      )}
    </div>
  )
}
