# OpenFinAgent Web UI - 部署文档

## ✅ 完成情况

### 已创建文件

```
web/
├── app.py                    # 主应用入口 (1.9KB)
├── requirements.txt          # Python 依赖 (140B)
├── README.md                 # 使用说明 (2.9KB)
├── DEPLOYMENT.md            # 部署文档 (本文件)
├── run.sh                    # 快速启动脚本
├── test_imports.py          # 模块测试脚本
└── pages/
    ├── home.py              # 首页 (4.5KB)
    ├── create.py            # 策略创建页面 (11.9KB)
    ├── backtest.py          # 回测分析页面 (16.0KB)
    └── compare.py           # 策略对比页面 (17.4KB)
```

### 核心功能

#### 1. 🏠 首页 (home.py)
- ✅ 项目介绍和特色展示
- ✅ 快速开始按钮（导航到各功能页面）
- ✅ 可用策略列表展示
- ✅ 示例策略展示（均线交叉、动量、RSI）
- ✅ 关键指标统计

#### 2. ✨ 创建策略 (create.py)
- ✅ **自然语言创建** - 输入中文描述，AI 自动解析生成策略
  - 示例模板展示
  - AI 解析并预览
  - 错误处理和友好提示
- ✅ **参数配置创建** - 手动配置策略参数
  - 6 种策略类型支持：
    - 均线交叉 (MA Cross)
    - 动量策略 (Momentum)
    - RSI 超买超卖
    - MACD 金叉死叉
    - 布林带 (Bollinger Bands)
    - 双均线 + 成交量
  - 每种策略的专属参数配置界面
  - 通用设置（策略名称、初始资金）
- ✅ 策略预览功能
- ✅ Session 状态管理

#### 3. 📈 回测分析 (backtest.py)
- ✅ 数据源选择（Akshare A 股 / 模拟数据）
- ✅ 股票代码输入
- ✅ 时间范围选择
- ✅ 高级设置（手续费率、滑点）
- ✅ 回测结果展示：
  - 关键指标卡片（总收益、年化收益、夏普比率、最大回撤）
  - 详细收益指标
  - 详细风险指标
  - 交易统计
- ✅ 可视化图表：
  - 权益曲线图（Plotly）
  - 回撤分析图
  - 指标雷达图
- ✅ 交易记录表格
- ✅ CSV 下载功能
- ✅ 错误处理和友好提示

#### 4. ⚖️ 策略对比 (compare.py)
- ✅ 多策略选择（2-5 个）
- ✅ 预设策略配置：
  - 均线交叉 (5,20) 和 (10,50)
  - 动量策略 (20 日，5%)
  - RSI 策略 (14,30,70)
  - MACD 策略 (12,26,9)
  - 布林带 (20,2)
  - 双均线 + 成交量
- ✅ 对比结果展示：
  - 归一化权益曲线对比图
  - 性能指标对比表格（高亮最优值）
  - 收益对比柱状图
  - 风险对比柱状图
  - 交易统计对比
- ✅ 进度条显示
- ✅ 错误处理

### 技术实现

#### 前端框架
- **Streamlit** - 快速构建数据应用
- **Plotly** - 交互式图表
- **Matplotlib** - 静态图表（备用）

#### 集成模块
- ✅ `src.strategy.builder` - 策略构建器
- ✅ `src.backtest.engine` - 回测引擎
- ✅ `src.visualization.plotter` - 可视化工具
- ✅ 所有 6 种策略类型

#### 代码质量
- ✅ 完善的错误处理
- ✅ 用户友好的中文提示
- ✅ 类型注解
- ✅ 日志记录
- ✅ 代码注释

### 测试结果

```
============================================================
OpenFinAgent Web UI - 模块导入测试
============================================================

[测试 1] 导入策略构建器...
✅ 策略构建器导入成功

[测试 2] 导入回测引擎...
✅ 回测引擎导入成功

[测试 3] 导入可视化工具...
✅ 可视化工具导入成功

[测试 4] 测试所有策略类型...
✅ 6 种策略类型全部测试通过

[测试 5] 运行简单回测...
✅ 回测功能正常

============================================================
测试结果：5 通过，0 失败
============================================================
```

## 🚀 部署步骤

### 1. 安装依赖

