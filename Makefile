# TradeFlow AI - Makefile
# 一键构建、测试、部署

.PHONY: help install dev test lint format type-check coverage clean build docker-build docker-run deploy

# Default target
help:
	@echo "TradeFlow AI - 可用命令:"
	@echo "  make install        - 安装生产依赖"
	@echo "  make dev            - 安装开发依赖"
	@echo "  make test           - 运行单元测试"
	@echo "  make test-verbose   - 运行详细测试输出"
	@echo "  make coverage       - 运行测试并生成覆盖率报告"
	@echo "  make lint           - 代码风格检查 (flake8)"
	@echo "  make format         - 格式化代码 (black, isort)"
	@echo "  make type-check     - 类型检查 (mypy)"
	@echo "  make quality        - 运行所有质量检查"
	@echo "  make clean          - 清理构建文件"
	@echo "  make build          - 构建分发包"
	@echo "  make docker-build   - 构建 Docker 镜像"
	@echo "  make docker-run     - 运行 Docker 容器"
	@echo "  make deploy         - 一键部署"

# Installation
install:
	@echo "📦 安装生产依赖..."
	pip install -r requirements.txt

dev:
	@echo "🔧 安装开发依赖..."
	pip install -r requirements-dev.txt
	pip install -e .

# Testing
test:
	@echo "🧪 运行单元测试..."
	pytest tests/ -v

test-verbose:
	@echo "🧪 运行详细测试..."
	pytest tests/ -vv -s

coverage:
	@echo "📊 生成测试覆盖率报告..."
	pytest tests/ --cov=tradeflow --cov-report=html --cov-report=term-missing --cov-fail-under=65
	@echo "✅ 覆盖率报告已生成：htmlcov/index.html"

# Code Quality
lint:
	@echo "🔍 代码风格检查..."
	flake8 tradeflow/ tests/ --max-line-length=120 --exclude=__pycache__

format:
	@echo "🎨 格式化代码..."
	black tradeflow/ tests/ --line-length=120
	isort tradeflow/ tests/ --profile=black

type-check:
	@echo "📝 类型检查..."
	mypy tradeflow/ --ignore-missing-imports

quality: lint format type-check
	@echo "✅ 所有质量检查完成"

# Build
clean:
	@echo "🧹 清理构建文件..."
	rm -rf build/ dist/ *.egg-info __pycache__/ .pytest_cache/ .mypy_cache/
	rm -rf htmlcov/ .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

build: clean
	@echo "📦 构建分发包..."
	python setup.py sdist bdist_wheel

# Docker
docker-build:
	@echo "🐳 构建 Docker 镜像..."
	docker build -t tradeflow-ai:latest .

docker-run:
	@echo "🐳 运行 Docker 容器..."
	docker run -it --rm tradeflow-ai:latest

docker-push:
	@echo "🚀 推送 Docker 镜像..."
	docker tag tradeflow-ai:latest tradeflow/tradeflow-ai:latest
	docker push tradeflow/tradeflow-ai:latest

# Deployment
deploy: quality test docker-build
	@echo "🚀 一键部署完成"
	@echo "✅ 质量检查通过"
	@echo "✅ 测试通过"
	@echo "✅ Docker 镜像构建完成"

# Development utilities
setup-venv:
	@echo "🔧 创建虚拟环境..."
	python -m venv venv
	@echo "✅ 虚拟环境已创建，运行 'source venv/bin/activate' 激活"

requirements:
	@echo "📝 更新依赖文件..."
	pip freeze > requirements.txt

# Backtesting
backtest:
	@echo "📈 运行策略回测..."
	python -m tradeflow.backtest

# Database migrations (if needed)
migrate:
	@echo "🗄️ 运行数据库迁移..."
	@echo "暂无迁移脚本"
