#!/bin/bash

# OpenFGA Node.js SDK 快速启动脚本

set -e

echo "=========================================="
echo "OpenFGA Node.js SDK 快速启动"
echo "=========================================="
echo ""

# 检查 pnpm 是否安装
if ! command -v pnpm &> /dev/null; then
    echo "错误: pnpm 未安装"
    echo "请运行: npm install -g pnpm"
    exit 1
fi

# 检查 Docker 是否运行
if ! docker info &> /dev/null; then
    echo "警告: Docker 未运行，请先启动 Docker"
    echo ""
fi

# 安装依赖
echo "1. 安装依赖..."
pnpm install

# 检查 .env 文件
if [ ! -f .env ]; then
    echo ""
    echo "2. 创建 .env 文件..."
    cp .env.example .env
    echo "已创建 .env 文件，请根据需要修改配置"
else
    echo ""
    echo "2. .env 文件已存在"
fi

# 编译 TypeScript
echo ""
echo "3. 编译 TypeScript..."
pnpm run build

echo ""
echo "=========================================="
echo "设置完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 确保 OpenFGA 服务器正在运行"
echo "   docker run -d --name openfga -p 8080:8080 openfga/openfga run"
echo ""
echo "2. 配置 .env 文件中的 Store ID 和 Model ID"
echo ""
echo "3. 运行示例："
echo "   pnpm run dev"
echo ""
