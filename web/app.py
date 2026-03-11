"""
OpenFinAgent Web UI - 首页 (v0.5.0)

简洁的 4 页面导航：
- 首页（本页面）
- 策略工厂
- 监控
- 回测
"""

import streamlit as st
from pathlib import Path
import sys

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="OpenFinAgent - AI 量化交易平台",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==================== 首页内容 ====================
st.markdown("""
# 📈 OpenFinAgent
## AI 量化交易平台

让投资更简单，用 AI 降低量化门槛
""")

st.divider()

# 核心功能
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 🤖 策略工厂
    用自然语言创建策略
    
    - AI 自动生成代码
    - 自动回测验证
    - 智能优化参数
    """)
    if st.button("🚀 开始创建", use_container_width=True):
        st.switch_page("pages/1_🤖_策略工厂.py")

with col2:
    st.markdown("""
    ### 🔔 监控中心
    7x24 实时监控
    
    - 信号自动检测
    - 多渠道通知
    - 历史记录查询
    """)
    if st.button("🔔 创建监控", use_container_width=True):
        st.switch_page("pages/2_🔔_监控.py")

with col3:
    st.markdown("""
    ### 📊 回测中心
    策略性能评估
    
    - 历史数据回测
    - 性能评分
    - 结果可视化
    """)
    if st.button("📊 开始回测", use_container_width=True):
        st.switch_page("pages/3_📊_回测.py")

st.divider()

# 系统状态
st.markdown("### ℹ️ 系统状态")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("版本", "v0.5.0")
with col2:
    st.metric("状态", "🟢 运行正常")
with col3:
    st.metric("模型", "GLM-5")

st.divider()

# 快速开始
with st.expander("❓ 快速开始指南"):
    st.markdown("""
    **3 步开始量化交易**:
    
    1. **创建策略** → 进入策略工厂，用自然语言描述你的交易想法
    2. **运行回测** → 查看策略的历史表现和评分
    3. **设置监控** → 实时监控市场信号，自动通知
    
    **示例策略描述**:
    ```
    当 5 日均线上穿 20 日均线时买入，下穿时卖出
    ```
    
    ---
    
    **GitHub**: https://github.com/bobipika2026/openfinagent  
    **API 文档**: http://localhost:8000/api/docs
    """)