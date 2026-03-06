# OpenFinAgent 数据库设计

**版本**: v1.0  
**最后更新**: 2026-03-06

---

## 1. 存储架构概述

### 1.1 当前阶段 (v0.1-v0.3)

**设计原则**: 轻量级、零依赖、开箱即用

| 数据类型 | 存储方案 | 格式 | 说明 |
|----------|----------|------|------|
| **K 线数据** | 本地文件缓存 | Parquet | 列式存储、压缩率高 |
| **策略配置** | 本地文件 | YAML/JSON | 易读易编辑 |
| **回测结果** | 本地文件 | JSON + CSV | 便于分享和导出 |
| **用户配置** | 本地文件 | YAML | ~/.openfinagent/config.yaml |
| **日志** | 本地文件 | JSON Lines | ~/.openfinagent/logs/ |

### 1.2 未来规划 (v0.5+)

**设计原则**: 高性能、可扩展、支持多用户

| 数据类型 | 数据库 | 选型理由 |
|----------|--------|----------|
| **K 线数据** | TimescaleDB | 时序优化、自动分区、压缩 |
| **用户数据** | PostgreSQL | ACID、复杂查询、JSONB |
| **缓存** | Redis | 热点数据、微秒级响应 |
| **文件存储** | MinIO / S3 | 策略文件、回测报告 |
| **搜索引擎** | Elasticsearch | 策略搜索、日志分析 |

---

## 2. 文件存储设计

### 2.1 目录结构

```
~/.openfinagent/
├── config.yaml              # 用户配置
├── cache/                   # 数据缓存
│   ├── akshare/
│   │   ├── 600519.SH/
│   │   │   ├── 1d.parquet
│   │   │   └── 1h.parquet
│   │   └── 000001.SZ/
│   │       └── 1d.parquet
│   └── yfinance/
│       └── AAPL/
│           └── 1d.parquet
├── strategies/              # 用户策略
│   ├── my_strategy.py
│   └── my_strategy.yaml
├── results/                 # 回测结果
│   ├── 2026-03-06/
│   │   ├── backtest_001/
│   │   │   ├── result.json
│   │   │   ├── trades.csv
│   │   │   └── equity_curve.csv
│   │   └── backtest_002/
│   └── ...
└── logs/                    # 日志
    ├── tradeflow.log
    └── backtest.log
```

### 2.2 数据缓存格式

```python
# Parquet 文件结构
# 文件：~/.openfinagent/cache/akshare/600519.SH/1d.parquet

# Schema:
#   datetime: timestamp[us]
#   open: double
#   high: double
#   low: double
#   close: double
#   volume: double
#   amount: double

# 分区：按年分区
# 600519.SH/1d/
#   ├── 2022.parquet
#   ├── 2023.parquet
#   └── 2024.parquet

# 压缩：Snappy
# 行组大小：10000 行
```

### 2.3 缓存策略

```python
class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_dir: str, ttl: int = 3600):
        self.cache_dir = cache_dir
        self.ttl = ttl  # 缓存过期时间 (秒)
    
    def get(self, key: str) -> Optional[DataFrame]:
        """获取缓存"""
        path = self._get_path(key)
        if not path.exists():
            return None
        
        # 检查过期
        if self._is_expired(path):
            path.unlink()
            return None
        
        return pd.read_parquet(path)
    
    def set(self, key: str, data: DataFrame):
        """设置缓存"""
        path = self._get_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        data.to_parquet(path, compression='snappy')
    
    def _get_path(self, key: str) -> Path:
        """生成缓存文件路径"""
        # key = "akshare:600519.SH:1d:2023-01-01:2023-12-31"
        parts = key.split(':')
        return Path(self.cache_dir) / parts[0] / parts[1] / f"{parts[2]}.parquet"
```

---

## 3. PostgreSQL Schema (Phase 2)

### 3.1 用户模块

