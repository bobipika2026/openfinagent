# OpenFinAgent v0.3.0 发布说明

**发布日期**: 2026-03-06  
**版本**: v0.3.0  
**类型**: 功能增强 + 性能优化

---

## 🎉 新功能

### 1. 新增数据源

#### Binance 数据源 (加密货币)
```python
from data.binance_source import BinanceDataSource

source = BinanceDataSource()
data = source.get_klines('BTC/USDT', '1d', '2024-01-01', '2024-01-31')
```
- ✅ 支持 BTC/USDT 等主流币种
- ✅ 14 种时间周期 (1m, 5m, 15m, 1h, 4h, 1d...)
- ✅ 无需 API key

#### Tushare 分钟线
```python
from data.sources import TushareDataSource

# 5 分钟线
source = TushareDataSource(token='your_token', freq='5m')
data = source.get_data('000001.SZ', '2024-01-01', '2024-01-02')
```
- ✅ 支持 1m, 5m, 15m, 30m, 60m 分钟线
- ✅ Token 配置支持

---

### 2. 策略优化器增强

#### 遗传算法优化器
```python
from optimization.genetic_optimizer import GeneticOptimizer, ParameterBound

optimizer = GeneticOptimizer(population_size=50, generations=100)
param_bounds = [
    ParameterBound('window', 10, 100, dtype='int'),
    ParameterBound('threshold', 0.1, 1.0, dtype='float')
]

best = optimizer.optimize(MyStrategy, param_bounds, backtest, data)
```
- ✅ 种群进化
- ✅ 交叉变异
- ✅ 精英保留
- ✅ 并行评估

#### 参数热力图
```python
from visualization.heatmap import ParameterHeatmap

heatmap = ParameterHeatmap()
result = heatmap.scan(MyStrategy, 'window', [10,20,30], 'threshold', [0.3,0.5,0.7], ...)
heatmap.plot(result, save_path='heatmap.png')
```
- ✅ 双参数扫描
- ✅ 热力图展示
- ✅ 最优参数标记
- ✅ 交互式图表

---

### 3. 性能优化

#### 优化回测引擎
```python
from backtest.optimized_engine import optimized_backtest

result = optimized_backtest(strategy, data)
# 速度提升 50%+
```
- ✅ NumPy 向量化
- ✅ 缓存机制
- ✅ 并行回测
- ⚡ **速度提升 50%+**

---

## 📊 质量提升

| 指标 | v0.2.0 | v0.3.0 | 提升 |
|------|--------|--------|------|
| 测试覆盖率 | 40% | 65% | +25% |
| 回测速度 | 1x | 1.5x | +50% |
| 类型注解 | 部分 | 完整 | ✅ |
| 文档完整度 | 基础 | 完善 | ✅ |

---

## 📦 安装

```bash
# 克隆仓库
git clone https://github.com/bobipika2026/openfinagent.git
cd openfinagent

# 安装依赖
pip install -r requirements.txt

# 可选：加密货币数据
pip install requests

# 可选：A 股分钟线
pip install tushare

# 可选：交互式图表
pip install plotly
```

---

## 🚀 快速开始

```python
# 1. 获取数据
from data.binance_source import BinanceDataSource
source = BinanceDataSource()
data = source.get_klines('BTC/USDT', '1h', '2024-01-01', '2024-01-31')

# 2. 定义策略
class MyStrategy:
    def __init__(self, window=20):
        self.window = window
    
    def generate_signals(self, data):
        import numpy as np
        signals = np.zeros(len(data), dtype=np.int8)
        ma = data['close'].rolling(self.window).mean()
        signals[data['close'] > ma] = 1
        signals[data['close'] < ma] = -1
        return signals

# 3. 优化参数
from optimization.genetic_optimizer import GeneticOptimizer, ParameterBound
optimizer = GeneticOptimizer()
best = optimizer.optimize(MyStrategy, [ParameterBound('window', 10, 100, dtype='int')], backtest, data)

# 4. 回测验证
from backtest.optimized_engine import optimized_backtest
strategy = MyStrategy(**best.params)
result = optimized_backtest(strategy, data)
print(f"夏普比率：{result.sharpe_ratio:.2f}")
```

---

## 📚 文档

- **完整功能文档**: `docs/v0.3_features.md`
- **使用示例**: `examples/v0.3_features_demo.py`
- **验证脚本**: `verify_features.py`

---

## 🧪 测试

```bash
# 运行所有测试
python3 -m pytest tests/ -v

# 查看覆盖率
python3 -m pytest tests/ --cov=src --cov-report=html

# 验证功能
python3 verify_features.py
```

---

## ⚠️ 注意事项

1. **Tushare Token**: 使用 Tushare 分钟线需要 API token
   - 注册地址：https://tushare.pro
   - 设置环境变量：`export TUSHARE_TOKEN=your_token`

2. **网络要求**: Binance 数据源需要访问国际互联网

3. **性能建议**: 大数据集建议使用优化引擎 + 缓存
   ```python
   engine = OptimizedBacktestEngine(use_cache=True)
   ```

---

## 🎯 下一步 (v0.4.0)

- [ ] 更多数据源 (Wind, Choice)
- [ ] 贝叶斯优化
- [ ] 实时数据流
- [ ] 策略组合优化

---

## 📞 支持

- **GitHub Issues**: https://github.com/bobipika2026/openfinagent/issues
- **文档**: https://github.com/bobipika2026/openfinagent/tree/main/docs

---

**Happy Trading! 📈**
