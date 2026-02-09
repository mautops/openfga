package handlers

import (
	"context"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"go.uber.org/zap"

	"openfga-go-microservice/internal/models"
	"openfga-go-microservice/internal/openfga"
)

// DocumentHandler 文档处理器
type DocumentHandler struct {
	fgaClient *openfga.Client
	logger    *zap.Logger
	// 这里可以添加数据库客户端，用于持久化存储
	// 为了简化示例，我们使用内存存储
	documents map[string]*models.Document
}

// NewDocumentHandler 创建文档处理器实例
func NewDocumentHandler(fgaClient *openfga.Client, logger *zap.Logger) *DocumentHandler {
	return &DocumentHandler{
		fgaClient: fgaClient,
		logger:    logger,
		documents: make(map[string]*models.Document),
	}
}

// CreateDocument 创建文档
// @Summary 创建新文档
// @Description 创建新文档并设置所有者权限
// @Accept json
// @Produce json
// @Param document body models.CreateDocumentRequest true "文档信息"
// @Success 201 {object} models.Document
// @Failure 400 {object} map[string]string
// @Failure 401 {object} map[string]string
// @Failure 500 {object} map[string]string
// @Router /api/documents [post]
func (h *DocumentHandler) CreateDocument(c *gin.Context) {
	var req models.CreateDocumentRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		h.logger.Error("请求参数绑定失败", zap.Error(err))
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的请求参数: " + err.Error()})
		return
	}

	// 从上下文中获取用户信息
	userID, _ := c.Get("user_id")
	organizationID, _ := c.Get("organization_id")

	// 创建文档
	doc := &models.Document{
		ID:             uuid.New().String(),
		Title:          req.Title,
		Content:        req.Content,
		OrganizationID: organizationID.(string),
		OwnerID:        userID.(string),
		CreatedAt:      time.Now(),
		UpdatedAt:      time.Now(),
	}

	// 保存文档（实际项目中应该保存到数据库）
	h.documents[doc.ID] = doc

	// 在 OpenFGA 中创建关系元组
	ctx := context.Background()

	// 设置文档所有者
	if err := h.fgaClient.WriteTuples(ctx, []openfga.TupleWrite{
		{
			User:     "user:" + userID.(string),
			Relation: "owner",
			Object:   "document:" + doc.ID,
		},
		{
			User:     "organization:" + organizationID.(string),
			Relation: "organization",
			Object:   "document:" + doc.ID,
		},
	}); err != nil {
		h.logger.Error("创建权限元组失败", zap.Error(err))
		// 清理已创建的文档
		delete(h.documents, doc.ID)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "创建文档权限失败"})
		return
	}

	h.logger.Info("文档创建成功",
		zap.String("document_id", doc.ID),
		zap.String("owner_id", userID.(string)),
	)

	c.JSON(http.StatusCreated, doc)
}

// GetDocument 获取文档
// @Summary 获取文档详情
// @Description 获取指定 ID 的文档详情（需要 viewer 权限）
// @Produce json
// @Param id path string true "文档 ID"
// @Success 200 {object} models.Document
// @Failure 404 {object} map[string]string
// @Failure 403 {object} map[string]string
// @Router /api/documents/{id} [get]
func (h *DocumentHandler) GetDocument(c *gin.Context) {
	docID := c.Param("id")

	// 获取文档（实际项目中应该从数据库查询）
	doc, exists := h.documents[docID]
	if !exists {
		c.JSON(http.StatusNotFound, gin.H{"error": "文档���存在"})
		return
	}

	h.logger.Info("文档查询成功", zap.String("document_id", docID))
	c.JSON(http.StatusOK, doc)
}

// UpdateDocument 更新文档
// @Summary 更新文档
// @Description 更新指定 ID 的文档（需要 editor 权限）
// @Accept json
// @Produce json
// @Param id path string true "文档 ID"
// @Param document body models.UpdateDocumentRequest true "更新的文档信息"
// @Success 200 {object} models.Document
// @Failure 400 {object} map[string]string
// @Failure 404 {object} map[string]string
// @Failure 403 {object} map[string]string
// @Router /api/documents/{id} [put]
func (h *DocumentHandler) UpdateDocument(c *gin.Context) {
	docID := c.Param("id")

	var req models.UpdateDocumentRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		h.logger.Error("请求参数绑定失败", zap.Error(err))
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的请求参数: " + err.Error()})
		return
	}

	// 获取文档
	doc, exists := h.documents[docID]
	if !exists {
		c.JSON(http.StatusNotFound, gin.H{"error": "文档不存在"})
		return
	}

	// 更新文档
	if req.Title != "" {
		doc.Title = req.Title
	}
	if req.Content != "" {
		doc.Content = req.Content
	}
	doc.UpdatedAt = time.Now()

	h.logger.Info("文档更新成功", zap.String("document_id", docID))
	c.JSON(http.StatusOK, doc)
}

