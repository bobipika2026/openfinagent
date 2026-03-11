#!/usr/bin/env python3
"""
OpenFinAgent Web UI - 主应用 (v0.5.0)

重新设计的导航框架:
- 统一的侧边栏导航
- 清晰的页面结构
- 去除重复导航
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
    initial_sidebar_state="expanded",
)

# ==================== 统一的侧边栏导航 ====================
def render_sidebar():
    """渲染统一的侧边栏导航"""
    with st.sidebar:
        # Logo 和标题
        st.markdown("## 📈 OpenFinAgent")
        st.markdown("AI 量化交易平台")
        st.divider()
        
        # 主导航
        st.markdown("### 主导航")
        page = st.radio(
            "导航",
            [
                "🏠 首页",
                "🤖 策略工厂",
                "📈 选股引擎",
                "🔔 监控中心",
                "📊 回测中心",
                "📚 策略库"
            ],
            label_visibility="collapsed",
            index=0
        )
        
        st.divider()
        
        # 快捷操作
        st.markdown("### 快捷操作")
        if st.button("➕ 创建策略", use_container_width=True, key="sidebar_create"):
            st.session_state.nav_redirect = "🤖 策略工厂"
        if st.button("🔍 选股", use_container_width=True, key="sidebar_select"):
            st.session_state.nav_redirect = "📈 选股引擎"
        if st.button("🔔 新建监控", use_container_width=True, key="sidebar_monitor"):
            st.session_state.nav_redirect = "🔔 监控中心"
        
        st.divider()
        
        # 系统信息
        st.markdown("### ℹ️ 系统")
        st.markdown("**版本**: v0.5.0")
        st.markdown("**状态**: 🟢 运行正常")
        
        # 帮助链接
        with st.expander("❓ 帮助"):
            st.markdown("""
            **快速开始**:
            1. 🤖 策略工厂 - 用自然语言创建策略
            2. 📈 选股引擎 - 批量回测生成股票池
            3. 🔔 监控中心 - 7x24 小时监控信号
            
            **文档**:
            - [使用指南](https://github.com/bobipika2026/openfinagent)
            - [API 文档](http://localhost:8000/api/docs)
            """)
    
    return page


# ==================== 页面路由 ====================
def navigate_to(page_name: str):
    """导航到指定页面"""
    # 检查是否有重定向
    if 'nav_redirect' in st.session_state:
        page_name = st.session_state.nav_redirect
        del st.session_state.nav_redirect
    
    # 页面映射
    page_map = {
        "🏠 首页": "pages/home.py",
        "🤖 策略工厂": "pages/03_🤖_策略工厂.py",
        "📈 选股引擎": "pages/04_📈_选股引擎.py",
        "🔔 监控中心": "pages/05_🔔_监控中心.py",
        "📊 回测中心": "pages/backtest.py",
        "📚 策略库": "pages/compare.py"
    }
    
    # 使用 Streamlit 的页面导航
    if page_name in page_map:
        st.switch_page(page_map[page_name])


# ==================== 主程序 ====================
def main():
    """主程序"""
    # 渲染侧边栏
    page = render_sidebar()
    
    # 处理导航
    if page == "🏠 首页":
        # 使用 Streamlit 的多页面应用
        st.switch_page("pages/home.py")
    elif page == "🤖 策略工厂":
        st.switch_page("pages/03_🤖_策略工厂.py")
    elif page == "📈 选股引擎":
        st.switch_page("pages/04_📈_选股引擎.py")
    elif page == "🔔 监控中心":
        st.switch_page("pages/05_🔔_监控中心.py")
    elif page == "📊 回测中心":
        st.switch_page("pages/backtest.py")
    elif page == "📚 策略库":
        st.switch_page("pages/compare.py")


if __name__ == "__main__":
    main()
