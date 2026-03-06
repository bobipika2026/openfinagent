# OpenFinAgent 部署方案

**版本**: v1.0  
**最后更新**: 2026-03-06

---

## 1. 部署架构

### 1.1 当前阶段 (v0.1-v0.3): Python 包分发

```
┌─────────────────────────────────────────────────────────────┐
│                      用户本地环境                            │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              pip install tradeflow-ai                │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Python Environment (3.9+)                  │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐       │   │
│  │  │ tradeflow │  │  pandas   │  │  numpy    │       │   │
│  │  │   Core    │  │           │  │           │       │   │
│  │  └───────────┘  └───────────┘  └───────────┘       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              本地文件存储                            │   │
│  │  ~/.tradeflow/cache/  ~/.tradeflow/results/        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**部署方式**:
- PyPI 包分发
- 用户本地安装
- 零服务器依赖

### 1.2 未来规划 (v0.5+): Web 平台

```
┌─────────────────────────────────────────────────────────────┐
│                        用户接入层                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Web 前端    │  │  移动 App    │  │   Python SDK │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Cloudflare CDN                          │
│              (静态资源加速 + WAF 防护)                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes 集群                           │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Ingress   │  │   Istio     │  │  API Gateway│        │
│  │   (Nginx)   │  │   Gateway   │  │   (Kong)    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  Application Layer                   │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐            │   │
│  │  │   Web    │ │ Backtest │ │ Strategy │            │   │
│  │  │   API    │ │  Worker  │ │  Engine  │            │   │
│  │  └──────────┘ └──────────┘ └──────────┘            │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   Data Layer                         │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐            │   │
│  │  │PostgreSQL│ │Timescale │ │  Redis   │            │   │
│  │  │          │ │   DB     │ │ Cluster  │            │   │
│  │  └──────────┘ └──────────┘ └──────────┘            │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     外部依赖层                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  AKShare    │  │Yahoo Finance│  │    MinIO    │        │
│  │  (A 股数据)  │  │  (美股数据)  │  │  (文件存储)  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Python 包部署

### 2.1 打包配置

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name='tradeflow-ai',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.9,<4.0',
    install_requires=[
        'pandas>=1.5.0,<2.0.0',
        'numpy>=1.23.0,<2.0.0',
        'matplotlib>=3.6.0,<4.0.0',
        'jieba>=0.42.0,<1.0.0',
        'akshare>=1.10.0,<2.0.0',
        'tqdm>=4.65.0,<5.0.0',
        'pydantic>=2.0.0,<3.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
        ],
        'full': [
            'ta-lib>=0.4.0',
            'plotly>=5.15.0',
            'yfinance>=0.2.0',
            'ccxt>=4.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'tradeflow=tradeflow.cli:main',
        ],
    },
)
```

### 2.2 发布流程

```bash
# 1. 更新版本号
# src/tradeflow/__init__.py
__version__ = '0.1.0'

# 2. 构建包
python setup.py sdist bdist_wheel

