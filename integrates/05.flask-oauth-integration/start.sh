#!/bin/bash

# Flask + OAuth + OpenFGA 集成示例启动脚本

set -e

echo "=================================="
echo "Flask + OAuth + OpenFGA 启动脚本"
echo "=================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 Python 3${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 已安装${NC}"

# 检查 .env 文件
if [ ! -f .env ]; then
    echo -e "${YELLOW}警告: .env 文件不存在，从 .env.example 复制${NC}"
    cp .env.example .env
    echo -e "${YELLOW}请编辑 .env 文件并填写配置${NC}"
    exit 1
fi

echo -e "${GREEN}✓ .env 文件存在${NC}"

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}创建虚拟环境...${NC}"
    python3 -m venv .venv
fi

# 激活虚拟环境
source .venv/bin/python

# 安装依赖
echo -e "${YELLOW}安装依赖...${NC}"
.venv/bin/pip install -q -r requirements.txt

echo -e "${GREEN}✓ 依赖安装完成${NC}"

# 检查 OpenFGA
OPENFGA_URL=$(grep OPENFGA_API_URL .env | cut -d '=' -f2)
if [ -z "$OPENFGA_URL" ]; then
    OPENFGA_URL="http://localhost:8080"
fi

echo -e "${YELLOW}检查 OpenFGA 连接...${NC}"
if curl -s -f "${OPENFGA_URL}/healthz" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OpenFGA 运行正常${NC}"
else
    echo -e "${RED}✗ OpenFGA 未运行${NC}"
    echo -e "${YELLOW}请先启动 OpenFGA:${NC}"
    echo "  docker run -d --name openfga -p 8080:8080 -p 3000:3000 openfga/openfga run"
    exit 1
fi

# 检查 Store ID
STORE_ID=$(grep OPENFGA_STORE_ID .env | cut -d '=' -f2)
if [ -z "$STORE_ID" ] || [ "$STORE_ID" = "your-store-id-here" ]; then
    echo -e "${YELLOW}警告: 未配置 OPENFGA_STORE_ID${NC}"
    echo -e "${YELLOW}请先创建 Store 并更新 .env 文件${NC}"
    echo ""
    echo "创建 Store:"
    echo "  curl -X POST ${OPENFGA_URL}/stores -H 'Content-Type: application/json' -d '{\"name\": \"flask-oauth-demo\"}'"
    exit 1
fi

# 启动应用
echo ""
echo "=================================="
echo "启动 Flask 应用..."
echo "=================================="
echo ""

.venv/bin/python app.py
