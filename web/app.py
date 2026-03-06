"""
OpenFinAgent Web UI - 主应用入口
AI 量化交易平台
"""

import streamlit as st
from pathlib import Path
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 页面配置
st.set_page_config(
    page_title="OpenFinAgent - AI 量化交易平台",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS 样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 侧边栏导航
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/stock-market.png", width=80)
    st.markdown("### 📊 OpenFinAgent")
    st.markdown("*AI 驱动的量化交易平台*")
    
    st.divider()
    
    # 导航菜单
    page = st.radio(
        "导航",
        ["🏠 首页", "✨ 创建策略", "📈 回测分析", "⚖️ 策略对比"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # 快速信息
    st.markdown("### ℹ️ 关于")
    st.markdown("""
    - **版本**: 0.1.0
    - **GitHub**: bobipika2026/openfinagent
    - **文档**: [查看文档](https://github.com/bobipika2026/openfinagent)
    """)

# 根据选择加载页面
if page == "🏠 首页":
    from pages import home
    home.show()
elif page == "✨ 创建策略":
    from pages import create
    create.show()
elif page == "📈 回测分析":
    from pages import backtest
    backtest.show()
elif page == "⚖️ 策略对比":
    from pages import compare
    compare.show()
