# TradeFlow AI - Dockerfile
# 多阶段构建，优化镜像大小

# ========== 构建阶段 ==========
FROM python:3.11-slim as builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir --user -r requirements.txt

# ========== 运行阶段 ==========
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    APP_HOME=/app

WORKDIR $APP_HOME

# 创建非 root 用户
RUN groupadd -r tradeflow && useradd -r -g tradeflow tradeflow

# 从构建阶段复制依赖
COPY --from=builder /root/.local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /root/.local/bin /usr/local/bin

# 复制应用代码
COPY tradeflow/ ./tradeflow/
COPY setup.py .
COPY README.md .

# 设置权限
RUN chown -R tradeflow:tradeflow $APP_HOME
USER tradeflow

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import tradeflow; print('OK')" || exit 1

# 暴露端口（如果需要 API 服务）
EXPOSE 8000

# 默认命令
CMD ["python", "-m", "tradeflow"]

# ========== 开发阶段 ==========
# 使用示例：docker build --target development -t tradeflow-ai:dev .
FROM builder as development

WORKDIR /app

# 复制开发依赖
COPY requirements-dev.txt .
RUN pip install --no-cache-dir --user -r requirements-dev.txt

# 复制代码（用于开发）
COPY . .

# 开发模式运行
CMD ["python", "-m", "pytest", "tests/", "-v", "--watch"]
