package config

import (
	"fmt"
	"os"

	"github.com/joho/godotenv"
	"github.com/spf13/viper"
)

// Config 应用配置结构
type Config struct {
	Server ServerConfig
	FGA    FGAConfig
	JWT    JWTConfig
}

// ServerConfig 服务器配置
type ServerConfig struct {
	Port    string
	GinMode string
}

// FGAConfig OpenFGA 配置
type FGAConfig struct {
	APIURL              string
	StoreID             string
	ModelID             string
	APIToken            string
	ClientID            string
	ClientSecret        string
	APIScopes           string
	APITokenIssuer      string
	APIAudience         string
	MaxRetries          int
	RetryMinWaitSeconds int
}

// JWTConfig JWT 配置
type JWTConfig struct {
	Secret string
	Issuer string
}

// LoadConfig 加载配置（导出函数）
func LoadConfig() (*Config, error) {
	return Load()
}

// Load 加载配置
func Load() (*Config, error) {
	// 尝试加载 .env 文件（开发环境）
	_ = godotenv.Load()

	// 使用 viper 加载配置
	viper.AutomaticEnv()

	// 设置默认值
	viper.SetDefault("SERVER_PORT", "8080")
	viper.SetDefault("GIN_MODE", "debug")
	viper.SetDefault("FGA_MAX_RETRIES", 3)
	viper.SetDefault("FGA_RETRY_MIN_WAIT_SECONDS", 1)
	viper.SetDefault("JWT_ISSUER", "openfga-microservice")

	config := &Config{
		Server: ServerConfig{
			Port:    viper.GetString("SERVER_PORT"),
			GinMode: viper.GetString("GIN_MODE"),
		},
		FGA: FGAConfig{
			APIURL:              viper.GetString("FGA_API_URL"),
			StoreID:             viper.GetString("FGA_STORE_ID"),
			ModelID:             viper.GetString("FGA_MODEL_ID"),
			APIToken:            viper.GetString("FGA_API_TOKEN"),
			ClientID:            viper.GetString("FGA_CLIENT_ID"),
			ClientSecret:        viper.GetString("FGA_CLIENT_SECRET"),
			APIScopes:           viper.GetString("FGA_API_SCOPES"),
			APITokenIssuer:      viper.GetString("FGA_API_TOKEN_ISSUER"),
			APIAudience:         viper.GetString("FGA_API_AUDIENCE"),
			MaxRetries:          viper.GetInt("FGA_MAX_RETRIES"),
			RetryMinWaitSeconds: viper.GetInt("FGA_RETRY_MIN_WAIT_SECONDS"),
		},
		JWT: JWTConfig{
			Secret: getRequiredEnv("JWT_SECRET"),
			Issuer: viper.GetString("JWT_ISSUER"),
		},
	}

	// 验证必需配置
	if err := config.validate(); err != nil {
		return nil, err
	}

	return config, nil
}

// validate 验证配置
func (c *Config) validate() error {
	if c.FGA.APIURL == "" {
		return fmt.Errorf("FGA_API_URL is required")
	}
	if c.FGA.StoreID == "" {
		return fmt.Errorf("FGA_STORE_ID is required")
	}
	if c.JWT.Secret == "" {
		return fmt.Errorf("JWT_SECRET is required")
	}
	return nil
}

// getRequiredEnv 获取必需的环境变量
func getRequiredEnv(key string) string {
	value := os.Getenv(key)
	if value == "" {
		panic(fmt.Sprintf("Required environment variable %s is not set", key))
	}
	return value
}
