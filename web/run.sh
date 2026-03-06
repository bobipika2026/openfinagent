#!/bin/bash

# OpenFinAgent Web UI 快速启动脚本

echo "=============================================="
echo "  OpenFinAgent Web UI - 快速启动"
echo "=============================================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python3"
    exit 1
fi

echo "✅ Python 版本：$(python3 --version)"

# 检查并安装依赖
echo ""
echo "📦 检查依赖..."

if ! python3 -c "import streamlit" &> /dev/null; then
    echo "⚠️  Streamlit 未安装，正在安装..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
    echo "✅ 依赖安装完成"
else
    echo "✅ Streamlit 已安装"
fi

# 运行测试
echo ""
echo "🧪 运行模块测试..."
python3 test_imports.py
if [ $? -ne 0 ]; then
    echo "⚠️  模块测试失败，但仍可尝试启动"
fi

# 启动 Streamlit
echo ""
echo "🚀 启动 Web UI..."
echo "   访问地址：http://localhost:8501"
echo "   按 Ctrl+C 停止服务"
echo ""

streamlit run app.py --server.port 8501 --server.address 0.0.0.0
