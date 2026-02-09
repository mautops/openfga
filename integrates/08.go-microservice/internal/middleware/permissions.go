package middleware

import (
	"context"
	"net/http"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"

	"openfga-go-microservice/internal/openfga"
)

// PermissionMiddleware 权限检查中间件
func PermissionMiddleware(fgaClient *openfga.Client, logger *zap.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		// 从上下文中获取用户信息
		userID, exists := c.Get("user_id")
		if !exists {
			logger.Error("用户 ID 不存在")
			c.JSON(http.StatusUnauthorized, gin.H{"error": "未认证"})
			c.Abort()
			return
		}

		// 从路由参数中获取资源 ID（如果存在）
		resourceID := c.Param("id")
		if resourceID == "" {
			// 如果没有资源 ID，可能是创建操作，直接放行
			c.Next()
			return
		}

		// 获取请求方法，映射到权限
		var relation string
		switch c.Request.Method {
		case "GET":
			relation = "can_view"
		case "PUT", "PATCH":
			relation = "can_edit"
		case "DELETE":
			relation = "can_delete"
		default:
			// POST 等其他方法直接放行
			c.Next()
			return
		}

		// 检查权限
		allowed, err := fgaClient.Check(
			context.Background(),
			userID.(string),
			relation,
			"document:"+resourceID,
		)

		if err != nil {
			logger.Error("权限检查失败",
				zap.String("user_id", userID.(string)),
				zap.String("relation", relation),
				zap.String("resource", "document:"+resourceID),
				zap.Error(err),
			)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "权限检查失败"})
			c.Abort()
			return
		}

		if !allowed {
			logger.Warn("权限被拒绝",
				zap.String("user_id", userID.(string)),
				zap.String("relation", relation),
				zap.String("resource", "document:"+resourceID),
			)
			c.JSON(http.StatusForbidden, gin.H{"error": "没有权限执行此操作"})
			c.Abort()
			return
		}

		// 权限检查通过，继续处理请求
		c.Next()
	}
}

// RequirePermission 需要特定权限的中间件工厂函数
func RequirePermission(fgaClient *openfga.Client, resourceType string, relation string, logger *zap.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		// 从上下文中获取用户信息
		userID, exists := c.Get("user_id")
		if !exists {
			logger.Error("用户 ID 不存在")
			c.JSON(http.StatusUnauthorized, gin.H{"error": "未认证"})
			c.Abort()
			return
		}

		// 从路由参数中获取资源 ID
		resourceID := c.Param("id")
		if resourceID == "" {
			logger.Error("资源 ID 不存在")
			c.JSON(http.StatusBadRequest, gin.H{"error": "资源 ID 不能为空"})
			c.Abort()
			return
		}

		// 检查权限
		allowed, err := fgaClient.Check(
			context.Background(),
			"user:"+userID.(string),
			relation,
			resourceType+":"+resourceID,
		)

		if err != nil {
			logger.Error("权限检查失败",
				zap.String("user_id", userID.(string)),
				zap.String("relation", relation),
				zap.String("resource", resourceType+":"+resourceID),
				zap.Error(err),
			)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "权限检查失败"})
			c.Abort()
			return
		}

		if !allowed {
			logger.Warn("权限被拒绝",
				zap.String("user_id", userID.(string)),
				zap.String("relation", relation),
				zap.String("resource", resourceType+":"+resourceID),
			)
			c.JSON(http.StatusForbidden, gin.H{"error": "没有权限执行此操作"})
			c.Abort()
			return
		}

		// 权限检查通过，继续处理请求
		c.Next()
	}
}
