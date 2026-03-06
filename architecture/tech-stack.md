# TradeFlow AI 技术栈

**版本**: v1.0  
**最后更新**: 2026-03-06

---

## 1. 编程语言

### 1.1 核心语言

| 组件 | 语言 | 版本 | 选型理由 |
|------|------|------|----------|
| **核心引擎** | Python | 3.9+ | 量化生态丰富、开发效率高、中文社区活跃 |
| **性能关键路径** | Cython/Numba | - | JIT 编译加速指标计算和回测循环 |
| **Web 界面** (Phase 3) | TypeScript + React | 18+ | 类型安全、组件化、生态完善 |
| **CLI 工具** | Python | 3.9+ | 与核心库无缝集成 |

### 1.2 语言版本要求

```python
# pyproject.toml / setup.py
python_requires = ">=3.9,<4.0"
```

**为什么选择 Python 3.9+?**
- ✅ 类型注解增强 (`dict`/`list` 泛型)
- ✅ 性能优化 (字典优化、向量调用)
- ✅ 生态成熟 (pandas/numpy 完全支持)
- ❌ 不支持 Python 3.8 及以下 (类型注解语法限制)

---

## 2. 核心依赖库

### 2.1 数据处理

| 库 | 版本 | 用途 | 替代方案 |
|------|------|------|----------|
| **pandas** | ^1.5.0 | 数据框操作、时间序列 | - |
| **numpy** | ^1.23.0 | 数值计算、向量化 | - |
| **ta-lib** | ^0.4.0 | 技术指标库 | ta (纯 Python) |
| **bottleneck** | ^1.3.0 | 加速 pandas 运算 | - |

**选型理由**:
- pandas/numpy: 量化行业标准，生态完善
- ta-lib: C 语言实现，性能优秀 (100+ 技术指标)
- bottleneck: 可选优化，加速 rolling 操作

### 2.2 自然语言处理

| 库 | 版本 | 用途 | 优先级 |
|------|------|------|--------|
| **jieba** | ^0.42.0 | 中文分词 | P0 (必需) |
| **HanLP** | ^2.1.0 | 高级 NLP (词性标注、依存句法) | P1 (可选) |
| **transformers** | ^4.30.0 | BERT 意图分类 | P2 (Phase 2) |

**选型理由**:
- jieba: 轻量级、离线可用、满足基础需求
- HanLP: 更准确的分词和词性标注 (需要下载模型)
- transformers: 高精度意图识别 (需要 GPU 加速)

### 2.3 可视化

| 库 | 版本 | 用途 | 说明 |
|------|------|------|------|
| **matplotlib** | ^3.6.0 | 基础图表 | 核心依赖 |
| **seaborn** | ^0.12.0 | 统计图表 | 交易分布图 |
| **mplfinance** | ^0.1.9 | K 线图 | K 线 + 指标 |
| **plotly** | ^5.15.0 | 交互式图表 | Phase 3 Web 界面 |

### 2.4 数据源

| 库 | 版本 | 用途 | 市场 |
|------|------|------|------|
| **akshare** | ^1.10.0 | A 股/期货/基金数据 | 中国 |
| **yfinance** | ^0.2.0 | 美股/港股数据 | 美国/香港 |
| **ccxt** | ^4.0.0 | 加密货币数据 | 币安/OKX 等 |

**选型理由**:
- akshare: 免费、全面、稳定 (A 股首选)
- yfinance: 雅虎财经官方接口 (美股首选)
- ccxt: 统一 API 支持 100+ 交易所

### 2.5 工具库

| 库 | 版本 | 用途 |
|------|------|------|
| **tqdm** | ^4.65.0 | 进度条 |
| **rich** | ^13.0.0 | 美化控制台输出 |
| **click** | ^8.1.0 | CLI 命令行框架 |
| **pydantic** | ^2.0.0 | 数据验证、配置管理 |
| **loguru** | ^0.7.0 | 日志记录 |

---

## 3. 开发工具链

### 3.1 代码质量

| 工具 | 用途 | 配置 |
|------|------|------|
| **black** | 代码格式化 | `black src/ tests/` |
| **isort** | 导入排序 | `isort src/ tests/` |
| **flake8** | 代码检查 | `flake8 src/ tests/` |
| **mypy** | 类型检查 | `mypy src/` |
| **pylint** | 代码评分 | `pylint src/` |

### 3.2 测试框架

| 工具 | 用途 | 说明 |
|------|------|------|
| **pytest** | 单元测试 | 核心测试框架 |
| **pytest-cov** | 覆盖率 | `pytest --cov=src` |
| **pytest-mock** | Mock 支持 | 模拟外部依赖 |
| **hypothesis** | 属性测试 | 随机生成测试用例 |

### 3.3 文档工具

| 工具 | 用途 | 说明 |
|------|------|------|
| **mkdocs** | 文档站点 | Markdown 文档生成 |
| **mkdocs-material** | 文档主题 | 美观的 Material 主题 |
| **mkdocstrings** | API 文档 | 自动生成 API 文档 |
| **pdoc** | 备用方案 | 简单 API 文档 |

---

## 4. 数据库选型

### 4.1 当前阶段 (v0.1-v0.3)

| 数据类型 | 存储方案 | 说明 |
|----------|----------|------|
| **K 线数据** | 内存 (DataFrame) + 本地缓存 (Parquet) | 轻量级、快速 |
| **策略配置** | JSON/YAML 文件 | 简单、易读 |
| **回测结果** | JSON + CSV | 便于分享和导出 |
| **用户配置** | ~/.tradeflow/config.yaml | 本地配置 |

