package openfga

import (
	"context"
	"fmt"
	"os"

	"openfga-go-microservice/pkg/config"

	openfga "github.com/openfga/go-sdk"
	"github.com/openfga/go-sdk/client"
	"github.com/openfga/go-sdk/credentials"
)

// Client OpenFGA 客户端封装
type Client struct {
	fgaClient *client.OpenFgaClient
	storeID   string
	modelID   string
}

// NewClient 创建 OpenFGA 客户端实例
func NewClient(cfg *config.FGAConfig) (*Client, error) {
	// 构建客户端配置
	clientConfig := &client.ClientConfiguration{
		ApiUrl:                 cfg.APIURL,
		StoreId:                cfg.StoreID,
		AuthorizationModelId:   cfg.ModelID,
	}

	// 根据配置选择认证方式
	if cfg.APIToken != "" {
		// API Token 认证方式
		clientConfig.Credentials = &credentials.Credentials{
			Method: credentials.CredentialsMethodApiToken,
			Config: &credentials.Config{
				ApiToken: cfg.APIToken,
			},
		}
	} else if cfg.ClientID != "" && cfg.ClientSecret != "" {
		// Client Credentials (OAuth2) 认证方式
		clientConfig.Credentials = &credentials.Credentials{
			Method: credentials.CredentialsMethodClientCredentials,
			Config: &credentials.Config{
				ClientCredentialsClientId:       cfg.ClientID,
				ClientCredentialsClientSecret:   cfg.ClientSecret,
				ClientCredentialsScopes:         cfg.APIScopes,
				ClientCredentialsApiTokenIssuer: cfg.APITokenIssuer,
			},
		}
	}

	// 创建 OpenFGA 客户端
	fgaClient, err := client.NewSdkClient(clientConfig)
	if err != nil {
		return nil, fmt.Errorf("创建 OpenFGA 客户端失败: %w", err)
	}

	return &Client{
		fgaClient: fgaClient,
		storeID:   cfg.StoreID,
		modelID:   cfg.ModelID,
	}, nil
}

// Check 检查用户权限
// user: 用户标识，格式如 "user:alice"
// relation: 关系类型，如 "viewer", "editor", "owner"
// object: 对象标识，格式如 "document:doc1"
func (c *Client) Check(ctx context.Context, user, relation, object string) (bool, error) {
	body := client.ClientCheckRequest{
		User:     user,
		Relation: relation,
		Object:   object,
	}

	data, err := c.fgaClient.Check(ctx).Body(body).Execute()
	if err != nil {
		return false, fmt.Errorf("权限检查失败: %w", err)
	}

	return data.GetAllowed(), nil
}

// BatchCheck 批量检查权限
func (c *Client) BatchCheck(ctx context.Context, checks []CheckRequest) ([]bool, error) {
	results := make([]bool, len(checks))

	for i, check := range checks {
		allowed, err := c.Check(ctx, check.User, check.Relation, check.Object)
		if err != nil {
			return nil, fmt.Errorf("批量检查第 %d 项失败: %w", i, err)
		}
		results[i] = allowed
	}

	return results, nil
}

// CheckRequest 权限检查请求
type CheckRequest struct {
	User     string
	Relation string
	Object   string
}

// WriteTuple 写入关系元组
func (c *Client) WriteTuple(ctx context.Context, user, relation, object string) error {
	body := client.ClientWriteRequest{
		Writes: []openfga.TupleKey{
			{
				User:     user,
				Relation: relation,
				Object:   object,
			},
		},
	}

	_, err := c.fgaClient.Write(ctx).Body(body).Execute()
	if err != nil {
		return fmt.Errorf("写入关系元组失败: %w", err)
	}

	return nil
}

// TupleWrite 元组写入结构
type TupleWrite struct {
	User     string
	Relation string
	Object   string
}

// WriteTuples 批量写入关系元组
func (c *Client) WriteTuples(ctx context.Context, tuples []TupleWrite) error {
	writes := make([]openfga.TupleKey, len(tuples))
	for i, t := range tuples {
		writes[i] = openfga.TupleKey{
			User:     t.User,
			Relation: t.Relation,
			Object:   t.Object,
		}
	}

	body := client.ClientWriteRequest{
		Writes: writes,
	}

	_, err := c.fgaClient.Write(ctx).Body(body).Execute()
	if err != nil {
		return fmt.Errorf("批量写入关系元组失败: %w", err)
	}

	return nil
}

