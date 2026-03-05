# TradeFlow AI 质量保障方案

## 📋 目录

1. [质量保障体系概述](#质量保障体系概述)
2. [测试框架](#测试框架)
3. [代码质量检查](#代码质量检查)
4. [CI/CD 流程](#cicd-流程)
5. [Docker 部署](#docker-部署)
6. [开发环境设置](#开发环境设置)
7. [使用指南](#使用指南)

---

## 质量保障体系概述

### 目标
- ✅ 测试覆盖率 ≥ 80%
- ✅ CI 自动化运行率 100%
- ✅ 一键部署能力
- ✅ 代码质量标准化

### 架构
```
tradeflow-ai/
├── tradeflow/           # 源代码
│   ├── __init__.py
│   ├── strategy.py      # 策略模块
│   ├── analyzer.py      # 分析器模块
│   └── executor.py      # 执行器模块
├── tests/               # 测试套件
│   ├── __init__.py
│   ├── conftest.py      # Pytest 配置
│   ├── test_strategy.py # 策略测试
│   ├── test_analyzer.py # 分析器测试
│   ├── test_executor.py # 执行器测试
│   ├── integration/     # 集成测试
│   └── backtest/        # 回测验证
├── .github/
│   └── workflows/
│       └── ci-cd.yml    # CI/CD 配置
├── Dockerfile           # Docker 配置
├── requirements.txt     # 依赖管理
├── requirements-dev.txt # 开发依赖
├── Makefile            # 构建脚本
├── pytest.ini          # 测试配置
├── mypy.ini            # 类型检查配置
└── scripts/
    └── setup.sh        # 环境设置脚本
```

---

## 测试框架

### 技术栈
- **pytest** - 测试框架
- **pytest-cov** - 覆盖率统计
- **pytest-mock** - Mock 支持
- **pytest-asyncio** - 异步测试

### 测试类型

#### 1. 单元测试 (Unit Tests)
位置：`tests/test_*.py`

```python
# 示例：策略测试
def test_strategy_init():
    strategy = Strategy(name="测试策略")
    assert strategy.name == "测试策略"
    assert strategy.conditions == []
```

**覆盖率要求：**
- `strategy.py`: ≥ 90%
- `analyzer.py`: ≥ 90%
- `executor.py`: ≥ 90%

#### 2. 集成测试 (Integration Tests)
位置：`tests/integration/`

测试模块间协作：
- 策略 + 分析器
- 策略 + 执行器
- 完整交易流程

```python
@pytest.mark.integration
def test_full_trading_pipeline():
    strategy = Strategy.from_natural_language("均线交叉")
    analyzer = Analyzer()
    executor = Executor()
    # ... 完整流程测试
```

#### 3. 策略回测验证 (Backtest Validation)
位置：`tests/backtest/`

验证策略回测准确性：
- 均线交叉策略
- MACD 策略
- RSI 策略
- 多因子策略

```python
@pytest.mark.backtest
def test_moving_average_crossover_backtest():
    strategy = Strategy.from_natural_language("均线交叉策略")
    result = strategy.backtest("2023-01-01", "2024-01-01")
    assert "total_return" in result
```

### 运行测试

```bash
# 运行所有测试
make test

# 运行测试并生成覆盖率报告
make coverage

# 运行特定类型测试
pytest tests/ -m unit          # 单元测试
pytest tests/ -m integration   # 集成测试
pytest tests/ -m backtest      # 回测测试

# 运行特定文件测试
pytest tests/test_strategy.py -v
```

---

## 代码质量检查

### 工具链

| 工具 | 用途 | 配置 |
|------|------|------|
| **Black** | 代码格式化 | `--line-length=120` |
| **Flake8** | 代码风格检查 | `max-line-length=120` |
| **Mypy** | 类型检查 | Python 3.11 |
| **isort** | 导入排序 | `--profile=black` |

### 运行质量检查

```bash
# 运行所有质量检查
make quality

# 单独运行
make lint        # Flake8
make format      # Black + isort
make type-check  # Mypy
```

### 预提交钩子

自动在 commit 前运行：
- Black 格式化检查
- Flake8 linting
- Mypy 类型检查

```bash
# 安装预提交钩子（setup.sh 自动执行）
./scripts/setup.sh
```

---

## CI/CD 流程

### GitHub Actions 工作流

位置：`.github/workflows/ci-cd.yml`

### 触发条件
- Push 到 `main` / `develop` 分支
- Pull Request
- 每天凌晨 2 点定时运行

### 工作流步骤

#### 1. 代码质量检查 (Quality Check)
- ⏱️ 超时：10 分钟
- 📋 检查项：
  - Black 格式化
  - isort 导入排序
  - Flake8 linting
  - Mypy 类型检查

#### 2. 单元测试 (Unit Tests)
- ⏱️ 超时：15 分钟
- 🐍 Python 版本：3.9, 3.10, 3.11
- 📊 覆盖率要求：≥ 80%
- 📁 输出：
  - 覆盖率报告 (HTML + XML)
  - Codecov 上传

#### 3. 集成测试 (Integration Tests)
- ⏱️ 超时：20 分钟
- 🔗 测试模块间协作

#### 4. 策略回测验证 (Backtest Validation)
- ⏱️ 超时：30 分钟
- 📈 验证策略回测准确性

#### 5. Docker 构建 (Docker Build)
- ⏱️ 超时：15 分钟
- 🐳 多阶段构建
- 🚀 推送到 Docker Hub (仅 main 分支)

#### 6. 安全扫描 (Security Scan)
- ⏱️ 超时：10 分钟
- 🔒 工具：
  - Safety (依赖漏洞扫描)
  - Bandit (代码安全 linting)

### 部署就绪检查

所有检查通过后标记为 "Deploy Ready"：
- ✅ 质量检查通过
- ✅ 单元测试通过（覆盖率≥80%）
- ✅ 集成测试通过
- ✅ Docker 镜像构建成功
- ✅ 安全扫描无严重问题

---

## Docker 部署

### 镜像特点
- 🎯 多阶段构建，优化镜像大小
- 🔒 非 root 用户运行
- ❤️ 健康检查
- 📦 生产/开发多目标

### 构建镜像

```bash
# 生产镜像
make docker-build

# 开发镜像
docker build --target development -t tradeflow-ai:dev .
```

### 运行容器

```bash
# 运行生产容器
make docker-run

# 运行开发容器
docker run -it --rm tradeflow-ai:dev
```

### Docker Hub

自动推送（main 分支）：
```
tradeflow/tradeflow-ai:latest
tradeflow/tradeflow-ai:<commit-sha>
```

---

## 开发环境设置

### 一键设置

```bash
# 克隆仓库
git clone <repository-url>
cd tradeflow-ai

# 运行设置脚本
./scripts/setup.sh
```

### 手动设置

```bash
# 1. 创建虚拟环境
python3 -m venv venv

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements-dev.txt

# 4. 安装为可编辑模式
pip install -e .
```

### Makefile 命令

```bash
make help          # 查看所有命令
make install       # 安装生产依赖
make dev           # 安装开发依赖
make test          # 运行测试
make coverage      # 生成覆盖率报告
make lint          # 代码风格检查
make format        # 格式化代码
make type-check    # 类型检查
make quality       # 所有质量检查
make clean         # 清理构建文件
make build         # 构建分发包
make docker-build  # 构建 Docker 镜像
make deploy        # 一键部署
```

---

## 使用指南

### 日常开发流程

1. **拉取最新代码**
   ```bash
   git pull origin develop
   ```

2. **创建功能分支**
   ```bash
   git checkout -b feature/your-feature
   ```

3. **开发并运行测试**
   ```bash
   # 开发代码...
   
   # 运行测试
   make test
   
   # 运行质量检查
   make quality
   ```

4. **提交代码**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   # 预提交钩子自动运行质量检查
   ```

5. **推送并创建 PR**
   ```bash
   git push origin feature/your-feature
   # GitHub 上创建 Pull Request
   ```

6. **CI 自动运行**
   - 等待 GitHub Actions 完成
   - 确保所有检查通过 ✅

7. **代码审查合并**
   - 通过审查后合并到 develop

### 发布流程

1. **更新版本号**
   ```bash
   # 修改 setup.py 中的 version
   ```

2. **运行完整测试**
   ```bash
   make deploy
   ```

3. **构建并推送**
   ```bash
   make build
   make docker-push
   ```

4. **创建 Release**
   - GitHub 创建 Release
   - 上传构建产物

---

## 质量指标监控

### 测试覆盖率

目标：≥ 80%

查看报告：
```bash
make coverage
# 打开 htmlcov/index.html
```

### 代码质量

- Black 格式化：100% 符合
- Flake8：0 错误
- Mypy：0 类型错误

### CI 通过率

- 目标：100%
- 监控：GitHub Actions 面板

---

## 故障排查

### 测试失败

```bash
# 运行详细测试输出
make test-verbose

# 运行特定测试
pytest tests/test_module.py::test_function -v -s
```

### 覆盖率不达标

```bash
# 查看覆盖率详情
pytest tests/ --cov=tradeflow --cov-report=term-missing

# 添加缺失的测试用例
```

### CI 失败

1. 查看 GitHub Actions 日志
2. 本地复现：`make quality && make test`
3. 修复后重新推送

---

## 持续改进

- 每月审查测试覆盖率
- 定期更新依赖
- 优化 CI/CD 流程
- 收集并修复质量问题

---

**最后更新**: 2026-03-05  
**维护者**: TradeFlow AI Team