# 3. 测试上传 (TestPyPI)
twine upload --repository testpypi dist/*

# 4. 测试安装
pip install -i https://test.pypi.org/simple/ tradeflow-ai

# 5. 正式上传
twine upload dist/*
```

### 2.3 安装方式

```bash
# 基础安装
pip install tradeflow-ai

# 完整安装 (包含所有可选依赖)
pip install tradeflow-ai[full]

# 开发安装
pip install tradeflow-ai[dev]

# 指定版本
pip install tradeflow-ai==0.1.0

# 从源码安装
git clone https://github.com/your-org/tradeflow-ai.git
cd tradeflow-ai
pip install -e .
```

---

## 3. Docker 部署 (Phase 2)

### 3.1 Dockerfile

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libatlas-base-dev \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制源代码
COPY src/ ./src/
COPY examples/ ./examples/

# 设置环境变量
ENV PYTHONPATH=/app/src
ENV TRADEFLOW_CACHE_DIR=/app/cache
ENV TRADEFLOW_LOG_LEVEL=INFO

# 创建缓存目录
RUN mkdir -p /app/cache /app/results

# 设置入口点
ENTRYPOINT ["python", "-m", "tradeflow"]
CMD ["--help"]
```

### 3.2 Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  tradeflow-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/tradeflow
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./cache:/app/cache
      - ./results:/app/results
    depends_on:
      - postgres
      - redis

  tradeflow-worker:
    build: .
    command: python -m tradeflow.worker
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/tradeflow
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./cache:/app/cache
      - ./results:/app/results
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=tradeflow
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  timescaledb:
    image: timescale/timescaledb:latest-pg15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=tradeflow
    volumes:
      - timescale_data:/var/lib/postgresql/data

volumes:
  postgres_data:
  redis_data:
  timescale_data:
```

---

## 4. Kubernetes 部署 (Phase 3)

### 4.1 Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tradeflow-api
  namespace: tradeflow
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tradeflow-api
  template:
    metadata:
      labels:
        app: tradeflow-api
    spec:
      containers:
      - name: tradeflow-api
        image: tradeflow/tradeflow-ai:v0.5.0
        ports:
        - containerPort: 8000
        resources:
          requests:
            cpu: "250m"
            memory: "512Mi"
          limits:
            cpu: "1000m"
            memory: "2Gi"
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: url
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### 4.2 HPA 自动伸缩

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: tradeflow-api-hpa
  namespace: tradeflow
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: tradeflow-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## 5. CI/CD

### 5.1 GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  release:
    types: [published]

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
      run: |
        pip install -r requirements-dev.txt
    
    - name: Lint
      run: |
        black --check src/ tests/
        flake8 src/ tests/
        mypy src/
    
    - name: Test
      run: |
        pytest tests/ -v --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.9"
    
    - name: Build package
      run: |
        pip install build twine
        python -m build
    
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_TOKEN }}
    
    - name: Build Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: |
          tradeflow/tradeflow-ai:${{ github.ref_name }}
          tradeflow/tradeflow-ai:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/tradeflow-api \
          tradeflow-api=tradeflow/tradeflow-ai:${{ github.ref_name }} \
          -n tradeflow
```

---

## 6. 监控告警

### 6.1 Prometheus 指标

```python
# src/tradeflow/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# 回测次数
backtest_total = Counter(
    'tradeflow_backtest_total',
    'Total number of backtests',
    ['status', 'strategy_type']
)

# 回测延迟
backtest_duration = Histogram(
    'tradeflow_backtest_duration_seconds',
    'Backtest duration',
    ['strategy_type'],
    buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0]
)

# 活跃用户
active_users = Gauge(
    'tradeflow_active_users',
    'Number of active users'
)

# 数据缓存命中率
cache_hit_ratio = Gauge(
    'tradeflow_cache_hit_ratio',
    'Data cache hit ratio'
)
```

### 6.2 Grafana 仪表板

| 仪表板 | 指标 | 说明 |
|--------|------|------|
| **系统概览** | QPS、延迟、错误率、CPU/内存 | 整体健康度 |
| **回测性能** | 回测次数、平均延迟、成功率 | 回测服务监控 |
| **业务指标** | 活跃用户、策略数、回测数 | 业务增长监控 |
| **数据缓存** | 命中率、缓存大小、过期数 | 缓存性能 |

### 6.3 告警规则

```yaml
# prometheus/alerts.yml
groups:
- name: tradeflow-alerts
  rules:
  - alert: HighErrorRate
    expr: sum(rate(tradeflow_backtest_total{status="failed"}[5m])) / sum(rate(tradeflow_backtest_total[5m])) > 0.05
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "回测错误率过高"
      description: "回测错误率超过 5% (当前值：{{ $value }})"

  - alert: HighLatency
    expr: histogram_quantile(0.99, rate(tradeflow_backtest_duration_seconds_bucket[5m])) > 10
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "回测延迟过高"
      description: "P99 回测延迟超过 10 秒 (当前值：{{ $value }}s)"

  - alert: PodCrashLooping
    expr: rate(kube_pod_container_status_restarts_total[15m]) * 60 * 5 > 0
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Pod 频繁重启"
      description: "Pod {{ $labels.pod }} 在 5 分钟内重启超过 5 次"
```

---

## 7. 环境配置

### 7.1 环境变量

```bash
# .env.example
# 应用配置
TRADEFLOW_ENV=production
TRADEFLOW_LOG_LEVEL=INFO
TRADEFLOW_DEBUG=false

# 数据库配置
DATABASE_URL=postgresql://user:pass@localhost:5432/tradeflow
REDIS_URL=redis://localhost:6379

# 数据源配置
TRADEFLOW_DATA_SOURCE=akshare
AKSHARE_API_KEY=
YAHOO_API_KEY=

# 缓存配置
TRADEFLOW_CACHE_ENABLED=true
TRADEFLOW_CACHE_DIR=~/.tradeflow/cache
TRADEFLOW_CACHE_TTL=3600

# 安全配置
TRADEFLOW_SECRET_KEY=your-secret-key
TRADEFLOW_API_KEY_EXPIRY=86400
```

### 7.2 配置管理

```python
# src/tradeflow/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    env: str = "development"
    log_level: str = "INFO"
    debug: bool = False
    
    database_url: str
    redis_url: str
    
    data_source: str = "akshare"
    cache_enabled: bool = True
    cache_dir: str = "~/.tradeflow/cache"
    cache_ttl: int = 3600
    
    secret_key: str
    api_key_expiry: int = 86400
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

---

## 8. 安全加固

### 8.1 API 安全

```python
# 速率限制
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

@app.get("/api/backtest", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def run_backtest():
    pass

# JWT 认证
from fastapi_jwt_auth import AuthJWT

@AuthorizeJWT()
async def get_user_info(Authorize: AuthJWT = Depends()):
    current_user = Authorize.get_jwt_subject()
    return {"user": current_user}
```

### 8.2 数据安全

```python
# 敏感数据加密
from cryptography.fernet import Fernet

class DataEncryptor:
    def __init__(self, key: str):
        self.fernet = Fernet(key.encode())
    
    def encrypt(self, data: str) -> str:
        return self.fernet.encrypt(data.encode()).decode()
    
    def decrypt(self, data: str) -> str:
        return self.fernet.decrypt(data.encode()).decode()

# API Key 加密存储
encrypted_key = encryptor.encrypt(user.api_key)
```

---

## 9. 成本优化

### 9.1 资源优化

| 措施 | 预期节省 |
|------|----------|
| 使用 Spot 实例 (非核心) | 60-70% |
| HPA 自动伸缩 | 30-40% |
| 数据压缩 (TimescaleDB) | 80-90% |
| 缓存热点数据 | 50-60% |

### 9.2 存储优化

```sql
-- TimescaleDB 压缩
SELECT add_compression_policy('klines', INTERVAL '90 days');

-- 数据保留策略
SELECT add_retention_policy('klines', INTERVAL '5 years');

-- 连续聚合 (减少存储)
CREATE MATERIALIZED VIEW klines_1d
WITH (timescaledb.continuous) AS
SELECT ...
FROM klines
GROUP BY time_bucket('1 day', time), symbol;
```

---

*文档版本：v1.0 | 创建时间：2026-03-06*
