/**
 * 文档列表组件
 * 显示用户可以访问的文档列表
 */

import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import * as api from '../services/api'
import type { Document } from '../types'
import { PermissionButton } from './PermissionGate'

export function DocumentList() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // 加载文档列表
  useEffect(() => {
    loadDocuments()
  }, [])

  const loadDocuments = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const docs = await api.getDocuments()
      setDocuments(docs)
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载文档列表失败')
    } finally {
      setIsLoading(false)
    }
  }

  // 创建新文档
  const handleCreateDocument = async () => {
    try {
      const title = prompt('请输入文档标题：')
      if (!title) return

      const newDoc = await api.createDocument({
        title,
        content: '',
      })
      setDocuments([newDoc, ...documents])
    } catch (err) {
      alert(err instanceof Error ? err.message : '创建文档失败')
    }
  }

  // 删除文档（乐观更新）
  const handleDeleteDocument = async (documentId: string) => {
    if (!confirm('确定要删除这个文档吗？')) return

    // 乐观更新：先从列表中移除
    const originalDocuments = [...documents]
    setDocuments(documents.filter((doc) => doc.id !== documentId))

    try {
      await api.deleteDocument(documentId)
    } catch (err) {
      // 删除失败，恢复列表
      setDocuments(originalDocuments)
      alert(err instanceof Error ? err.message : '删除文档失败')
    }
  }

  // 分享文档
  const handleShareDocument = async (documentId: string) => {
    const username = prompt('请输入要分享给的用户名：')
    if (!username) return

    const permission = prompt('请选择权限类型（viewer/editor）：', 'viewer')
    if (!permission || !['viewer', 'editor'].includes(permission)) {
      alert('无效的权限类型')
      return
    }

    try {
      await api.shareDocument(documentId, username, permission as 'viewer' | 'editor')
      alert('分享成功')
    } catch (err) {
      alert(err instanceof Error ? err.message : '分享失败')
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">加载文档列表...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
          <button
            onClick={loadDocuments}
            className="mt-2 text-red-600 hover:text-red-800 underline"
          >
            重试
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* 标题栏 */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-900">我的文档</h1>
        <button
          onClick={handleCreateDocument}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          创建文档
        </button>
      </div>

      {/* 文档列表 */}
      {documents.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">还没有文档</p>
          <button
            onClick={handleCreateDocument}
            className="mt-4 text-blue-600 hover:text-blue-800 underline"
          >
            创建第一个文档
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition"
            >
              <div className="flex items-start justify-between">
                {/* 文档信息 */}
                <div className="flex-1">
                  <Link
                    to={`/documents/${doc.id}`}
                    className="text-xl font-semibold text-gray-900 hover:text-blue-600"
                  >
                    {doc.title}
                  </Link>
                  <p className="text-gray-600 mt-1 line-clamp-2">
                    {doc.content || '暂无内容'}
                  </p>
                  <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                    <span>创建时间：{new Date(doc.createdAt).toLocaleDateString()}</span>
                    <span>更新时间：{new Date(doc.updatedAt).toLocaleDateString()}</span>
                  </div>
                </div>

                {/* 操作按钮 */}
                <div className="flex gap-2 ml-4">
                  {/* 编辑按钮 - 只有 editor 权限的用户可见 */}
                  <PermissionButton
                    objectType="document"
                    objectId={doc.id}
                    relation="can_edit"
                    onClick={() => {}}
                    className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                  >
                    <Link to={`/documents/${doc.id}/edit`}>编辑</Link>
                  </PermissionButton>

                  {/* 分享按钮 - 只有 owner 可见 */}
                  <PermissionButton
                    objectType="document"
                    objectId={doc.id}
                    relation="owner"
                    onClick={() => handleShareDocument(doc.id)}
                    className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    分享
                  </PermissionButton>

                  {/* 删除按钮 - 只有 owner 可见 */}
                  <PermissionButton
                    objectType="document"
                    objectId={doc.id}
                    relation="owner"
                    onClick={() => handleDeleteDocument(doc.id)}
                    className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
                  >
                    删除
                  </PermissionButton>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
