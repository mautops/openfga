package models

import "time"

// Document 文档模型
type Document struct {
	ID             string    `json:"id"`
	Title          string    `json:"title" binding:"required"`
	Content        string    `json:"content" binding:"required"`
	OrganizationID string    `json:"organization_id" binding:"required"`
	OwnerID        string    `json:"owner_id"`
	CreatedAt      time.Time `json:"created_at"`
	UpdatedAt      time.Time `json:"updated_at"`
}

// CreateDocumentRequest 创建文档请求
type CreateDocumentRequest struct {
	Title          string `json:"title" binding:"required"`
	Content        string `json:"content" binding:"required"`
	OrganizationID string `json:"organization_id" binding:"required"`
}

// UpdateDocumentRequest 更新文档请求
type UpdateDocumentRequest struct {
	Title   string `json:"title"`
	Content string `json:"content"`
}

// DocumentResponse 文档响应
type DocumentResponse struct {
	ID             string    `json:"id"`
	Title          string    `json:"title"`
	Content        string    `json:"content"`
	OrganizationID string    `json:"organization_id"`
	OwnerID        string    `json:"owner_id"`
	CreatedAt      time.Time `json:"created_at"`
	UpdatedAt      time.Time `json:"updated_at"`
	Permissions    *DocumentPermissions `json:"permissions,omitempty"`
}

// DocumentPermissions 文档权限信息
type DocumentPermissions struct {
	CanView   bool `json:"can_view"`
	CanEdit   bool `json:"can_edit"`
	CanDelete bool `json:"can_delete"`
}

// ShareDocumentRequest 分享文档请求
type ShareDocumentRequest struct {
	UserID   string `json:"user_id" binding:"required"`
	Relation string `json:"relation" binding:"required"`
}