```sql
-- 用户表
CREATE TABLE users (
    id              VARCHAR(32) PRIMARY KEY,
    username        VARCHAR(50) UNIQUE NOT NULL,
    email           VARCHAR(100) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    status          SMALLINT DEFAULT 1,  -- 1:正常 2:禁用
    role            VARCHAR(20) DEFAULT 'user',  -- user/admin
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

### 3.2 策略模块

```sql
-- 策略表
CREATE TABLE strategies (
    id              VARCHAR(32) PRIMARY KEY,
    user_id         VARCHAR(32) NOT NULL REFERENCES users(id),
    name            VARCHAR(100) NOT NULL,
    description     TEXT,
    type            VARCHAR(30) NOT NULL,  -- ma_cross/momentum/rsi/macd
    language        VARCHAR(20) DEFAULT 'python',
    code            TEXT,
    parameters      JSONB DEFAULT '{}',
    is_public       BOOLEAN DEFAULT FALSE,
    is_template     BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_strategies_user_id ON strategies(user_id);
CREATE INDEX idx_strategies_type ON strategies(type);
CREATE INDEX idx_strategies_public ON strategies(is_public) WHERE is_public = TRUE;

-- 策略版本表
CREATE TABLE strategy_versions (
    id              BIGSERIAL PRIMARY KEY,
    strategy_id     VARCHAR(32) NOT NULL REFERENCES strategies(id) ON DELETE CASCADE,
    version         INTEGER NOT NULL,
    code            TEXT NOT NULL,
    parameters      JSONB,
    change_log      TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(strategy_id, version)
);
```

### 3.3 回测模块

```sql
-- 回测任务表
CREATE TABLE backtests (
    id              VARCHAR(32) PRIMARY KEY,
    user_id         VARCHAR(32) NOT NULL REFERENCES users(id),
    strategy_id     VARCHAR(32) REFERENCES strategies(id),
    name            VARCHAR(100) NOT NULL,
    symbol          VARCHAR(20) NOT NULL,
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    initial_capital DECIMAL(18,2) NOT NULL,
    commission_rate DECIMAL(10,6) DEFAULT 0.0003,
    slippage        DECIMAL(10,6) DEFAULT 0.001,
    status          VARCHAR(20) DEFAULT 'pending',  -- pending/running/completed/failed
    error_message   TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);

CREATE INDEX idx_backtests_user_id ON backtests(user_id);
CREATE INDEX idx_backtests_status ON backtests(status);

-- 回测结果表
CREATE TABLE backtest_results (
    backtest_id     VARCHAR(32) PRIMARY KEY REFERENCES backtests(id) ON DELETE CASCADE,
    total_return    DECIMAL(10,6),
    annual_return   DECIMAL(10,6),
    sharpe_ratio    DECIMAL(10,4),
    max_drawdown    DECIMAL(10,6),
    win_rate        DECIMAL(5,4),
    total_trades    INTEGER,
    winning_trades  INTEGER,
    losing_trades   INTEGER,
    avg_profit      DECIMAL(18,2),
    avg_loss        DECIMAL(18,2),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 回测交易记录表
CREATE TABLE backtest_trades (
    id              BIGSERIAL PRIMARY KEY,
    backtest_id     VARCHAR(32) NOT NULL REFERENCES backtests(id) ON DELETE CASCADE,
    datetime        TIMESTAMPTZ NOT NULL,
    symbol          VARCHAR(20) NOT NULL,
    side            VARCHAR(10) NOT NULL,  -- buy/sell
    quantity        BIGINT NOT NULL,
    price           DECIMAL(18,4) NOT NULL,
    commission      DECIMAL(18,2) DEFAULT 0,
    profit          DECIMAL(18,2)
);

CREATE INDEX idx_backtest_trades_backtest_id ON backtest_trades(backtest_id);
CREATE INDEX idx_backtest_trades_datetime ON backtest_trades(datetime);
```

### 3.4 TimescaleDB 时序表

```sql
-- 加载 TimescaleDB 扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- K 线数据表
CREATE TABLE klines (
    time            TIMESTAMPTZ NOT NULL,
    symbol          VARCHAR(20) NOT NULL,
    interval        VARCHAR(10) NOT NULL,  -- 1m/5m/1h/1d
    open            DECIMAL(18,4) NOT NULL,
    high            DECIMAL(18,4) NOT NULL,
    low             DECIMAL(18,4) NOT NULL,
    close           DECIMAL(18,4) NOT NULL,
    volume          BIGINT NOT NULL,
    amount          DECIMAL(18,2)
);

-- 创建超表 (按时间分区)
SELECT create_hypertable('klines', 'time');

-- 创建索引
CREATE INDEX idx_klines_symbol_time_interval 
    ON klines(symbol, interval, time DESC);

-- 数据保留策略：保留 5 年
SELECT add_retention_policy('klines', INTERVAL '5 years');

-- 压缩策略：90 天前的数据压缩
SELECT add_compression_policy('klines', INTERVAL '90 days');

-- 连续聚合：1 小时 K 线 (从 1 分钟聚合)
CREATE MATERIALIZED VIEW klines_1h
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS time,
    symbol,
    first(open, time) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, time) AS close,
    sum(volume) AS volume,
    sum(amount) AS amount
FROM klines
WHERE interval = '1m'
GROUP BY time_bucket('1 hour', time), symbol
WITH NO DATA;

-- 刷新策略
SELECT add_continuous_refresh_policy('klines_1h', INTERVAL '1 hour');
```

---

## 4. Redis 缓存设计 (Phase 2)

### 4.1 Key 命名规范

```
openfinagent:{module}:{resource}:{identifier}
```

### 4.2 缓存结构

```redis
# 用户会话 (String, TTL: 2h)
openfinagent:session:{user_id} -> JWT Token

# 热门策略 (Sorted Set, 按浏览量排序)
openfinagent:strategies:popular -> {strategy_id: score}

# 回测进度 (Hash, TTL: 24h)
openfinagent:backtest:{backtest_id} -> {
    status: "running",
    progress: "0.65",
    current_bar: "2023-06-15"
}

# 数据缓存 (String, TTL: 1h)
openfinagent:data:kline:{symbol}:{interval}:{date} -> Parquet Base64

# 限流计数 (String, TTL: 60s)
openfinagent:ratelimit:{user_id}:{endpoint} -> count

# 实时行情 (Hash, TTL: 60s)
openfinagent:market:quote:{symbol} -> {
    last_price: "10.50",
    volume: "1000000",
    update_time: "2026-03-06T08:00:00Z"
}
```

### 4.3 缓存策略

| 数据类型 | 策略 | TTL | 更新方式 |
|----------|------|-----|----------|
| 用户会话 | Cache-Aside | 2h | 登录时写入 |
| 热门策略 | Write-Through | 1h | 访问时更新 |
| 回测进度 | Write-Through | 24h | 进度更新时写入 |
| 数据缓存 | Cache-Aside | 1h | 首次查询时写入 |
| 实时行情 | Write-Through | 60s | 行情推送时更新 |

---

## 5. 索引策略

### 5.1 PostgreSQL 索引

| 表 | 索引 | 类型 | 说明 |
|------|------|------|------|
| users | idx_users_username | B-Tree | 登录查询 |
| users | idx_users_email | B-Tree | 邮箱查询 |
| strategies | idx_strategies_user_id | B-Tree | 用户策略列表 |
| strategies | idx_strategies_public | 部分索引 | 公开策略查询 |
| backtests | idx_backtests_user_id | B-Tree | 用户回测列表 |
| backtests | idx_backtests_status | B-Tree | 状态过滤 |
| backtest_trades | idx_backtest_trades_backtest_id | B-Tree | 回测交易查询 |
| backtest_trades | idx_backtest_trades_datetime | B-Tree | 时间范围查询 |

### 5.2 TimescaleDB 索引

| 表 | 索引 | 说明 |
|------|------|------|
| klines | symbol + interval + time (DESC) | K 线查询 |

---

## 6. 数据迁移

### 6.1 迁移工具

```python
# 使用 Alembic 管理数据库迁移
# alembic.ini

[alembic]
script_location = migrations

# 迁移版本
# migrations/
# ├── versions/
# │   ├── 001_initial_schema.py
# │   ├── 002_add_strategy_versions.py
# │   └── 003_add_backtest_results.py
```

### 6.2 迁移脚本示例

```python
# migrations/versions/001_initial_schema.py

from alembic import op
import sqlalchemy as sa

def upgrade():
    # 创建用户表
    op.create_table('users',
        sa.Column('id', sa.String(32), primary_key=True),
        sa.Column('username', sa.String(50), unique=True, nullable=False),
        sa.Column('email', sa.String(100), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('status', sa.SmallInteger, default=1),
        sa.Column('role', sa.String(20), default='user'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now())
    )
    
    # 创建索引
    op.create_index('idx_users_username', 'users', ['username'])
    op.create_index('idx_users_email', 'users', ['email'])

def downgrade():
    op.drop_table('users')
```

---

## 7. 备份策略

### 7.1 备份计划

| 数据类型 | 备份方式 | 频率 | 保留期 |
|----------|----------|------|--------|
| PostgreSQL | pg_dump + WAL | 每日全量 + 实时 WAL | 30 天 |
| TimescaleDB | pg_dump + 对象存储 | 每日全量 | 90 天 |
| Redis | RDB + AOF | 每小时 RDB + 实时 AOF | 7 天 |
| 本地文件 | rsync + tar | 每日 | 30 天 |

### 7.2 备份脚本

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/tradeflow"
DATE=$(date +%Y%m%d)

# PostgreSQL 备份
pg_dump -U tradeflow -h localhost tradeflow | gzip > $BACKUP_DIR/postgres_$DATE.sql.gz

# TimescaleDB 备份
pg_dump -U tradeflow -h localhost tradeflow -t klines | gzip > $BACKUP_DIR/timescale_$DATE.sql.gz

# 本地文件备份
tar -czf $BACKUP_DIR/files_$DATE.tar.gz ~/.openfinagent/

# 清理旧备份
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

---

## 8. 性能优化

### 8.1 查询优化

```sql
-- ❌ 慢查询：全表扫描
SELECT * FROM backtest_trades 
WHERE symbol = '600519.SH';

-- ✅ 快查询：使用索引
SELECT * FROM backtest_trades 
WHERE backtest_id = 'xxx' AND symbol = '600519.SH';

-- ❌ 慢查询：N+1 问题
for backtest in backtests:
    trades = query("SELECT * FROM trades WHERE backtest_id = ?", backtest.id)

-- ✅ 快查询：批量加载
backtests = query("SELECT * FROM backtests WHERE user_id = ?", user_id)
backtest_ids = [b.id for b in backtests]
trades = query("SELECT * FROM trades WHERE backtest_id IN ?", backtest_ids)
```

### 8.2 分区策略

```sql
-- TimescaleDB 自动分区 (按时间)
-- 无需手动管理，TimescaleDB 自动创建分区

-- PostgreSQL 手动分区 (按用户)
CREATE TABLE backtests_partitioned (
    LIKE backtests INCLUDING ALL
) PARTITION BY HASH (user_id);

-- 创建分区
CREATE TABLE backtests_p0 PARTITION OF backtests_partitioned
    FOR VALUES WITH (MODULUS 10, REMAINDER 0);
CREATE TABLE backtests_p1 PARTITION OF backtests_partitioned
    FOR VALUES WITH (MODULUS 10, REMAINDER 1);
-- ...
```

---

*文档版本：v1.0 | 创建时间：2026-03-06*