// DeleteDocument 删除文档
// @Summary 删除文档
// @Description 删除指定 ID 的文档（需要 owner 权限）
// @Param id path string true "文档 ID"
// @Success 204
// @Failure 404 {object} map[string]string
// @Failure 403 {object} map[string]string
// @Router /api/documents/{id} [delete]
func (h *DocumentHandler) DeleteDocument(c *gin.Context) {
	docID := c.Param("id")

	// 检查文档是否存在
	_, exists := h.documents[docID]
	if !exists {
		c.JSON(http.StatusNotFound, gin.H{"error": "文档不存在"})
		return
	}

	// 删除文档
	delete(h.documents, docID)

	// 删除 OpenFGA 中的关系元组
	ctx := context.Background()
	userID, _ := c.Get("user_id")
	organizationID, _ := c.Get("organization_id")

	if err := h.fgaClient.DeleteTuples(ctx, []openfga.TupleWrite{
		{
			User:     "user:" + userID.(string),
			Relation: "owner",
			Object:   "document:" + docID,
		},
		{
			User:     "organization:" + organizationID.(string),
			Relation: "organization",
			Object:   "document:" + docID,
		},
	}); err != nil {
		h.logger.Error("删除权限元组失败", zap.Error(err))
		// 即使删除元组失败，文档已经删除，记录错误但不返回失败
	}

	h.logger.Info("文档删除成功", zap.String("document_id", docID))
	c.Status(http.StatusNoContent)
}

// ListDocuments 列出文档
// @Summary 列出用户可访问的文档
// @Description 列出当前用户有权限访问的所有文档
// @Produce json
// @Success 200 {array} models.Document
// @Router /api/documents [get]
func (h *DocumentHandler) ListDocuments(c *gin.Context) {
	userID, _ := c.Get("user_id")

	// 获取用户可访问的文档列表
	var accessibleDocs []*models.Document
	ctx := context.Background()

	for _, doc := range h.documents {
		// 检查用户是否有查看权限
		allowed, err := h.fgaClient.Check(
			ctx,
			"user:"+userID.(string),
			"can_view",
			"document:"+doc.ID,
		)

		if err != nil {
			h.logger.Error("权限检查失败",
				zap.String("document_id", doc.ID),
				zap.Error(err),
			)
			continue
		}

		if allowed {
			accessibleDocs = append(accessibleDocs, doc)
		}
	}

	h.logger.Info("文档列表查询成功",
		zap.String("user_id", userID.(string)),
		zap.Int("count", len(accessibleDocs)),
	)

	c.JSON(http.StatusOK, accessibleDocs)
}

// ShareDocument 分享文档
// @Summary 分享文档给其他用户
// @Description 将文档的指定权限分享给其他用户（需要 owner 权限）
// @Accept json
// @Produce json
// @Param id path string true "文档 ID"
// @Param share body models.ShareDocumentRequest true "分享信息"
// @Success 200 {object} map[string]string
// @Failure 400 {object} map[string]string
// @Failure 404 {object} map[string]string
// @Failure 403 {object} map[string]string
// @Router /api/documents/{id}/share [post]
func (h *DocumentHandler) ShareDocument(c *gin.Context) {
	docID := c.Param("id")

	var req models.ShareDocumentRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		h.logger.Error("请求参数绑定失败", zap.Error(err))
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的请求参数: " + err.Error()})
		return
	}

	// 检查文档是否存在
	_, exists := h.documents[docID]
	if !exists {
		c.JSON(http.StatusNotFound, gin.H{"error": "文档不存在"})
		return
	}

	// 验证权限类型
	if req.Relation != "viewer" && req.Relation != "editor" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的权限类型，只能是 viewer 或 editor"})
		return
	}

	// 在 OpenFGA 中创建分享关系
	ctx := context.Background()
	if err := h.fgaClient.WriteTuples(ctx, []openfga.TupleWrite{
		{
			User:     "user:" + req.UserID,
			Relation: req.Relation,
			Object:   "document:" + docID,
		},
	}); err != nil {
		h.logger.Error("创建分享权限失败", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "分享失败"})
		return
	}

	h.logger.Info("文档分享成功",
		zap.String("document_id", docID),
		zap.String("target_user", req.UserID),
		zap.String("relation", req.Relation),
	)

	c.JSON(http.StatusOK, gin.H{"message": "分享成功"})
}
