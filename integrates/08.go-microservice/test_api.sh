#!/bin/bash

# OpenFGA Go 微服务测试脚本
# 用于测试文档管理 API 的各种权限场景

set -e

# 配置
API_URL="http://localhost:8080"
JWT_SECRET="your-super-secret-jwt-key-change-this-in-production"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印函数
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

print_section() {
    echo ""
    echo "=========================================="
    echo "$1"
    echo "=========================================="
}

# 生成 JWT Token
generate_token() {
    local user_id=$1
    local email=$2
    local org_id=$3

    cd tools
    TOKEN=$(go run generate_token.go -user "$user_id" -email "$email" -org "$org_id" -secret "$JWT_SECRET" 2>/dev/null | grep -A 1 "Token:" | tail -n 1)
    cd ..
    echo "$TOKEN"
}

# 测试健康检查
test_health_check() {
    print_section "测试 1: 健康检查"

    response=$(curl -s -w "\n%{http_code}" "$API_URL/health")
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)

    if [ "$http_code" = "200" ]; then
        print_success "健康检查通过"
        echo "响应: $body"
    else
        print_error "健康检查失败 (HTTP $http_code)"
        exit 1
    fi
}

# 测试创建文档
test_create_document() {
    print_section "测试 2: 创建文档"

    print_info "生成 Alice 的 JWT Token..."
    ALICE_TOKEN=$(generate_token "user:alice" "alice@example.com" "org:acme")

    print_info "创建文档..."
    response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/api/documents" \
        -H "Authorization: Bearer $ALICE_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "title": "测试文档",
            "content": "这是一个测试文档的内容",
            "organization_id": "org:acme"
        }')

    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)

    if [ "$http_code" = "201" ]; then
        print_success "文档创建成功"
        DOC_ID=$(echo "$body" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
        echo "文档 ID: $DOC_ID"
        echo "响应: $body"
    else
        print_error "文档创建失败 (HTTP $http_code)"
        echo "响应: $body"
        exit 1
    fi
}

# 测试查看文档（所有者）
test_view_document_owner() {
    print_section "测试 3: 查看文档（所有者）"

    print_info "Alice 查看自己创建的文档..."
    response=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/api/documents/$DOC_ID" \
        -H "Authorization: Bearer $ALICE_TOKEN")

    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)

    if [ "$http_code" = "200" ]; then
        print_success "文档查看成功（所有者）"
        echo "响应: $body"
    else
        print_error "文档查看失败 (HTTP $http_code)"
        echo "响应: $body"
        exit 1
    fi
}

# 测试查看文档（无权限）
test_view_document_no_permission() {
    print_section "测试 4: 查看文档（无权限）"

    print_info "生成 Bob 的 JWT Token..."
    BOB_TOKEN=$(generate_token "user:bob" "bob@example.com" "org:other")

    print_info "Bob 尝试查看 Alice 的文档（应该失败）..."
    response=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/api/documents/$DOC_ID" \
        -H "Authorization: Bearer $BOB_TOKEN")

    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)

    if [ "$http_code" = "403" ]; then
        print_success "权限检查正常（拒绝访问）"
        echo "响应: $body"
    else
        print_error "权限检查异常 (HTTP $http_code，应该是 403)"
        echo "响应: $body"
    fi
}

# 测试编辑文档（所有者）
test_update_document_owner() {
    print_section "测试 5: 编辑文档（所有者）"

    print_info "Alice 编辑自己的文档..."
    response=$(curl -s -w "\n%{http_code}" -X PUT "$API_URL/api/documents/$DOC_ID" \
        -H "Authorization: Bearer $ALICE_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "title": "更新后的测试文档",
            "content": "这是更新后的内容"
        }')

    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)

    if [ "$http_code" = "200" ]; then
        print_success "文档编辑成功（所有者）"
        echo "响应: $body"
    else
        print_error "文档编辑失败 (HTTP $http_code)"
        echo "响应: $body"
        exit 1
    fi
}

# 测试编辑文档（无权限）
test_update_document_no_permission() {
    print_section "测试 6: 编辑文档（无权限）"

    print_info "Bob 尝试编辑 Alice 的文档（应该失败）..."
    response=$(curl -s -w "\n%{http_code}" -X PUT "$API_URL/api/documents/$DOC_ID" \
        -H "Authorization: Bearer $BOB_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "title": "Bob 的修改",
            "content": "Bob 尝试修改内容"
        }')

    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)

    if [ "$http_code" = "403" ]; then
        print_success "权限检查正常（拒绝编辑）"
        echo "响应: $body"
    else
        print_error "权限检查异常 (HTTP $http_code，应该是 403)"
        echo "响应: $body"
    fi
}

# 测试列出文档
test_list_documents() {
    print_section "测试 7: 列出文档"

    print_info "Alice 列出自己可访问的文档..."
    response=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/api/documents" \
        -H "Authorization: Bearer $ALICE_TOKEN")

    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)

    if [ "$http_code" = "200" ]; then
        print_success "文档列表获取成功"
        echo "响应: $body"
    else
        print_error "文档列表获取失败 (HTTP $http_code)"
        echo "响应: $body"
        exit 1
    fi
}

# 测试删除文档（所有者）
test_delete_document_owner() {
    print_section "测试 8: 删除文档（所有者）"

    print_info "Alice 删除自己的文档..."
    response=$(curl -s -w "\n%{http_code}" -X DELETE "$API_URL/api/documents/$DOC_ID" \
        -H "Authorization: Bearer $ALICE_TOKEN")

    http_code=$(echo "$response" | tail -n 1)

    if [ "$http_code" = "204" ]; then
        print_success "文档删除成功（所有者）"
    else
        print_error "文档删除失败 (HTTP $http_code)"
        exit 1
    fi
}

# 测试无效 Token
test_invalid_token() {
    print_section "测试 9: 无效 Token"

    print_info "使用无效 Token 访问 API..."
    response=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/api/documents" \
        -H "Authorization: Bearer invalid-token")

    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)

    if [ "$http_code" = "401" ]; then
        print_success "Token 验证正常（拒绝访问）"
        echo "响应: $body"
    else
        print_error "Token 验证异常 (HTTP $http_code，应该是 401)"
        echo "响应: $body"
    fi
}

# 主测试流程
main() {
    echo "=========================================="
    echo "OpenFGA Go 微服务 API 测试"
    echo "=========================================="
    echo ""

    # 检查服务是否运行
    print_info "检查服务状态..."
    if ! curl -s "$API_URL/health" > /dev/null; then
        print_error "服务未运行，请先启动服务: make run"
        exit 1
    fi

    # 运行测试
    test_health_check
    test_create_document
    test_view_document_owner
    test_view_document_no_permission
    test_update_document_owner
    test_update_document_no_permission
    test_list_documents
    test_delete_document_owner
    test_invalid_token

    # 测试总结
    print_section "测试完成"
    print_success "所有测试通过！"
}

# 运行主函数
main