// DeleteTuple 删除关系元组
func (c *Client) DeleteTuple(ctx context.Context, user, relation, object string) error {
	body := client.ClientWriteRequest{
		Deletes: []openfga.TupleKeyWithoutCondition{
			{
				User:     user,
				Relation: relation,
				Object:   object,
			},
		},
	}

	_, err := c.fgaClient.Write(ctx).Body(body).Execute()
	if err != nil {
		return fmt.Errorf("删除关系元组失败: %w", err)
	}

	return nil
}

// DeleteTuples 批量删除关系元组
func (c *Client) DeleteTuples(ctx context.Context, tuples []TupleWrite) error {
	deletes := make([]openfga.TupleKeyWithoutCondition, len(tuples))
	for i, t := range tuples {
		deletes[i] = openfga.TupleKeyWithoutCondition{
			User:     t.User,
			Relation: t.Relation,
			Object:   t.Object,
		}
	}

	body := client.ClientWriteRequest{
		Deletes: deletes,
	}

	_, err := c.fgaClient.Write(ctx).Body(body).Execute()
	if err != nil {
		return fmt.Errorf("批量删除关系元组失败: %w", err)
	}

	return nil
}

// ListObjects 列出用户有指定关系的所有对象
func (c *Client) ListObjects(ctx context.Context, user, relation, objectType string) ([]string, error) {
	body := client.ClientListObjectsRequest{
		User:     user,
		Relation: relation,
		Type:     objectType,
	}

	data, err := c.fgaClient.ListObjects(ctx).Body(body).Execute()
	if err != nil {
		return nil, fmt.Errorf("列出对象失败: %w", err)
	}

	return data.GetObjects(), nil
}

// ReadTuples 读取关系元组
func (c *Client) ReadTuples(ctx context.Context, user, relation, object string) ([]openfga.Tuple, error) {
	body := client.ClientReadRequest{
		User:     openfga.PtrString(user),
		Relation: openfga.PtrString(relation),
		Object:   openfga.PtrString(object),
	}

	data, err := c.fgaClient.Read(ctx).Body(body).Execute()
	if err != nil {
		return nil, fmt.Errorf("读取关系元组失败: %w", err)
	}

	return data.GetTuples(), nil
}

// HealthCheck 健康检查
func (c *Client) HealthCheck(ctx context.Context) error {
	// 通过读取 store 信息来验证连接
	options := client.ClientGetStoreOptions{
		StoreId: openfga.PtrString(c.storeID),
	}

	_, err := c.fgaClient.GetStore(ctx).Options(options).Execute()
	if err != nil {
		return fmt.Errorf("OpenFGA 健康检查失败: %w", err)
	}

	return nil
}

// Close 关闭客户端连接
func (c *Client) Close() error {
	// OpenFGA Go SDK 目前不需要显式关闭
	return nil
}

// InitializeModel 初始化授权模型（开发环境使用）
func InitializeModel(cfg *config.FGAConfig, modelFile string) error {
	// 读取模型文件
	modelContent, err := os.ReadFile(modelFile)
	if err != nil {
		return fmt.Errorf("读取模型文件失败: %w", err)
	}

	// 创建临时客户端
	clientConfig := &client.ClientConfiguration{
		ApiUrl:  cfg.APIURL,
		StoreId: cfg.StoreID,
	}

	if cfg.APIToken != "" {
		clientConfig.Credentials = &credentials.Credentials{
			Method: credentials.CredentialsMethodApiToken,
			Config: &credentials.Config{
				ApiToken: cfg.APIToken,
			},
		}
	}

	fgaClient, err := client.NewSdkClient(clientConfig)
	if err != nil {
		return fmt.Errorf("创建临时客户端失败: %w", err)
	}

	// 解析并写入模型（需要使用 language transformer）
	// 这里简化处理，实际使用时需要引入 github.com/openfga/language/pkg/go/transformer
	fmt.Printf("模型内容:\n%s\n", string(modelContent))
	fmt.Println("注意: 生产环境建议使用 OpenFGA CLI 或 API 管理授权模型")

	_ = fgaClient // 避免未使用变量警告

	return nil
}