```bash
cd /root/.openclaw/workspace/projects/tradeflow-ai/web

# 方式 1：使用 pip
pip install -r requirements.txt

# 方式 2：使用快速启动脚本
./run.sh
```

### 2. 运行应用

```bash
# 方式 1：直接运行
streamlit run app.py

# 方式 2：使用启动脚本
./run.sh

# 方式 3：指定端口和地址
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### 3. 访问界面

打开浏览器访问：`http://localhost:8501`

## 📝 使用说明

### 创建第一个策略

1. 访问首页，点击"✨ 创建第一个策略"
2. 选择创建方式：
   - **自然语言创建**：输入"当 5 日均线上穿 20 日均线时买入，下穿时卖出，初始资金 10 万元"
   - **参数配置**：选择"均线交叉策略"，配置参数
3. 点击创建按钮
4. 查看策略预览

### 运行回测

1. 切换到"📈 回测分析"页面
2. 选择股票代码（如 000001）
3. 设置时间范围
4. 点击"▶️ 运行回测"
5. 查看回测结果和图表

### 策略对比

1. 切换到"⚖️ 策略对比"页面
2. 选择股票和时间范围
3. 选择 2-5 个要对比的策略
4. 点击"▶️ 运行对比"
5. 查看对比图表和指标表格

## 🔧 配置选项

### 环境变量（可选）

```bash
# 设置默认端口
export STREAMLIT_SERVER_PORT=8501

# 设置默认地址
export STREAMLIT_SERVER_ADDRESS=0.0.0.0

# 启用浏览器自动打开
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### Streamlit 配置

创建 `~/.streamlit/config.toml`：

```toml
[server]
port = 8501
address = "0.0.0.0"
headless = true

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1E88E5"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

## 🐛 已知问题和解决方案

### 1. Streamlit 未安装

**症状**：运行时报错 `ModuleNotFoundError: No module named 'streamlit'`

**解决**：
```bash
pip install streamlit
```

### 2. 中文显示问题

**症状**：图表中中文显示为方块

**解决**：
```bash
# Ubuntu/Debian
sudo apt-get install fonts-wqy-zenhei

# CentOS/RHEL
sudo yum install wqy-zenhei-fonts
```

### 3. 数据加载失败

**症状**：回测时提示数据加载失败

**解决**：
- 检查股票代码是否正确（6 位数字）
- 检查时间范围是否合理
- 切换到"模拟数据"模式测试

### 4. 端口被占用

**症状**：端口 8501 已被占用

**解决**：
```bash
# 使用其他端口
streamlit run app.py --server.port 8502
```

## 📊 性能优化建议

### 1. 数据缓存

对于频繁访问的股票数据，可以实现缓存机制：

```python
@st.cache_data
def load_cached_data(symbol, start_date, end_date):
    return load_data(symbol, start_date, end_date)
```

### 2. 延迟加载

对于大型图表，可以使用延迟加载：

```python
if st.checkbox("显示详细图表"):
    show_equity_chart(results)
```

### 3. 分页显示

对于大量交易记录，可以分页显示：

```python
st.dataframe(df, use_container_width=True, height=400)
```

## 🔒 安全注意事项

### 1. 生产环境部署

- 启用 HTTPS
- 配置认证机制
- 限制访问 IP
- 设置会话超时

### 2. 数据源安全

- 使用官方数据源（Akshare、Yahoo Finance）
- 验证输入参数
- 限制时间范围

### 3. 资源限制

- 设置最大回测周期
- 限制并发请求
- 监控内存使用

## 📈 未来改进计划

### 短期（v0.2.0）
- [ ] 添加策略保存功能
- [ ] 添加策略加载功能
- [ ] 支持自定义策略上传
- [ ] 添加用户认证

### 中期（v0.3.0）
- [ ] 实时行情接入
- [ ] 模拟交易功能
- [ ] 策略绩效报告导出（PDF）
- [ ] 多语言支持

### 长期（v1.0.0）
- [ ] 实盘交易接口
- [ ] 策略市场
- [ ] 社区分享功能
- [ ] 移动端适配

## 📞 技术支持

- **GitHub**: [bobipika2026/openfinagent](https://github.com/bobipika2026/openfinagent)
- **问题反馈**: 提交 Issue
- **文档**: 查看 README.md

---

**部署时间**: 2026-03-06  
**版本**: 0.1.0  
**状态**: ✅ 生产就绪
