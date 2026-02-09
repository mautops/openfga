#!/bin/bash

# FastAPI + OpenFGA 快速启动脚本

set -e

echo "=========================================="
echo "FastAPI + OpenFGA 集成示例 - 快速启动"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker 未安装，请先安装 Docker${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker 已安装${NC}"

# 检查 OpenFGA 是否运行
if docker ps | grep -q openfga; then
    echo -e "${GREEN}✓ OpenFGA 已运行${NC}"
else
    echo -e "${YELLOW}启动 OpenFGA...${NC}"
    docker run -d \
        --name openfga \
        -p 8080:8080 \
        -p 3000:3000 \
        openfga/openfga run

    echo -e "${GREEN}✓ OpenFGA 已启动${NC}"
    echo "  等待服务就绪..."
    sleep 5
fi

# 检查 Python 环境
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}创建 Python 虚拟环境...${NC}"

    if command -v uv &> /dev/null; then
        uv venv
        echo -e "${GREEN}✓ 虚拟环境已创建（使用 uv）${NC}"
    else
        python3 -m venv .venv
        echo -e "${GREEN}✓ 虚拟环境已创建${NC}"
    fi
fi

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
if [ ! -f ".venv/installed" ]; then
    echo -e "${YELLOW}安装 Python 依赖...${NC}"

    if command -v uv &> /dev/null; then
        uv pip install -r requirements.txt
    else
        pip install -r requirements.txt
    fi

    touch .venv/installed
    echo -e "${GREEN}✓ 依赖已安装${NC}"
else
    echo -e "${GREEN}✓ 依赖已安装${NC}"
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}创建 .env 文件...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env 文件已创建${NC}"
    echo -e "${YELLOW}⚠ 请编辑 .env 文件，填写 OPENFGA_STORE_ID${NC}"
fi

# 检查 Store ID
STORE_ID=$(grep "^OPENFGA_STORE_ID=" .env | cut -d '=' -f2)

if [ -z "$STORE_ID" ]; then
    echo ""
    echo -e "${YELLOW}=========================================="
    echo "需要创建 OpenFGA Store"
    echo "==========================================${NC}"
    echo ""
    echo "执行以下命令创建 Store:"
    echo ""
    echo -e "${GREEN}curl -X POST http://localhost:8080/stores \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -d '{\"name\": \"fastapi-demo\"}'${NC}"
    echo ""
    echo "然后将返回的 store_id 填入 .env 文件的 OPENFGA_STORE_ID"
    echo ""
    echo "接下来创建授权模型:"
    echo ""
    echo -e "${GREEN}curl -X POST http://localhost:8080/stores/{store_id}/authorization-models \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -d @authorization_model.json${NC}"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓ Store ID 已配置: $STORE_ID${NC}"

# 启动应用
echo ""
echo -e "${GREEN}=========================================="
echo "启动 FastAPI 应用"
echo "==========================================${NC}"
echo ""
echo "应用将在 http://localhost:8000 启动"
echo "API 文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止应用"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
