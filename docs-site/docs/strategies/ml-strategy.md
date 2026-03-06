# 机器学习策略

机器学习策略（Machine Learning Strategy）利用机器学习算法分析市场数据，预测价格走势并生成交易信号。

## 📖 策略原理

### 核心思想

- **数据驱动**: 从历史数据中学习规律
- **特征工程**: 提取有效的预测特征
- **模型预测**: 使用 ML 模型预测未来走势

### 常用算法

```
- 随机森林 (Random Forest)
- 梯度提升树 (XGBoost/LightGBM)
- 支持向量机 (SVM)
- K 近邻 (KNN)
```

## 📊 策略流程图

```mermaid
graph LR
    A[原始数据] --> B[特征工程]
    B --> C[训练模型]
    C --> D[模型验证]
    D --> E[生成预测]
    E --> F[交易信号]
```

## 💻 代码实现

```python
from openfinagent import Strategy, Signal, SignalType
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

class MLStrategy(Strategy):
    """
    机器学习策略
    
    参数:
        lookback: 回看周期 (默认：60)
        n_estimators: 树的数量 (默认：100)
        retrain_freq: 重新训练频率 (默认：20)
    """
    
    def __init__(self, lookback: int = 60,
                 n_estimators: int = 100,
                 retrain_freq: int = 20):
        super().__init__(name="MLStrategy")
        self.lookback = lookback
        self.n_estimators = n_estimators
        self.retrain_freq = retrain_freq
        
        # 初始化模型
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=5,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.train_count = 0
    
    def create_features(self, prices):
        """创建特征"""
        features = []
        
        # 收益率特征
        for i in [1, 3, 5, 10]:
            if len(prices) > i:
                ret = (prices[-1] - prices[-i]) / prices[-i]
                features.append(ret)
        
        # 波动率特征
        if len(prices) > 10:
            vol = np.std(prices[-10:]) / np.mean(prices[-10:])
            features.append(vol)
        
        # 均线特征
        for window in [5, 10, 20]:
            if len(prices) > window:
                ma = np.mean(prices[-window:])
                features.append((prices[-1] - ma) / ma)
        
        return np.array(features)
    
    def create_labels(self, prices, horizon=5):
        """创建标签"""
        labels = []
        for i in range(len(prices) - horizon):
            future_return = (prices[i + horizon] - prices[i]) / prices[i]
            labels.append(1 if future_return > 0 else 0)
        return np.array(labels)
    
    def train_model(self, prices):
        """训练模型"""
        X = []
        y = []
        
        for i in range(self.lookback, len(prices) - 5):
            features = self.create_features(prices[:i])
            label = self.create_labels(prices[:i])[0]
            X.append(features)
            y.append(label)
        
        if len(X) > 10:
            X = np.array(X)
            y = np.array(y)
            
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled, y)
            self.is_trained = True
    
    def on_bar(self, bar):
        self.train_count += 1
        
        # 定期重新训练
        if self.train_count % self.retrain_freq == 0:
            prices = self.get_closes(self.lookback * 2)
            if len(prices) > self.lookback:
                self.train_model(prices)
        
        if not self.is_trained:
            return
        
        # 获取当前特征
        prices = self.get_closes(self.lookback)
        if len(prices) < self.lookback:
            return
        
        features = self.create_features(prices)
        features_scaled = self.scaler.transform([features])
        
        # 预测
        prob = self.model.predict_proba(features_scaled)[0][1]
        
        # 生成信号
        if prob > 0.6:
            self.emit_signal(Signal(
                type=SignalType.BUY,
                strength=prob,
                reason=f"ML 预测上涨 (概率{prob:.2%})"
            ))
        elif prob < 0.4:
            self.emit_signal(Signal(
                type=SignalType.SELL,
                strength=1 - prob,
                reason=f"ML 预测下跌 (概率{1-prob:.2%})"
            ))
```

## ⚙️ 参数配置

```yaml
strategy:
  name: MLStrategy
  params:
    lookback: 60          # 回看周期
    n_estimators: 100     # 树的数量
    max_depth: 5          # 树的最大深度
    retrain_freq: 20      # 重新训练频率
    prediction_horizon: 5 # 预测周期
```

### 特征工程

| 特征类型 | 具体特征 | 说明 |
|---------|---------|------|
| 收益率 | 1 日/3 日/5 日/10 日收益 | 短期动量 |
| 波动率 | 10 日波动率 | 风险指标 |
| 均线 | 5/10/20 日偏离度 | 趋势指标 |
| 成交量 | 成交量变化率 | 资金流向 |
| 技术指标 | RSI/MACD/KDJ | 经典指标 |

## 📈 回测示例

```python
from openfinagent import Backtester, MLStrategy

# 创建策略
strategy = MLStrategy(
    lookback=60,
    n_estimators=100,
    retrain_freq=20
)

# 配置回测
backtester = Backtester(
    strategy=strategy,
    data_file='data/stock_data.csv',
    initial_capital=100000,
    commission=0.001
)

# 运行回测
results = backtester.run()

# 输出结果
print(f"总收益率：{results.total_return:.2%}")
print(f"夏普比率：{results.sharpe_ratio:.2f}")
print(f"最大回撤：{results.max_drawdown:.2%}")
print(f"预测准确率：{results.accuracy:.2%}")
```

## 🎯 优缺点分析

### 优点

- ✅ 自动学习市场规律
- ✅ 可处理大量特征
- ✅ 适应性强，可更新
- ✅ 减少人为干预

### 缺点

- ❌ 需要大量数据
- ❌ 存在过拟合风险
- ❌ 模型解释性差
- ❌ 计算资源需求高

## 🔧 优化方向

### 1. 特征选择

```python
from sklearn.feature_selection import SelectKBest, f_classif

# 选择最重要的 K 个特征
selector = SelectKBest(f_classif, k=10)
X_selected = selector.fit_transform(X, y)
```

### 2. 模型集成

```python
from sklearn.ensemble import VotingClassifier

# 多模型投票
model1 = RandomForestClassifier()
model2 = XGBClassifier()
model3 = SVC(probability=True)

ensemble = VotingClassifier(
    estimators=[('rf', model1), ('xgb', model2), ('svc', model3)],
    voting='soft'
)
```

### 3. 超参数优化

```python
from sklearn.model_selection import GridSearchCV

# 网格搜索最优参数
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [3, 5, 7, 10]
}

grid_search = GridSearchCV(
    RandomForestClassifier(),
    param_grid,
    cv=5
)
grid_search.fit(X, y)
```

## 📊 适用场景

| 场景 | 适用性 | 说明 |
|------|--------|------|
| 股票市场 | ⭐⭐⭐⭐ | 数据充足 |
| 期货市场 | ⭐⭐⭐⭐ | 规律性强 |
| 加密货币 | ⭐⭐⭐ | 波动大 |
| 外汇市场 | ⭐⭐⭐ | 需要更多特征 |

## ⚠️ 风险提示

1. **过拟合**: 模型过度拟合历史数据
2. **数据泄露**: 未来信息泄露到训练集
3. **市场变化**: 历史规律可能失效
4. **黑箱风险**: 模型决策不透明

## 📚 相关资源

- [策略文档索引](index.md)
- [特征工程教程](../tutorials/)
- [模型评估](../api/evaluation.md)

---

_机器学习策略代表了量化交易的未来方向。_
