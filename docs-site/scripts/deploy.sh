#!/bin/bash

# OpenFinAgent 文档站点部署脚本

set -e

echo "🚀 OpenFinAgent 文档站点部署脚本"
echo "================================"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python3"
    exit 1
fi

echo "✅ Python 版本：$(python3 --version)"

# 进入目录
cd "$(dirname "$0")/.."

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "📦 安装依赖..."
pip install -q -r requirements.txt

# 构建站点
echo "🔨 构建文档站点..."
mkdocs build --clean

# 检查构建结果
if [ -d "site" ]; then
    echo "✅ 构建成功！"
    echo "📁 输出目录：$(pwd)/site"
    echo ""
    echo "🌐 本地预览：mkdocs serve"
    echo "🚀 部署到 GitHub Pages: mkdocs gh-deploy --force"
else
    echo "❌ 构建失败"
    exit 1
fi
