"""
OpenFinAgent - 首页 (v0.5.0)

统一的导航入口，清晰的页面结构
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

# ==================== 主界面 ====================
def main():
    """首页主界面"""
    
    # 标题
    st.markdown("""
    # 📈 OpenFinAgent
    ## AI 量化交易平台 - 让投资更简单
    """)
    
    st.divider()
    
    # 核心功能卡片
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🤖 策略工厂
        用自然语言描述你的交易想法，AI 自动生成策略代码
        
        **功能**:
        - 自然语言创建策略
        - AI 代码生成
        - 自动回测验证
        - 策略优化
        
        """)
        if st.button("🚀 开始创建", use_container_width=True, key="home_create"):
            st.switch_page("pages/03_🤖_策略工厂.py")
    
    with col2:
        st.markdown("""
        ### 📈 选股引擎
        基于策略自动筛选股票，批量回测生成股票池
        
        **功能**:
        - 策略选股
        - 批量回测
        - 股票池管理
        - 导出 CSV
        
        """)
        if st.button("🔍 开始选股", use_container_width=True, key="home_select"):
            st.switch_page("pages/04_📈_选股引擎.py")
    
    with col3:
        st.markdown("""
        ### 🔔 监控中心
        7x24 小时行情监控，实时捕捉交易信号
        
        **功能**:
        - 实时监控
        - 信号检测
        - 多渠道通知
        - 历史记录
        
        """)
        if st.button("🔔 创建监控", use_container_width=True, key="home_monitor"):
            st.switch_page("pages/05_🔔_监控中心.py")
    
    st.divider()
    
    # 快捷入口
    st.markdown("### 📚 更多功能")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("**📊 回测中心**")
        st.markdown("运行策略回测，查看详细报告")
        if st.button("查看回测", use_container_width=True, key="home_backtest"):
            st.switch_page("pages/backtest.py")
    
    with col2:
        st.markdown("**📚 策略库**")
        st.markdown("管理和查看已创建的策略")
        if st.button("查看策略", use_container_width=True, key="home_library"):
            st.switch_page("pages/compare.py")
    
    with col3:
        st.markdown("**📈 策略对比**")
        st.markdown("对比多个策略的性能")
        if st.button("开始对比", use_container_width=True, key="home_compare"):
            st.switch_page("pages/compare.py")
    
    with col4:
        st.markdown("**❓ 使用帮助**")
        st.markdown("查看使用指南和文档")
        if st.button("查看帮助", use_container_width=True, key="home_help"):
            st.markdown("""
            **快速开始**:
            1. 🤖 策略工厂 - 创建策略
            2. 📊 回测中心 - 运行回测
            3. 🔔 监控中心 - 设置监控
            
            **文档**:
            - [GitHub](https://github.com/bobipika2026/openfinagent)
            - [API 文档](http://localhost:8000/api/docs)
            """)
    
    st.divider()
    
    # 系统状态
    st.markdown("### ℹ️ 系统状态")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("版本", "v0.5.0")
    with col2:
        st.metric("状态", "🟢 运行正常")
    with col3:
        st.metric("API", "🟢 正常")


if __name__ == "__main__":
    main()
