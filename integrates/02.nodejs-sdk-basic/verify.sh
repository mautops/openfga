#!/bin/bash

# 项目完整性验证脚本

echo "=========================================="
echo "OpenFGA Node.js SDK 项目验证"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查计数
PASSED=0
FAILED=0

# 检查函数
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 存在"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $1 缺失"
        ((FAILED++))
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 目录存在"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $1 目录缺失"
        ((FAILED++))
    fi
}

echo "1. 检查目录结构"
echo "----------------------------------------"
check_dir "src"
echo ""

echo "2. 检查核心代码文件"
echo "----------------------------------------"
check_file "src/client.ts"
check_file "src/examples.ts"
check_file "src/advanced-examples.ts"
echo ""

echo "3. 检查配置文件"
echo "----------------------------------------"
check_file "package.json"
check_file "tsconfig.json"
check_file ".env.example"
check_file "authorization_model.fga"
check_file ".gitignore"
echo ""

echo "4. 检查文档文件"
echo "----------------------------------------"
check_file "README.md"
check_file "PROJECT_OVERVIEW.md"
check_file "QUICK_REFERENCE.md"
check_file "PROJECT_SUMMARY.md"
echo ""

echo "5. 检查辅助文件"
echo "----------------------------------------"
check_file "setup.sh"
echo ""

echo "6. 检查文件内容"
echo "----------------------------------------"

# 检查 package.json 是否包含必要的依赖
if grep -q "@openfga/sdk" package.json; then
    echo -e "${GREEN}✓${NC} package.json 包含 @openfga/sdk"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} package.json 缺少 @openfga/sdk"
    ((FAILED++))
fi

if grep -q "dotenv" package.json; then
    echo -e "${GREEN}✓${NC} package.json 包含 dotenv"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} package.json 缺少 dotenv"
    ((FAILED++))
fi

# 检查 TypeScript 配置
if grep -q "strict" tsconfig.json; then
    echo -e "${GREEN}✓${NC} tsconfig.json 启用严格模式"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} tsconfig.json 未启用严格模式"
fi

# 检查授权模型
if grep -q "model" authorization_model.fga; then
    echo -e "${GREEN}✓${NC} authorization_model.fga 包含模型定义"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} authorization_model.fga 格式错误"
    ((FAILED++))
fi

echo ""

echo "7. 统计信息"
echo "----------------------------------------"
echo "TypeScript 文件数: $(find src -name "*.ts" | wc -l)"
echo "TypeScript 代码行数: $(find src -name "*.ts" -exec wc -l {} + | tail -1 | awk '{print $1}')"
echo "文档文件数: $(ls *.md 2>/dev/null | wc -l)"
echo "配置文件数: $(ls *.json 2>/dev/null | wc -l)"
echo ""

echo "=========================================="
echo "验证结果"
echo "=========================================="
echo -e "${GREEN}通过: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}失败: $FAILED${NC}"
else
    echo -e "${GREEN}失败: $FAILED${NC}"
fi
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ 项目完整性验证通过！${NC}"
    echo ""
    echo "下一步："
    echo "1. 运行 ./setup.sh 安装依赖"
    echo "2. 配置 .env 文件"
    echo "3. 运行 pnpm run dev 测试示例"
    exit 0
else
    echo -e "${RED}✗ 项目完整性验证失败，请检查缺失的文件${NC}"
    exit 1
fi
