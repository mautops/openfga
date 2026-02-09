package main

import (
	"flag"
	"fmt"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

// Claims JWT Claims 结构
type Claims struct {
	UserID         string `json:"user_id"`
	Email          string `json:"email"`
	OrganizationID string `json:"organization_id"`
	jwt.RegisteredClaims
}

func main() {
	// 命令行参数
	userID := flag.String("user", "user:alice", "用户 ID")
	email := flag.String("email", "alice@example.com", "用户邮箱")
	orgID := flag.String("org", "org:acme", "组织 ID")
	secret := flag.String("secret", "your-super-secret-jwt-key-change-this-in-production", "JWT 密钥")
	hours := flag.Int("hours", 24, "Token 有效期（小时）")

	flag.Parse()

	// 创建 Claims
	claims := &Claims{
		UserID:         *userID,
		Email:          *email,
		OrganizationID: *orgID,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(time.Duration(*hours) * time.Hour)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			Issuer:    "openfga-microservice",
		},
	}

	// 创建 Token
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)

	// 签名
	tokenString, err := token.SignedString([]byte(*secret))
	if err != nil {
		fmt.Printf("生成 Token 失败: %v\n", err)
		return
	}

	// 输出结果
	fmt.Println("=== JWT Token 生成成功 ===")
	fmt.Printf("用户 ID: %s\n", *userID)
	fmt.Printf("邮箱: %s\n", *email)
	fmt.Printf("组织 ID: %s\n", *orgID)
	fmt.Printf("有效期: %d 小时\n", *hours)
	fmt.Println("\nToken:")
	fmt.Println(tokenString)
	fmt.Println("\n使用方法:")
	fmt.Printf("export TOKEN=\"%s\"\n", tokenString)
	fmt.Println("curl -H \"Authorization: Bearer $TOKEN\" http://localhost:8080/api/documents")
}
