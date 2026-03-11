# OpenFinAgent Web UI 和 API 快速启动指南

## 🚀 快速开始

### 前置条件

确保已安装以下依赖：

```bash
pip install streamlit fastapi uvicorn pydantic pandas numpy
```

### 1. 启动 Web UI

```bash
# 进入 web 目录
cd /root/.openclaw/workspace/projects/tradeflow-ai/web

# 启动 Streamlit 应用
streamlit run app.py
```

**访问地址**: http://localhost:8501

页面导航：
- 🏠 首页
- ✨ 一键回测
- 📊 策略对比
- 📚 策略库
- 🤖 策略工厂 (新增)
- 📈 选股引擎 (新增)
- 🔔 监控中心 (新增)

### 2. 启动 API 服务

```bash
# 进入项目根目录
cd /root/.openclaw/workspace/projects/tradeflow-ai

# 方法 1: 使用启动脚本
python api/run_api.py

# 方法 2: 直接使用 uvicorn
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

**访问地址**:
- API 文档：http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- 健康检查：http://localhost:8000/health

### 3. 运行测试

```bash
# 进入项目根目录
cd /root/.openclaw/workspace/projects/tradeflow-ai

# 运行 API 测试
pytest tests/api/test_api.py -v

# 查看测试覆盖率
pytest tests/api/test_api.py --cov=api --cov-report=html
```

---

## 📋 使用示例

### Web UI 使用流程

#### 策略工厂

1. 访问 **🤖 策略工厂** 页面
2. 在 **创建策略** 标签页输入策略描述
   ```
   当 5 日均线上穿 20 日均线时买入
   当 5 日均线下穿 20 日均线时卖出
   初始资金 10 万元
   ```
3. 点击 **🚀 创建策略**
4. 查看 **策略预览** 和 **回测结果**
5. 在 **入库状态** 保存策略到库

#### 选股引擎

1. 访问 **📈 选股引擎** 页面
2. 在 **策略选择** 标签页选择策略
3. 在 **条件配置** 设置选股条件
   - 基本面：PE、PB、市值
   - 技术面：均线、量比
4. 点击 **🔍 开始选股**
5. 在 **批量回测** 查看结果
6. 在 **股票池** 管理和导出

#### 监控中心

1. 访问 **🔔 监控中心** 页面
2. 在 **监控任务** 创建新任务
   - 输入任务名称
   - 选择策略
   - 添加监控标的
   - 配置通知
3. 在 **实时信号** 查看信号
4. 在 **通知历史** 查看记录
5. 在 **通知设置** 配置渠道

### API 使用示例

#### 创建策略

```bash
curl -X POST http://localhost:8000/api/v1/strategies/from-text \
  -H "Content-Type: application/json" \
  -d '{
    "description": "当 5 日均线上穿 20 日均线时买入",
    "initial_capital": 100000,
    "symbol": "600519.SH"
  }'
```

#### 创建股票池

```bash
curl -X POST http://localhost:8000/api/v1/stock-pools \
  -H "Content-Type: application/json" \
  -d '{
    "name": "价值选股池",
    "strategy_id": "strat_001",
    "conditions": [
      {
        "field": "pe_ratio",
        "operator": "between",
        "value": 10,
        "value2": 30
      }
    ],
    "market": "A 股"
  }'
```

#### 启动监控

```bash
curl -X POST http://localhost:8000/api/v1/monitoring/start \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "茅台监控",
    "strategy_id": "strat_001",
    "symbols": ["600519.SH"],
    "interval": 60
  }'
```

#### Python SDK

```python
import requests

BASE_URL = "http://localhost:8000"

# 创建策略
response = requests.post(
    f"{BASE_URL}/api/v1/strategies/from-text",
    json={
        "description": "均线交叉策略",
        "initial_capital": 100000
    }
)
strategy = response.json()
print(f"策略 ID: {strategy['strategy_id']}")

# 创建股票池
response = requests.post(
    f"{BASE_URL}/api/v1/stock-pools",
    json={
        "name": "测试股票池",
        "strategy_id": strategy['strategy_id'],
        "conditions": []
    }
)
pool = response.json()
print(f"股票池 ID: {pool['pool_id']}")

# 启动监控
response = requests.post(
    f"{BASE_URL}/api/v1/monitoring/start",
    json={
        "task_name": "测试监控",
        "strategy_id": strategy['strategy_id'],
        "symbols": ["600519.SH"]
    }
)
task = response.json()
print(f"任务 ID: {task['data']['task_id']}")
```

---

## 🔧 故障排查

### Web UI 无法启动

```bash
# 检查 Streamlit 是否安装
pip show streamlit

# 检查端口是否被占用
lsof -i :8501

# 使用其他端口
streamlit run app.py --server.port 8502
```

### API 无法启动

```bash
# 检查 FastAPI 是否安装
pip show fastapi uvicorn

# 检查端口是否被占用
lsof -i :8000

# 查看详细日志
uvicorn api:app --log-level debug
```

### 导入错误

```bash
# 确保在项目根目录
cd /root/.openclaw/workspace/projects/tradeflow-ai

# 检查 Python 路径
python -c "import sys; print(sys.path)"

# 手动添加路径
export PYTHONPATH=/root/.openclaw/workspace/projects/tradeflow-ai:$PYTHONPATH
```

### 依赖缺失

```bash
# 安装 Web UI 依赖
pip install -r web/requirements.txt

# 安装 API 依赖
pip install -r api/requirements.txt

# 安装项目依赖
pip install -r requirements.txt
```

---

## 📊 性能优化

### 生产环境部署

**Web UI**:
```bash
# 使用 Nginx 反向代理
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

**API**:
```bash
# 使用多进程
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 或使用 uvicorn 集群
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

### 缓存配置

在 `.streamlit/config.toml` 中配置：

```toml
[server]
headless = true
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

---

## 📖 更多文档

- [API 详细文档](api/README.md)
- [Web UI 部署指南](web/DEPLOYMENT.md)
- [功能规格说明](FEATURE_SPEC_v0.4.md)
- [开发报告](docs/WEB_UI_API_DEVELOPMENT.md)

---

## 🆘 获取帮助

如遇问题，请查看：

1. 日志文件（控制台输出）
2. API 文档（Swagger UI）
3. 测试用例（参考实现）
4. 源代码注释

---

_OpenFinAgent Team | v1.0.0 | 2024-03-11_
