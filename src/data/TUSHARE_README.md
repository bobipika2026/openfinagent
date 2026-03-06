# Tushare 数据源模块

增强版 Tushare 数据源，支持完整的 Tushare Pro API 功能。

## 功能特性

### 1. 数据获取
- ✅ 日线数据 (`get_daily_data`)
- ✅ 分钟线数据 (`get_min_data`) - 支持 1/5/15/30/60 分钟
- ✅ 实时行情 (`get_realtime_quote`)
- ✅ 股票基本信息 (`get_stock_basic`)
- ✅ 财务数据 (利润表、资产负债表、现金流量表、财务指标)
- ✅ 指数数据 (指数日线、指数基本信息、指数成分股)
- ✅ 交易日历 (`get_trade_cal`)
- ✅ 股票列表 (`get_stock_list`)

### 2. Token 管理
- ✅ 环境变量支持 (`TUSHARE_TOKEN`)
- ✅ 配置文件支持 (`~/.tradeflow/tushare_config.json`)
- ✅ Token 池 (多 Token 轮询)
- ✅ 三种轮询策略：
  - `priority`: 优先级优先
  - `round_robin`: 轮询
  - `least_used`: 最少使用优先
- ✅ Token 健康检查
- ✅ 自动错误计数和降级

### 3. 缓存机制
- ✅ 内存缓存 (LRU 淘汰)
- ✅ 磁盘缓存 (可选)
- ✅ 可配置的 TTL (默认 1 小时)
- ✅ 自动过期清理
- ✅ 缓存统计信息

### 4. 错误处理
- ✅ API 限流处理
- ✅ 自动重试 (最多 3 次)
- ✅ 指数退避延迟
- ✅ Token 自动切换
- ✅ 详细的错误日志

## 快速开始

### 安装依赖

```bash
pip install tushare pandas numpy
```

### 基本使用

```python
from data.tushare_source import TushareDataSource

# 初始化数据源
source = TushareDataSource(token='your_tushare_token')

# 获取日线数据
df = source.get_daily_data(
    ts_code='000001.SZ',
    start_date='2024-01-01',
    end_date='2024-01-31'
)

# 获取分钟线数据
df_min = source.get_min_data(
    ts_code='000001.SZ',
    freq='5min',
    start_date='2024-01-31'
)

# 获取实时行情
quote = source.get_realtime_quote('000001.SZ')
print(f"当前价格：{quote.get('price')}")
```

### 使用环境变量

```bash
export TUSHARE_TOKEN='your_token_here'
```

```python
# 自动从环境变量读取 Token
source = TushareDataSource()
```

### 多 Token 轮询

```python
from data.tushare_token_manager import TushareTokenManager, TokenInfo

# 创建 Token 管理器
tokens = [
    TokenInfo(token='token1', name='primary', priority=10),
    TokenInfo(token='token2', name='backup', priority=5),
]

manager = TushareTokenManager(
    tokens=tokens,
    rotation_strategy='priority'  # 或 'round_robin', 'least_used'
)

# 使用 Token 管理器初始化数据源
source = TushareDataSource(token_manager=manager)
```

### 配置缓存

```python
from data.tushare_cache import TushareCache

# 创建缓存
cache = TushareCache(
    max_size=1000,          # 最大缓存条目数
    ttl_seconds=3600,       # 默认过期时间 (秒)
    disk_cache=True,        # 启用磁盘缓存
    auto_cleanup=True       # 自动清理过期缓存
)

# 使用自定义缓存
source = TushareDataSource(cache=cache, use_cache=True)
```

## API 参考

### TushareDataSource

#### 初始化参数
- `token`: Tushare Token (可选)
- `token_manager`: Token 管理器实例 (可选)
- `cache`: 缓存实例 (可选)
- `use_cache`: 是否使用缓存 (默认 True)
- `rate_limit_delay`: 请求间隔秒数 (默认 0.1)
- `max_retries`: 最大重试次数 (默认 3)

#### 主要方法

**日线数据**
```python
get_daily_data(
    ts_code: str,
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    use_cache: bool = True
) -> pd.DataFrame
```

**分钟线数据**
```python
get_min_data(
    ts_code: str,
    freq: str = '5min',  # '1min', '5min', '15min', '30min', '60min'
    start_date: Optional[Union[str, datetime]] = None,
    end_date: Optional[Union[str, datetime]] = None,
    use_cache: bool = True
) -> pd.DataFrame
```

