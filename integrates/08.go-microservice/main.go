package main

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"

	"openfga-go-microservice/internal/handlers"
	"openfga-go-microservice/internal/middleware"
	"openfga-go-microservice/internal/openfga"
	"openfga-go-microservice/pkg/config"
)

func main() {
	// 初始化日志
	logger, err := zap.NewProduction()
	if err != nil {
		panic(fmt.Sprintf("初始化日志失败: %v", err))
	}
	defer logger.Sync()

	// 加载配置
	cfg, err := config.LoadConfig()
	if err != nil {
		logger.Fatal("加载配置失败", zap.Error(err))
	}

	// 设置 Gin 模式
	gin.SetMode(cfg.Server.GinMode)

	// 初始化 OpenFGA 客户端
	fgaClient, err := openfga.NewClient(&cfg.FGA)
	if err != nil {
		logger.Fatal("初始化 OpenFGA 客户端失败", zap.Error(err))
	}

	// 创建 Gin 引擎
	router := gin.New()
	router.Use(gin.Recovery())
	router.Use(ginLogger(logger))

	// 健康检查端点
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status": "healthy",
			"time":   time.Now().Format(time.RFC3339),
		})
	})

	// API 路由组
	api := router.Group("/api")
	{
		// 文档处理器
		docHandler := handlers.NewDocumentHandler(fgaClient, logger)

		// 文档路由 - 需要认证
		docs := api.Group("/documents")
		docs.Use(middleware.AuthMiddleware(&cfg.JWT, logger))
		{
			// 创建文档 - 只需认证
			docs.POST("", docHandler.CreateDocument)

			// 查看文档 - 需要 viewer 权限
			docs.GET("/:id",
				middleware.RequirePermission(fgaClient, "document", "can_view", logger),
				docHandler.GetDocument,
			)

			// 编辑文档 - 需要 editor 权限
			docs.PUT("/:id",
				middleware.RequirePermission(fgaClient, "document", "can_edit", logger),
				docHandler.UpdateDocument,
			)

			// 删除文档 - 需要 owner 权限
			docs.DELETE("/:id",
				middleware.RequirePermission(fgaClient, "document", "can_delete", logger),
				docHandler.DeleteDocument,
			)

			// 列出文档 - 只需认证
			docs.GET("", docHandler.ListDocuments)
		}
	}

	// 创建 HTTP 服务器
	srv := &http.Server{
		Addr:         ":" + cfg.Server.Port,
		Handler:      router,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	// 在 goroutine 中启动服务器
	go func() {
		logger.Info("启动服务器", zap.String("port", cfg.Server.Port))
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Fatal("服务器启动失败", zap.Error(err))
		}
	}()

	// 等待中断信号以优雅地关闭服务器
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	logger.Info("正在关闭服务器...")

	// 设置 5 秒的超时时间
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		logger.Fatal("服务器强制关闭", zap.Error(err))
	}

	logger.Info("服务器已退出")
}

// ginLogger Gin 日志中间件
func ginLogger(logger *zap.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		path := c.Request.URL.Path
		query := c.Request.URL.RawQuery

		c.Next()

		latency := time.Since(start)
		statusCode := c.Writer.Status()
		clientIP := c.ClientIP()
		method := c.Request.Method

		logger.Info("HTTP 请求",
			zap.String("method", method),
			zap.String("path", path),
			zap.String("query", query),
			zap.Int("status", statusCode),
			zap.Duration("latency", latency),
			zap.String("ip", clientIP),
		)
	}
}
