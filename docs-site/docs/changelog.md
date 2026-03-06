# 更新日志 (Changelog)

> 记录 OpenFinAgent 的所有重要更新

---

## [v0.3.0] - 2026-03-06

### 🎉 新增功能

#### 数据源扩展

- **Binance 数据源** (`data.binance_source`)
  - 支持 BTC/USDT、ETH/USDT 等加密货币
  - 14 种时间周期（1m ~ 1M）
  - 无需 API Key，使用公开接口
  - 自动分页和限流控制
  - 📖 [使用指南](guides/binance-data.md)

- **Tushare 分钟线** (`data.sources.TushareDataSource`)
  - 支持 1m/5m/15m/30m/60m 分钟线
  - A 股全市场覆盖（股票、指数、基金）
  - 复权处理（前复权、后复权、不复权）
  - Token 管理器（加密存储）
  - 数据缓存机制
  - 📖 [使用指南](guides/tushare-data.md)

#### 策略优化器

- **遗传算法优化器** (`optimization.genetic_optimizer`)
  - 基于生物进化原理的智能搜索
  - 支持选择、交叉、变异操作
  - 精英保留策略
  - 并行计算加速
  - 灵活的优化目标配置
  - 📖 [使用指南](guides/optimizer.md)

- **参数热力图** (`visualization.heatmap`)
  - 双参数扫描和可视化
  - 热力图、等高线图、交互式图表
  - 最优参数自动标记
  - 参数敏感性分析
  - 📖 [使用指南](guides/optimizer.md)

#### 性能优化

- **优化回测引擎** (`backtest.optimized_engine`)
  - NumPy 向量化计算
  - 缓存机制避免重复计算
  - 内存占用优化
  - 并行回测支持
  - ⚡ 速度提升 50%+

### 📊 质量提升

#### 测试覆盖率

| 模块 | v0.2.0 | v0.3.0 | 提升 |
|------|--------|--------|------|
| 策略模块 | 45% | 75% | +30% |
| 回测引擎 | 40% | 70% | +30% |
| 数据源 | 30% | 60% | +30% |
| **总体** | **40%** | **65%** | **+25%** |

#### 代码质量

- ✅ 完整类型注解（所有核心模块）
- ✅ 完善错误处理（参数验证和异常捕获）
- ✅ 全面日志记录（调试和监控）
- ✅ 详细文档字符串（所有 API）

### 📦 新增文件

```
src/
├── data/
│   ├── binance_source.py          # Binance 数据源
│   └── tushare_token_manager.py   # Tushare Token 管理器
├── optimization/
│   └── genetic_optimizer.py       # 遗传算法优化器
└── visualization/
    └── heatmap.py                 # 参数热力图

docs-site/docs/
└── guides/
    ├── binance-data.md            # Binance 使用指南
    ├── tushare-data.md            # Tushare 使用指南
    └── optimizer.md               # 优化器使用指南
```

### 🔧 改进内容

- 优化请求频率控制，避免触发 API 限流
- 改进错误提示，更清晰的诊断信息
- 增强数据验证，确保数据质量
- 优化内存管理，降低峰值占用

### 🐛 Bug 修复

- 修复 Tushare 数据源在特定日期范围返回空数据的问题
- 修复遗传算法优化器在边界参数处的异常
- 修复热力图可视化在中文字体下的显示问题
- 修复批量回测在并行模式下的资源竞争问题

### ⚠️ 注意事项

1. **Tushare Token**: 使用分钟线需要 2000 积分
   - 注册地址：https://tushare.pro
   - 设置环境变量：`export TUSHARE_TOKEN=your_token`

2. **网络要求**: Binance 数据源需要访问国际互联网

3. **性能建议**: 大数据集建议使用优化引擎 + 缓存
   ```python
   from backtest.optimized_engine import OptimizedBacktestEngine
   engine = OptimizedBacktestEngine(use_cache=True)
   ```

4. **过拟合风险**: 参数优化时注意留出验证集

---

## [v0.2.0] - 2026-02-15

### 🎉 新增功能

#### 策略模板

- **RSI 策略** (`strategy.rsi_strategy`)
  - 基于相对强弱指数的超买超卖策略
  - 可配置超买超卖阈值
  - 适合震荡市场

- **MACD 策略** (`strategy.macd_strategy`)
  - 基于 MACD 指标的金叉死叉策略
  - 支持 Histogram 确认
  - 适合趋势市场

- **布林带策略** (`strategy.bollinger_strategy`)
  - 支持均值回归和趋势突破两种模式
  - 自动计算带宽指标
  - 适应不同市场环境

- **双均线 + 成交量策略** (`strategy.dual_ma_volume_strategy`)
  - 结合均线交叉和成交量确认
  - 减少假突破
  - 提高信号可靠性

#### 风险控制

- **风险控制器** (`risk.control.RiskController`)
  - 仓位控制（单笔最大仓位、总仓位上限）
  - 止损止盈（固定止损、移动止损）
  - 最大回撤控制
  - 交易频率限制
  - 风险预算管理

#### 批量回测

- **批量回测器** (`backtest.batch.BatchBacktester`)
  - 多股票批量回测
  - 并行处理加速
  - 结果汇总和导出

- **多策略对比** (`backtest.batch.MultiStrategyBacktester`)
  - 多策略同时回测
  - 性能对比分析
  - 对比图表生成

#### 多数据源

- **AkShare 数据源** - A 股免费数据
- **Yahoo Finance 数据源** - 美股/港股数据
- **CSV 数据源** - 本地 CSV 文件
- **Mock 数据源** - 模拟数据

### 📊 质量提升

- 添加完整类型注解
- 完善错误处理和参数验证
- 全面日志记录
- 测试覆盖率提升至 40%

### 🐛 Bug 修复

- 修复回测结果计算错误
- 修复数据源时区问题
- 修复策略信号生成延迟

---

## [v0.1.0] - 2026-01-10

### 🎉 初始版本

#### 核心功能

- 基础回测引擎
- 双均线策略模板
- 动量策略模板
- 均值回归策略模板
- 网格交易策略模板
- 基础数据源（CSV、Mock）

#### 文档

- 快速开始指南
- 策略文档
- API 参考
- 教程示例

---

## 📝 版本说明

### 版本号规则

采用语义化版本号：`MAJOR.MINOR.PATCH`

- **MAJOR** - 不兼容的 API 变更
- **MINOR** - 向后兼容的功能新增
- **PATCH** - 向后兼容的问题修复

### 发布周期

- **大版本** - 每 6 个月（重大功能更新）
- **小版本** - 每 1-2 个月（功能增强）
- **补丁版本** - 按需发布（Bug 修复）

### 升级建议

- **v0.1 → v0.2**: 直接升级，API 兼容
- **v0.2 → v0.3**: 直接升级，API 兼容
- **v0.3 → v1.0**: 检查 API 变更（未来）

---

## 🔗 相关链接

- [GitHub Releases](https://github.com/bobipika2026/openfinagent/releases)
- [项目文档](https://bobipika2026.github.io/openfinagent)
- [问题反馈](https://github.com/bobipika2026/openfinagent/issues)

---

_最后更新：2026 年 3 月 6 日_
