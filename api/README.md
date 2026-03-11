# OpenFinAgent API 文档

## 快速开始

### 安装依赖

```bash
pip install fastapi uvicorn pydantic
```

### 启动 API 服务

```bash
# 方法 1: 使用启动脚本
cd /root/.openclaw/workspace/projects/tradeflow-ai
python api/run_api.py

# 方法 2: 使用 uvicorn
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### 访问文档

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

---

## API 路由

### 健康检查

```http
GET /health
```

**响应示例**:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## 策略工厂

### 1. 通过自然语言创建策略

```http
POST /api/v1/strategies/from-text
Content-Type: application/json

{
  "description": "当 5 日均线上穿 20 日均线时买入，下穿时卖出，初始资金 10 万元",
  "initial_capital": 100000,
  "symbol": "600519.SH"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "策略创建成功",
  "strategy_id": "strat_001",
  "strategy_name": "均线交叉策略",
  "backtest_result": {
    "total_return": 15.5,
    "annual_return": 15.5,
    "sharpe_ratio": 1.2,
    "max_drawdown": -8.3,
    "win_rate": 65.0,
    "total_trades": 24,
    "profit_loss_ratio": 2.1
  },
  "stored": true
}
```

### 2. 通过搜索创建策略

```http
POST /api/v1/strategies/from-search
Content-Type: application/json

{
  "keywords": "均线交叉",
  "initial_capital": 100000
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "找到 3 个策略",
  "strategies": [
    {
      "strategy_id": "strat_001",
      "strategy_name": "均线交叉策略",
      "backtest_result": {...},
      "stored": true
    }
  ]
}
```

### 3. 优化策略参数

```http
POST /api/v1/strategies/{strategy_id}/optimize
Content-Type: application/json

{
  "generations": 50,
  "population_size": 20
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "策略优化完成",
  "strategy_id": "strat_001",
  "optimized_params": {
    "short_window": 7,
    "long_window": 25
  },
  "backtest_result": {...},
  "improvement": 12.5
}
```

---

## 选股引擎

### 1. 创建股票池

```http
POST /api/v1/stock-pools
Content-Type: application/json

{
  "name": "价值选股池",
  "strategy_id": "strat_001",
  "conditions": [
    {
      "field": "pe_ratio",
      "operator": "between",
      "value": 10,
      "value2": 30
    },
    {
      "field": "market_cap",
      "operator": ">",
      "value": 1000000000
    }
  ],
  "market": "A 股",
  "max_stocks": 100
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "股票池创建成功",
  "pool_id": "pool_001",
  "name": "价值选股池",
  "stock_count": 50,
  "stocks": [
    {
      "symbol": "600519.SH",
      "name": "贵州茅台",
      "price": 1800.5,
      "change_percent": 2.3,
      "market_cap": 2260000000000,
      "pe_ratio": 28.5
    }
  ],
  "created_at": "2024-03-11T10:00:00"
}
```

### 2. 获取股票池列表

```http
GET /api/v1/stock-pools
```

**响应示例**:
```json
{
  "success": true,
  "message": "获取成功",
  "pools": [
    {
      "pool_id": "pool_001",
      "name": "价值选股池",
      "stock_count": 50,
      "created_at": "2024-03-11T10:00:00",
      "updated_at": "2024-03-11T10:00:00"
    }
  ]
}
```

### 3. 获取股票池详情

```http
GET /api/v1/stock-pools/{pool_id}
```

---

## 监控中心

### 1. 启动监控任务

```http
POST /api/v1/monitoring/start
Content-Type: application/json

{
  "task_name": "茅台监控",
  "strategy_id": "strat_001",
  "symbols": ["600519.SH"],
  "interval": 60,
  "notify_enabled": true,
  "notify_channels": ["app", "email"]
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "监控任务已启动：task_001",
  "data": {
    "task_id": "task_001"
  }
}
```

### 2. 停止监控任务

```http
POST /api/v1/monitoring/stop
Content-Type: application/json

{
  "task_id": "task_001"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "监控任务已停止：task_001"
}
```

### 3. 获取监控信号

```http
GET /api/v1/monitoring/signals?task_id=task_001
```

**响应示例**:
```json
{
  "success": true,
  "message": "获取成功",
  "signals": [
    {
      "signal_id": "sig_001",
      "task_id": "task_001",
      "symbol": "600519.SH",
      "signal_type": "buy",
      "price": 1800.5,
      "timestamp": "2024-03-11T10:30:00",
      "strength": 0.85,
      "message": "均线金叉信号"
    }
  ]
}
```

---

## 错误处理

### 错误响应格式

```json
{
  "success": false,
  "message": "错误描述",
  "status_code": 500
}
```

### 常见错误码

- `400`: 请求参数错误
- `404`: 资源不存在
- `500`: 服务器内部错误

---

## 使用示例

### Python 示例

```python
import requests

# 创建策略
response = requests.post(
    "http://localhost:8000/api/v1/strategies/from-text",
    json={
        "description": "当 5 日均线上穿 20 日均线时买入",
        "initial_capital": 100000
    }
)

result = response.json()
print(f"策略 ID: {result['strategy_id']}")
print(f"总收益率：{result['backtest_result']['total_return']}%")

# 创建股票池
response = requests.post(
    "http://localhost:8000/api/v1/stock-pools",
    json={
        "name": "测试股票池",
        "strategy_id": result['strategy_id'],
        "conditions": [],
        "market": "A 股"
    }
)

# 启动监控
response = requests.post(
    "http://localhost:8000/api/v1/monitoring/start",
    json={
        "task_name": "测试监控",
        "strategy_id": result['strategy_id'],
        "symbols": ["600519.SH"],
        "interval": 60
    }
)
```

### cURL 示例

```bash
# 创建策略
curl -X POST http://localhost:8000/api/v1/strategies/from-text \
  -H "Content-Type: application/json" \
  -d '{"description": "均线交叉策略", "initial_capital": 100000}'

# 获取股票池
curl http://localhost:8000/api/v1/stock-pools

# 启动监控
curl -X POST http://localhost:8000/api/v1/monitoring/start \
  -H "Content-Type: application/json" \
  -d '{"task_name": "监控任务", "strategy_id": "strat_001", "symbols": ["600519.SH"]}'
```

---

## 开发说明

### 添加新路由

1. 在 `api/routes.py` 中定义路由
2. 在 `api/schemas.py` 中定义请求/响应模型
3. 在 `api/__init__.py` 中注册路由

### 测试 API

```bash
# 运行测试
pytest tests/api/

# 手动测试
http POST :8000/api/v1/strategies/from-text description="测试"
```

### 部署

```bash
# 生产环境部署
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4

# 使用 gunicorn
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

## 更新日志

### v1.0.0 (2024-03-11)

- ✅ 策略工厂 API
- ✅ 选股引擎 API
- ✅ 监控中心 API
- ✅ 完整的 Swagger 文档
- ✅ 错误处理机制