### 4.2 未来规划 (v0.5+)

| 数据类型 | 数据库 | 选型理由 |
|----------|--------|----------|
| **K 线数据** | TimescaleDB | 时序优化、压缩率高 |
| **用户数据** | PostgreSQL | ACID、复杂查询 |
| **缓存** | Redis | 热点数据加速 |
| **文件存储** | MinIO / S3 | 策略文件、回测报告 |

---

## 5. 部署方案

### 5.1 Python 包分发

```bash
# 构建
python setup.py sdist bdist_wheel

# 发布到 PyPI
twine upload dist/*

# 安装
pip install tradeflow-ai
```

### 5.2 Docker 容器 (Phase 3)

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY examples/ ./examples/

ENTRYPOINT ["python", "-m", "tradeflow"]
```

### 5.3 Web 服务部署 (Phase 3)

| 组件 | 技术 | 说明 |
|------|------|------|
| **后端** | FastAPI | 异步高性能 API |
| **前端** | React + Vite | 快速构建 SPA |
| **部署** | Docker + K8s | 容器化编排 |
| **CDN** | Cloudflare | 静态资源加速 |

---

## 6. 版本管理

### 6.1 语义化版本

```
主版本。次版本.修订版本
  ↑      ↑      ↑
  │      │      └─►  Bug 修复 (向后兼容)
  │      └────────►  新功能 (向后兼容)
  └───────────────►  破坏性变更
```

**示例**:
- `v0.1.0` - Alpha 发布
- `v0.2.0` - 新增 RSI/MACD 策略
- `v1.0.0` - 生产就绪

### 6.2 分支策略

```
main (受保护)
  │
  ├── develop (集成分支)
  │     │
  │     ├── feature/nlp-parser
  │     ├── feature/backtest-parallel
  │     └── fix/issue-123
  │
  └── release/v0.2.0 (发布分支)
```

---

## 7. CI/CD

### 7.1 GitHub Actions 工作流

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11"]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: pip install -r requirements-dev.txt
    
    - name: Lint
      run: |
        black --check src/ tests/
        flake8 src/ tests/
        mypy src/
    
    - name: Test
      run: pytest tests/ -v --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  publish:
    needs: test
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Build and publish
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_TOKEN }}
```

---

## 8. 性能基准

### 8.1 回测性能目标

| 场景 | 数据量 | 目标时间 | 当前性能 |
|------|--------|----------|----------|
| 单策略回测 | 1 年日线 | < 1 秒 | 0.5 秒 |
| 单策略回测 | 10 年日线 | < 5 秒 | 3 秒 |
| 多策略对比 | 5 策略×1 年 | < 10 秒 | 8 秒 |
| 参数扫描 | 100 组参数 | < 30 秒 | - (Phase 2) |

### 8.2 优化技术

```python
# 1. 向量化计算 (替代循环)
# ❌ 慢
for i in range(len(data)):
    ma[i] = data['close'][i-20:i].mean()

# ✅ 快
ma = data['close'].rolling(20).mean()

# 2. Numba JIT 加速
from numba import jit

@jit(nopython=True)
def calculate_signal(prices):
    # 编译为机器码
    pass

# 3. 并行回测
from multiprocessing import Pool

with Pool() as p:
    results = p.map(run_backtest, strategy_list)
```

---

## 9. 安全考虑

### 9.1 依赖安全

```bash
# 定期扫描漏洞
pip install pip-audit
pip-audit

# 或使用 safety
pip install safety
safety check
```

### 9.2 代码执行安全

```python
# 限制用户策略的危险操作
RESTRICTED_MODULES = [
    'os', 'sys', 'subprocess', 'socket',
    'multiprocessing', 'threading'
]

# 沙箱环境执行
import restricted_exec
restricted_exec.exec_user_strategy(code)
```

---

## 10. 技术决策记录 (ADR)

### ADR-001: 选择 Python 作为核心语言

**日期**: 2026-03-05  
**状态**: 已采纳

**背景**: 需要选择核心开发语言

**选项**:
1. Python - 量化生态丰富
2. Rust - 性能优秀但生态弱
3. Go - 性能好但量化库少

**决策**: 选择 Python

**理由**:
- pandas/numpy 生态无可替代
- 目标用户熟悉 Python
- 性能瓶颈可用 Cython/Numba 优化

### ADR-002: 使用 akshare 作为 A 股数据源

**日期**: 2026-03-05  
**状态**: 已采纳

**理由**:
- 免费开源
- 数据全面 (A 股/期货/基金)
- 社区活跃、维护频繁

---

## 11. 依赖管理

### 11.1 依赖分级

```
# 核心依赖 (必需)
pandas, numpy, matplotlib, jieba, akshare

# 可选依赖 (增强功能)
ta-lib, hanlp, plotly, yfinance, ccxt

# 开发依赖 (开发环境)
pytest, black, flake8, mypy, mkdocs
```

### 11.2 requirements.txt 结构

```txt
# requirements.txt - 核心依赖
pandas>=1.5.0,<2.0.0
numpy>=1.23.0,<2.0.0
matplotlib>=3.6.0,<4.0.0
jieba>=0.42.0,<1.0.0
akshare>=1.10.0,<2.0.0
tqdm>=4.65.0,<5.0.0
pydantic>=2.0.0,<3.0.0

# requirements-dev.txt - 开发依赖
-r requirements.txt
pytest>=7.0.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0
mkdocs>=1.4.0
mkdocs-material>=9.0.0
```

---

*文档版本：v1.0 | 创建时间：2026-03-06*
