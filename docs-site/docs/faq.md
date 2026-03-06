# 常见问题 (FAQ)

## 📦 安装问题

### Q: 安装时遇到依赖冲突怎么办？

```bash
# 清除 pip 缓存
pip cache purge

# 升级 pip
pip install --upgrade pip

# 使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 重新安装
pip install -r requirements.txt
```

### Q: 如何在国内加速安装？

```bash
# 使用清华镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用阿里云镜像
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### Q: TensorFlow/PyTorch 安装失败？

```bash
# 使用预编译版本
pip install tensorflow==2.13.0

# 或使用 conda
conda install tensorflow
conda install pytorch torchvision -c pytorch
```

## 🔧 配置问题

### Q: 如何配置 API 密钥？

```bash
# 复制配置文件
cp .env.example .env

# 编辑配置
vim .env

# 填入你的密钥
ALPACA_API_KEY=your_key_here
ALPACA_API_SECRET=your_secret_here
```

### Q: 配置文件在哪里？

默认位置：
- Linux/macOS: `~/.openfinagent/.env`
- Windows: `C:\Users\YourName\.openfinagent\.env`
- 项目目录：`./openfinagent/.env`

### Q: 如何切换模拟/实盘模式？

```ini
# .env 文件
PAPER_TRADING=true   # 模拟交易
PAPER_TRADING=false  # 实盘交易
```

## 📊 数据问题

### Q: 数据从哪里获取？

支持的数据源：
- **美股**: Alpaca, Yahoo Finance, Alpha Vantage
- **A 股**: Tushare, Baostock, AKShare
- **加密货币**: Binance, CoinGecko
- **期货**: 各期货公司 API

### Q: 历史数据如何下载？

```bash
# 使用内置脚本
python scripts/download_data.py --symbol AAPL --start 2023-01-01 --end 2023-12-31

# 或使用 Python API
from openfinagent import DataDownloader

downloader = DataDownloader(source='alpaca')
data = downloader.download('AAPL', start='2023-01-01', end='2023-12-31')
```

### Q: 数据格式是什么？

```csv
timestamp,open,high,low,close,volume
2023-01-01 10:00:00,100.0,102.0,99.0,101.0,1000000
2023-01-01 10:01:00,101.0,103.0,100.5,102.5,800000
```

## 📈 回测问题

### Q: 回测结果和实盘差异大？

可能原因：
1. **滑点和手续费**: 回测中设置过低
2. **流动性假设**: 回测假设无限流动性
3. **未来函数**: 策略使用了未来数据
4. **幸存者偏差**: 只测试了现存股票

解决方案：
```python
backtester = Backtester(
    strategy=strategy,
    commission=0.001,    # 提高手续费
    slippage=0.002,      # 提高滑点
    max_position=0.1     # 限制仓位
)
```

### Q: 如何加速回测？

```python
# 使用多进程
backtester = Backtester(..., n_jobs=4)

# 减少数据量
backtester = Backtester(..., start_date='2023-01-01')

# 禁用可视化
results = backtester.run(plot=False)
```

### Q: 回测报错"数据不足"？

```python
# 检查数据长度
print(len(data))

# 确保数据足够
# 如果策略需要 60 日数据，至少准备 100 日
data = load_data(min_rows=100)
```

## 💼 交易问题

### Q: 订单无法成交？

可能原因：
1. **价格不合理**: 限价单价格偏离市场价太多
2. **数量过大**: 超过市场流动性
3. **账户限制**: 资金不足或仓位超限
4. **市场关闭**: 非交易时间

解决方案：
```python
# 使用市价单
order = Order(type=OrderType.MARKET)

# 减少数量
order = Order(quantity=100)  # 而不是 10000

# 检查账户状态
print(account.cash)
print(account.buying_power)
```

### Q: 如何设置止盈止损？

```python
# 开仓时设置
self.buy(symbol='AAPL', quantity=100)
self.set_stop_loss('AAPL', stop_price=140.0)
self.set_take_profit('AAPL', take_price=170.0)

# 或追踪止损
self.set_trailing_stop('AAPL', trail_percent=0.05)
```

### Q: 如何处理跳空缺口？

```python
# 在 on_bar 中检查
def on_bar(self, bar):
    prev_close = self.get_prev_close()
    gap = (bar.open - prev_close) / prev_close
    
    if abs(gap) > 0.05:  # 跳空超过 5%
        # 特殊处理
        self.handle_gap(gap)
```

## 🐛 错误处理

### Q: 策略运行中报错？

```python
# 添加异常处理
def on_bar(self, bar):
    try:
        # 策略逻辑
        pass
    except Exception as e:
        self.logger.error(f"Error: {e}")
        # 可选择平仓或跳过
        # self.close_all()
```

### Q: 连接断开怎么办？

```python
# 添加重连逻辑
from openfinagent import ConnectionManager

manager = ConnectionManager(
    max_retries=5,
    retry_delay=10
)

@manager.auto_reconnect
def run_strategy():
    bot.run()
```

### Q: 内存占用过高？

```python
# 减少数据缓存
config = Config(cache_size=1000)

# 定期清理
import gc
gc.collect()

# 分批处理数据
for chunk in data_chunks:
    process(chunk)
```

## 📚 学习资源

### Q: 如何学习量化交易？

推荐学习路径：
1. **基础**: Python 编程、统计学基础
2. **入门**: 完成本教程所有示例
3. **进阶**: 学习机器学习策略
4. **实战**: 模拟交易 → 小资金实盘

### Q: 有社区可以交流吗？

- **GitHub Issues**: [提交问题](https://github.com/bobipika2026/openfinagent/issues)
- **GitHub Discussions**: [参与讨论](https://github.com/bobipika2026/openfinagent/discussions)
- **文档**: [完整文档](https://bobipika2026.github.io/openfinagent)

### Q: 如何贡献代码？

```bash
# Fork 项目
git fork https://github.com/bobipika2026/openfinagent

# 创建分支
git checkout -b feature/your-feature

# 提交 PR
git push origin feature/your-feature
```

## 🔒 安全问题

### Q: API 密钥安全吗？

**重要提示**:
- ✅ 不要在代码中硬编码密钥
- ✅ 使用 .env 文件管理密钥
- ✅ 将 .env 加入 .gitignore
- ✅ 定期更换密钥
- ❌ 不要分享密钥
- ❌ 不要上传到 GitHub

### Q: 如何备份策略和数据？

```bash
# 备份策略
cp -r strategies/ backup/strategies_$(date +%Y%m%d)

# 备份数据
cp -r data/ backup/data_$(date +%Y%m%d)

# 备份配置
cp .env backup/env_$(date +%Y%m%d)
```

---

_没有找到答案？[提交 Issue](https://github.com/bobipika2026/openfinagent/issues/new)_
