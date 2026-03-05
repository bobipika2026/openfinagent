#!/bin/bash
# TradeFlow AI 开发环境一键设置脚本
# 使用方法：./scripts/setup.sh

set -e

echo "🚀 TradeFlow AI 开发环境设置"
echo "=============================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Python 版本
check_python() {
    echo -e "\n${YELLOW}检查 Python 版本...${NC}"
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}错误：未找到 Python 3${NC}"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "✅ Python $PYTHON_VERSION"
}

# 创建虚拟环境
create_venv() {
    echo -e "\n${YELLOW}创建虚拟环境...${NC}"
    if [ -d "venv" ]; then
        echo "⚠️  虚拟环境已存在，跳过"
    else
        python3 -m venv venv
        echo "✅ 虚拟环境创建成功"
    fi
}

# 激活虚拟环境
activate_venv() {
    echo -e "\n${YELLOW}激活虚拟环境...${NC}"
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
}

# 安装依赖
install_dependencies() {
    echo -e "\n${YELLOW}安装依赖...${NC}"
    pip install --upgrade pip
    
    if [ -f "requirements-dev.txt" ]; then
        pip install -r requirements-dev.txt
        echo "✅ 开发依赖安装完成"
    elif [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        echo "✅ 生产依赖安装完成"
    else
        echo -e "${RED}错误：未找到 requirements 文件${NC}"
        exit 1
    fi
}

# 安装预提交钩子
setup_precommit() {
    echo -e "\n${YELLOW}设置预提交钩子...${NC}"
    if [ -d ".git" ]; then
        cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for TradeFlow AI

echo "🔍 运行代码质量检查..."

# 运行 Black 格式化检查
black --check tradeflow/ tests/ --line-length=120

# 运行 Flake8 linting
flake8 tradeflow/ tests/ --max-line-length=120 --exclude=__pycache__

# 运行 Mypy 类型检查
mypy tradeflow/ --ignore-missing-imports

echo "✅ 预提交检查通过"
EOF
        chmod +x .git/hooks/pre-commit
        echo "✅ 预提交钩子设置完成"
    else
        echo "⚠️  未检测到 Git 仓库，跳过预提交钩子设置"
    fi
}

# 运行测试
run_tests() {
    echo -e "\n${YELLOW}运行测试...${NC}"
    pytest tests/ -v --tb=short
    echo "✅ 测试完成"
}

# 生成覆盖率报告
generate_coverage() {
    echo -e "\n${YELLOW}生成测试覆盖率报告...${NC}"
    pytest tests/ --cov=tradeflow --cov-report=html --cov-report=term-missing
    echo "✅ 覆盖率报告已生成：htmlcov/index.html"
}

# 主函数
main() {
    check_python
    create_venv
    activate_venv
    install_dependencies
    setup_precommit
    
    echo -e "\n${GREEN}=============================="
    echo "🎉 开发环境设置完成！"
    echo "==============================${NC}"
    echo ""
    echo "下一步："
    echo "  1. 激活虚拟环境：source venv/bin/activate"
    echo "  2. 运行测试：make test"
    echo "  3. 查看覆盖率：make coverage"
    echo "  4. 代码格式化：make format"
    echo ""
    echo "可用命令："
    echo "  make help     - 查看所有可用命令"
    echo "  make quality  - 运行所有质量检查"
    echo "  make dev      - 安装开发依赖"
    echo ""
}

# 执行主函数
main