**实时行情**
```python
get_realtime_quote(
    ts_code: str,
    use_cache: bool = False
) -> Dict[str, Any]
```

**股票基本信息**
```python
get_stock_basic(
    ts_code: Optional[str] = None,
    exchange: Optional[str] = None,
    use_cache: bool = True
) -> pd.DataFrame
```

**财务数据**
```python
get_income(ts_code, start_date, end_date) -> pd.DataFrame      # 利润表
get_balance(ts_code, start_date, end_date) -> pd.DataFrame     # 资产负债表
get_cashflow(ts_code, start_date, end_date) -> pd.DataFrame    # 现金流量表
get_fina_indicator(ts_code, start_date, end_date) -> pd.DataFrame  # 财务指标
```

**指数数据**
```python
get_index_daily(ts_code, start_date, end_date) -> pd.DataFrame  # 指数日线
get_index_basic(ts_code) -> pd.DataFrame                        # 指数基本信息
get_index_member(ts_code) -> pd.DataFrame                       # 指数成分股
```

### TushareTokenManager

#### 主要方法
- `add_token(token, name, priority)`: 添加 Token
- `remove_token(token)`: 移除 Token
- `get_token()`: 获取一个可用 Token
- `record_error(token)`: 记录 Token 错误
- `reset_token_errors(token)`: 重置 Token 错误
- `list_tokens()`: 列出所有 Token
- `get_stats()`: 获取统计信息
- `health_check()`: 健康检查

### TushareCache

#### 主要方法
- `set(api_name, params, data, ttl_seconds)`: 存储缓存
- `get(api_name, params)`: 获取缓存
- `delete(api_name, params)`: 删除缓存
- `clear()`: 清空缓存
- `cleanup()`: 清理过期缓存
- `get_stats()`: 获取统计信息

## 便捷函数

```python
from data.tushare_source import get_daily, get_min, get_quote

# 获取日线
df = get_daily('000001.SZ', '2024-01-01', '2024-01-31')

# 获取分钟线
df = get_min('000001.SZ', freq='5min')

# 获取实时行情
quote = get_quote('000001.SZ')
```

## 配置示例

### 环境变量配置

```bash
# 单个 Token
export TUSHARE_TOKEN='your_token'
export TUSHARE_TOKEN_NAME='main'

# 多个 Token
export TUSHARE_TOKEN_0='token1'
export TUSHARE_TOKEN_0_NAME='primary'
export TUSHARE_TOKEN_0_PRIORITY='10'

export TUSHARE_TOKEN_1='token2'
export TUSHARE_TOKEN_1_NAME='backup'
export TUSHARE_TOKEN_1_PRIORITY='5'
```

### 配置文件

位置：`~/.tradeflow/tushare_config.json`

```json
{
  "tokens": [
    {
      "token": "your_token",
      "name": "primary",
      "priority": 10,
      "api_count": 0,
      "is_active": true,
      "error_count": 0
    }
  ],
  "rotation_strategy": "priority"
}
```

## 错误处理

```python
from data.tushare_source import TushareDataSource, TushareAPIError, TushareRateLimitError

source = TushareDataSource(token='your_token')

try:
    df = source.get_daily_data('000001.SZ', '2024-01-01', '2024-01-31')
except TushareRateLimitError:
    print("触发限流，请稍后重试")
except TushareAPIError as e:
    print(f"API 错误：{e}")
except Exception as e:
    print(f"其他错误：{e}")
```

## 运行测试

```bash
cd /root/.openclaw/workspace/projects/tradeflow-ai
python3 -m pytest tests/test_tushare.py -v
```

## 注意事项

1. **Token 获取**: 需要在 [Tushare 官网](https://tushare.pro) 注册并获取 Token
2. **积分限制**: 部分高级数据需要足够的积分才能访问
3. **限流策略**: 默认每分钟最多请求 10 次，可根据需要调整 `rate_limit_delay`
4. **缓存使用**: 实时行情默认不使用缓存，历史数据默认使用缓存
5. **股票代码格式**: 使用 `000001.SZ` 或 `600000.SH` 格式

## 更新日志

### v2.0.0
- ✨ 新增 Token 池管理
- ✨ 新增本地缓存 (内存 + 磁盘)
- ✨ 新增错误处理和重试机制
- ✨ 新增财务数据接口
- ✨ 新增指数数据接口
- 🐛 修复分钟线数据处理
- 🐛 优化日期格式化逻辑

### v1.0.0
- 初始版本
- 支持日线、分钟线数据
- 基础错误处理

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
