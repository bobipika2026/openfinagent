# 教程 3: 使用真实数据进行回测

在本教程中，你将学习如何使用真实市场数据进行策略回测。

---

## 📖 教程目录

- [学习目标](#学习目标)
- [数据源介绍](#数据源介绍)
- [准备工作](#准备工作)
- [示例 1: A 股数据回测](#示例 1-a 股数据回测)
- [示例 2: 美股数据回测](#示例 2-美股数据回测)
- [示例 3: 多股票对比回测](#示例 3-多股票对比回测)
- [数据质量检查](#数据质量检查)
- [回测结果分析](#回测结果分析)
- [常见问题](#常见问题)
- [下一步](#下一步)

---

## 🎯 学习目标

完成本教程后，你将能够：

- ✅ 了解 TradeFlow AI 支持的数据源
- ✅ 使用 AKShare 获取 A 股数据
- ✅ 使用 yfinance 获取美股数据
- ✅ 进行多股票对比回测
- ✅ 检查和处理数据质量问题

---

## 数据源介绍

TradeFlow AI 支持多种数据源：

| 数据源 | 市场 | 免费 | 需要 API | 说明 |
|--------|------|------|---------|------|
| `mock` | 全部 | ✅ | ❌ | 模拟数据，适合学习 |
| `akshare` | A 股 | ✅ | ❌ | 开源财经数据接口 |
| `yfinance` | 美股/港股 | ✅ | ❌ | Yahoo Finance |
| `binance` | 加密货币 | ✅ | ❌ | 币安交易所 |
| `tushare` | A 股 | ⚠️ | ✅ | 需要积分（更稳定） |

---

## 准备工作

### 安装数据源依赖

```bash
# A 股数据（AKShare）
pip install akshare

# 美股数据（Yahoo Finance）
pip install yfinance

# 加密货币数据
pip install ccxt
```

### 验证安装

```bash
# 测试 AKShare
python -c "import akshare as ak; print('AKShare OK')"

# 测试 yfinance
python -c "import yfinance as yf; print('yfinance OK')"
```

---

## 示例 1: A 股数据回测

### 使用 AKShare 获取 A 股数据

创建文件 `backtest_a_stock.py`：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用真实 A 股数据进行回测
"""

from tradeflow import StrategyBuilder, BacktestEngine
from tradeflow.backtest.engine import load_data


def main():
    print("=" * 70)
    print("🚀 A 股真实数据回测 - 贵州茅台 (600519.SH)")
    print("=" * 70)
    
    # ========== 步骤 1: 创建策略 ==========
    print("\n📝 步骤 1: 创建策略")
    print("-" * 70)
    
    strategy = StrategyBuilder.from_natural_language("""
    当 10 日均线上穿 30 日均线时买入
    当 10 日均线下穿 30 日均线时卖出
    初始资金 50 万元
    手续费 万分之三
    """)
    
    print(f"✅ 策略：{strategy.name}")
    print(f"   短期均线：{strategy.short_window}日")
    print(f"   长期均线：{strategy.long_window}日")
    print(f"   初始资金：¥{strategy.initial_capital:,.0f}")
    
    # ========== 步骤 2: 加载真实数据 ==========
    print("\n📊 步骤 2: 加载 A 股数据 (AKShare)")
    print("-" * 70)
    
    try:
        data = load_data(
            symbol="600519.SH",
            start_date="2022-01-01",
            end_date="2023-12-31",
            source='akshare'  # 使用 AKShare 获取真实数据
        )
        
        print(f"✅ 数据加载成功！")
        print(f"   时间范围：{data.index[0].date()} 至 {data.index[-1].date()}")
        print(f"   数据条数：{len(data)}")
        print(f"   价格区间：¥{data['close'].min():.2f} - ¥{data['close'].max():.2f}")
        print(f"   最新收盘价：¥{data['close'].iloc[-1]:.2f}")
        
    except Exception as e:
        print(f"❌ 数据加载失败：{e}")
        print("\n💡 提示:")
        print("   1. 确保已安装 akshare: pip install akshare")
        print("   2. 检查网络连接")
        print("   3. 使用模拟数据：source='mock'")
        return
    
    # ========== 步骤 3: 运行回测 ==========
    print("\n🔄 步骤 3: 运行回测")
    print("-" * 70)
    
    engine = BacktestEngine(
        commission_rate=0.0003,  # A 股手续费约万分之三
        slippage=0.001           # 滑点 0.1%
    )
    
    results = engine.run(strategy, data, show_progress=True)
    print(f"✅ 回测完成！")
    
    # ========== 步骤 4: 显示结果 ==========
    print("\n📈 步骤 4: 回测结果")
    print("-" * 70)
    
    results.show()
    
    # ========== 步骤 5: 生成图表 ==========
    print("\n🎨 步骤 5: 生成图表")
    print("-" * 70)
    
    try:
        results.plot(save_path='a_stock_backtest.png')
        print(f"✅ 图表已保存：a_stock_backtest.png")
    except Exception as e:
        print(f"⚠️  绘图失败：{e}")
    
    # ========== 步骤 6: 保存结果 ==========
    print("\n💾 步骤 6: 保存结果")
    print("-" * 70)
    
    results.to_csv('a_stock_trades.csv')
    print(f"✅ 交易记录已保存：a_stock_trades.csv")
    
    # ========== 步骤 7: 与买入持有对比 ==========
    print("\n📊 步骤 7: 与买入持有策略对比")
    print("-" * 70)
    
    buy_hold_return = (data['close'].iloc[-1] - data['close'].iloc[0]) / data['close'].iloc[0] * 100
    strategy_return = results.metrics['总收益']
    
    print(f"买入持有收益：{buy_hold_return:.2f}%")
    print(f"策略收益：    {strategy_return:.2f}%")
    print(f"超额收益：    {strategy_return - buy_hold_return:.2f}%")
    
    print("\n" + "=" * 70)
    print("✅ A 股回测完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()
```

### 运行回测

```bash
python backtest_a_stock.py
```

### 常见问题处理

**问题 1: AKShare 数据加载失败**

```python
# 备用方案：使用 tushare（需要注册获取 token）
import tushare as ts

pro = ts.pro_api('your_token_here')
df = pro.daily(ts_code='600519.SH', start_date='20220101', end_date='20231231')
```

**问题 2: 股票代码格式错误**

A 股代码格式：
- 上交所：`600519.SH`
- 深交所：`000858.SZ`

---

## 示例 2: 美股数据回测

### 使用 yfinance 获取美股数据

创建文件 `backtest_us_stock.py`：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用真实美股数据进行回测
"""

from tradeflow import StrategyBuilder, BacktestEngine
from tradeflow.backtest.engine import load_data


def main():
    print("=" * 70)
    print("🚀 美股真实数据回测 - 苹果 (AAPL)")
    print("=" * 70)
    
    # ========== 步骤 1: 创建策略 ==========
    strategy = StrategyBuilder.create(
        'momentum',
        lookback=30,
        threshold=0.08,      # 8% 阈值
        initial_capital=100000,
        stop_loss=0.12,      # 12% 止损
        take_profit=0.35,    # 35% 止盈
        name='美股动量策略'
    )
    
    print(f"✅ 策略：{strategy.name}")
    
    # ========== 步骤 2: 加载美股数据 ==========
    print("\n📊 加载美股数据 (Yahoo Finance)")
    print("-" * 70)
    
    try:
        data = load_data(
            symbol="AAPL",
            start_date="2022-01-01",
            end_date="2023-12-31",
            source='yfinance'
        )
        
        print(f"✅ 数据加载成功！")
        print(f"   时间范围：{data.index[0].date()} 至 {data.index[-1].date()}")
        print(f"   数据条数：{len(data)}")
        print(f"   价格区间：${data['close'].min():.2f} - ${data['close'].max():.2f}")
        
    except Exception as e:
        print(f"❌ 数据加载失败：{e}")
        print("\n💡 提示:")
        print("   1. 确保已安装 yfinance: pip install yfinance")
        print("   2. 检查网络连接")
        return
    
    # ========== 步骤 3: 运行回测 ==========
    print("\n🔄 运行回测")
    print("-" * 70)
    
    engine = BacktestEngine(
        commission_rate=0.001,  # 美股手续费（约 0.1%）
        slippage=0.001
    )
    
    results = engine.run(strategy, data, show_progress=True)
    
    # ========== 步骤 4: 显示结果 ==========
    print("\n📈 回测结果")
    print("-" * 70)
    
    results.show()
    
    # ========== 步骤 5: 保存结果 ==========
    results.to_csv('us_stock_trades.csv')
    results.plot(save_path='us_stock_backtest.png')
    
    print("\n✅ 美股回测完成！")


if __name__ == "__main__":
    main()
```

### 运行回测

```bash
python backtest_us_stock.py
```

### 常见美股代码

```python
# 科技股
"AAPL"   # 苹果
"MSFT"   # 微软
"GOOGL"  # 谷歌
"AMZN"   # 亚马逊
"NVDA"   # 英伟达
"TSLA"   # 特斯拉

# 指数 ETF
"QQQ"    # 纳斯达克 100
"SPY"    # 标普 500
"DIA"    # 道琼斯
```

---

## 示例 3: 多股票对比回测

### 批量回测多只股票

创建文件 `backtest_multiple_stocks.py`：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多股票对比回测
"""

from tradeflow import StrategyBuilder, BacktestEngine
from tradeflow.backtest.engine import load_data


def backtest_single_stock(symbol, name, data_source='akshare'):
    """回测单只股票"""
    print(f"\n{'='*70}")
    print(f"📈 回测：{name} ({symbol})")
    print(f"{'='*70}")
    
    # 加载数据
    try:
        data = load_data(
            symbol=symbol,
            start_date="2023-01-01",
            end_date="2023-12-31",
            source=data_source
        )
        print(f"✅ 数据：{len(data)} 条，价格区间：¥{data['close'].min():.0f}-¥{data['close'].max():.0f}")
    except Exception as e:
        print(f"❌ 数据加载失败：{e}")
        return None
    
    # 创建策略
    strategy = StrategyBuilder.create(
        'ma_cross',
        short_window=10,
        long_window=30,
        initial_capital=100000,
        name=f'{name}均线策略'
    )
    
    # 运行回测
    engine = BacktestEngine()
    results = engine.run(strategy, data, show_progress=False)
    
    # 显示关键指标
    metrics = results.metrics
    print(f"📊 结果：年化收益 {metrics['年化收益']:.2f}%, "
          f"夏普比率 {metrics['夏普比率']:.2f}, "
          f"最大回撤 {metrics['最大回撤']:.2f}%")
    
    return {
        'symbol': symbol,
        'name': name,
        'results': results,
        'metrics': metrics
    }


def main():
    print("=" * 70)
    print("🚀 多股票对比回测")
    print("=" * 70)
    
    # 定义股票列表
    stocks = [
        ("600519.SH", "贵州茅台"),
        ("000858.SZ", "五粮液"),
        ("000333.SZ", "美的集团"),
        ("601318.SH", "中国平安"),
        ("600036.SH", "招商银行"),
    ]
    
    # 批量回测
    all_results = []
    for symbol, name in stocks:
        result = backtest_single_stock(symbol, name, data_source='mock')  # 使用 mock 避免网络请求
        if result:
            all_results.append(result)
    
    # 汇总对比
    print(f"\n{'='*70}")
    print("📊 回测结果汇总")
    print(f"{'='*70}")
    
    print(f"\n{'股票':<15} {'年化收益':>12} {'夏普比率':>12} {'最大回撤':>12} {'交易次数':>12}")
    print("-" * 70)
    
    for result in all_results:
        m = result['metrics']
        print(f"{result['name']:<15} {m['年化收益']:>11.2f}% {m['夏普比率']:>12.2f} {m['最大回撤']:>11.2f}% {m['交易次数']:>12}")
    
    # 找出最佳策略
    best = max(all_results, key=lambda x: x['metrics']['夏普比率'])
    print(f"\n🏆 夏普比率最高：{best['name']} ({best['metrics']['夏普比率']:.2f})")
    
    # 保存汇总结果
    import pandas as pd
    summary_data = []
    for result in all_results:
        m = result['metrics']
        summary_data.append({
            '股票': result['name'],
            '代码': result['symbol'],
            '年化收益 (%)': m['年化收益'],
            '夏普比率': m['夏普比率'],
            '最大回撤 (%)': m['最大回撤'],
            '交易次数': m['交易次数'],
            '胜率 (%)': m['胜率']
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv('multi_stock_summary.csv', index=False, encoding='utf-8-sig')
    print(f"\n✅ 汇总结果已保存：multi_stock_summary.csv")
    
    print("\n" + "=" * 70)
    print("✅ 多股票对比回测完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()
```

### 运行回测

```bash
python backtest_multiple_stocks.py
```

---

## 数据质量检查

### 检查数据完整性

```python
def check_data_quality(data, symbol):
    """检查数据质量"""
    print(f"\n📋 数据质量检查 - {symbol}")
    print("-" * 50)
    
    # 1. 检查缺失值
    missing = data.isnull().sum()
    if missing.any():
        print(f"⚠️  缺失值:")
        for col, count in missing.items():
            if count > 0:
                print(f"   {col}: {count}")
    else:
        print("✅ 无缺失值")
    
    # 2. 检查价格合理性
    if (data['close'] <= 0).any():
        print("⚠️  发现非正价格！")
    else:
        print("✅ 价格正常")
    
    # 3. 检查成交量
    if (data['volume'] < 0).any():
        print("⚠️  发现负成交量！")
    else:
        print("✅ 成交量正常")
    
    # 4. 检查涨跌停
    daily_change = data['close'].pct_change()
    if (daily_change > 0.11).any() or (daily_change < -0.11).any():
        print("⚠️  发现异常涨跌幅（>11%）")
    else:
        print("✅ 涨跌幅正常")
    
    # 5. 数据时间范围
    print(f"📅 时间范围：{data.index[0].date()} 至 {data.index[-1].date()}")
    print(f"📊 数据条数：{len(data)}")
```

### 处理缺失数据

```python
def handle_missing_data(data):
    """处理缺失数据"""
    # 前向填充
    data = data.fillna(method='ffill')
    
    # 仍有缺失则后向填充
    data = data.fillna(method='bfill')
    
    return data
```

---

## 回测结果分析

### 深度分析回测结果

```python
def analyze_backtest_results(results):
    """深度分析回测结果"""
    metrics = results.metrics
    
    print("\n📊 深度分析")
    print("=" * 50)
    
    # 1. 收益分析
    print("\n1️⃣ 收益分析:")
    print(f"   总收益：{metrics['总收益']:.2f}%")
    print(f"   年化收益：{metrics['年化收益']:.2f}%")
    
    # 2. 风险分析
    print("\n2️⃣ 风险分析:")
    print(f"   最大回撤：{metrics['最大回撤']:.2f}%")
    print(f"   波动率：{metrics['波动率']:.2f}%")
    
    # 3. 风险调整后收益
    print("\n3️⃣ 风险调整后收益:")
    print(f"   夏普比率：{metrics['夏普比率']:.2f}")
    if metrics['夏普比率'] > 1.5:
        print("   ✅ 优秀")
    elif metrics['夏普比率'] > 1.0:
        print("   ✅ 良好")
    elif metrics['夏普比率'] > 0.5:
        print("   ⚠️  一般")
    else:
        print("   ❌ 较差")
    
    # 4. 交易分析
    print("\n4️⃣ 交易分析:")
    print(f"   交易次数：{metrics['交易次数']}")
    print(f"   胜率：{metrics['胜率']:.2f}%")
    
    # 5. 综合评分
    print("\n5️⃣ 综合评分:")
    score = (
        min(metrics['年化收益'], 30) / 30 * 30 +  # 收益分（上限 30%）
        min(metrics['夏普比率'], 2) / 2 * 30 +    # 夏普分（上限 2）
        (100 - min(abs(metrics['最大回撤']), 30)) / 100 * 20 +  # 回撤分
        min(metrics['胜率'], 70) / 70 * 20        # 胜率分（上限 70%）
    )
    print(f"   综合得分：{score:.1f}/100")
    
    if score >= 80:
        print("   ✅ 优秀策略")
    elif score >= 60:
        print("   ✅ 良好策略")
    elif score >= 40:
        print("   ⚠️  一般策略")
    else:
        print("   ❌ 需要优化")
```

---

## ❓ 常见问题

### Q1: AKShare 数据加载慢怎么办？

**A**: 
- AKShare 依赖网站响应，可能较慢
- 可以缓存数据到本地：

```python
import pickle

# 第一次加载并缓存
data = load_data("600519.SH", "2023-01-01", "2023-12-31", source='akshare')
with open('data_cache.pkl', 'wb') as f:
    pickle.dump(data, f)

# 后续使用缓存
with open('data_cache.pkl', 'rb') as f:
    data = pickle.load(f)
```

### Q2: yfinance 数据不准确怎么办？

**A**: 
- yfinance 数据可能有延迟或错误
- 可以对比多个数据源
- 考虑使用付费数据服务（如 Wind、Bloomberg）

### Q3: 回测结果很好，实盘很差？

**A**: 可能原因：
1. **过拟合**: 参数过度优化
2. **幸存者偏差**: 只回测了成功的股票
3. **交易成本**: 实盘有冲击成本
4. **流动性**: 实盘可能无法按回测价格成交

**建议**:
- 使用更长的回测周期（5-10 年）
- 多股票测试，避免单一股票过拟合
- 增加交易成本和滑点
- 进行样本外测试

### Q4: 如何获取复权价格？

**A**: 

```python
# AKShare 获取后复权数据
import akshare as ak

df = ak.stock_zh_a_hist(symbol="600519", period="daily", 
                        start_date="20230101", end_date="20231231",
                        adjust="hfq")  # hfq=后复权，qfq=前复权，空=不复权
```

---

## 📝 练习任务

### 任务 1: 回测沪深 300 成分股

选择 5 只沪深 300 成分股，使用相同策略回测，对比结果。

### 任务 2: 跨市场对比

对比 A 股、美股、港股同一策略的表现。

### 任务 3: 长周期回测

使用 5-10 年数据进行回测，验证策略的长期有效性。

### 任务 4: 参数敏感性分析

测试不同均线组合（5/20、10/30、20/60）在真实数据上的表现。

---

## 💡 最佳实践

1. **数据质量优先**: 始终检查数据完整性
2. **多周期验证**: 在牛、熊、震荡市都测试
3. **样本外测试**: 保留部分数据用于验证
4. **考虑成本**: 设置合理的手续费和滑点
5. **风险管理**: 关注最大回撤，不仅是收益

---

## 🎓 下一步

- 📚 [策略语法参考](../strategy-syntax.md)
- 🔧 [API 参考](../api_reference.md)
- 💬 [用户案例](../showcase.md)
- ❓ [常见问题](../faq.md)

---

**用真实数据验证你的策略！** 🚀
