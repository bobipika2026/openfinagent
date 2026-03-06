"""
导航组件 - 侧边栏优化
"""

import streamlit as st
from pathlib import Path


def render_sidebar():
    """渲染优化后的侧边栏"""
    
    with st.sidebar:
        # Logo 和标题
        st.markdown(
            """
            <style>
                .sidebar-logo {
                    text-align: center;
                    padding: 20px 0;
                }
                .sidebar-title {
                    font-size: 1.8rem;
                    font-weight: bold;
                    color: #667eea;
                    text-align: center;
                    margin: 10px 0;
                }
                .sidebar-subtitle {
                    font-size: 0.9rem;
                    color: #666;
                    text-align: center;
                    margin-bottom: 20px;
                }
                .nav-item {
                    padding: 12px 15px;
                    margin: 5px 0;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                .nav-item:hover {
                    background-color: rgba(102, 126, 234, 0.1);
                }
                .nav-item.active {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }
                .sidebar-divider {
                    margin: 20px 0;
                    border-top: 1px solid #e0e0e0;
                }
                .sidebar-info {
                    font-size: 0.85rem;
                    color: #666;
                    padding: 10px;
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    margin-top: 20px;
                }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        # Logo 区域
        st.markdown(
            """
            <div class="sidebar-logo">
                <div style="font-size: 3rem;">📈</div>
                <div class="sidebar-title">OpenFinAgent</div>
                <div class="sidebar-subtitle">AI 驱动的量化交易平台</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.divider()
        
        # 导航菜单
        st.markdown("### 🧭 导航")
        
        pages = {
            "🏠 首页": "pages/home.py",
            "✨ 创建策略": "pages/create.py",
            "📈 回测分析": "pages/backtest.py",
            "⚖️ 策略对比": "pages/compare.py",
            "📚 策略模板": "pages/templates.py" if (Path(__file__).parent.parent / "pages" / "templates.py").exists() else None,
            "📊 实时监控": "pages/monitor.py" if (Path(__file__).parent.parent / "pages" / "monitor.py").exists() else None,
        }
        
        # 过滤存在的页面
        available_pages = {k: v for k, v in pages.items() if v is not None}
        
        # 获取当前页面
        current_page = st.query_params.get("page", "🏠 首页")
        
        # 导航选择
        selected_page = st.radio(
            "页面导航",
            list(available_pages.keys()),
            index=list(available_pages.keys()).index(current_page) if current_page in available_pages else 0,
            label_visibility="collapsed"
        )
        
        # 页面切换逻辑
        if selected_page != current_page:
            page_file = available_pages[selected_page]
            if page_file:
                st.switch_page(page_file)
        
        st.divider()
        
        # 快速操作
        st.markdown("### ⚡ 快速操作")
        
        if st.button("🔄 刷新数据", use_container_width=True):
            st.cache_resource.clear()
            st.success("✅ 缓存已清除")
        
        if st.button("📥 导出数据", use_container_width=True):
            st.info("💡 导出功能开发中...")
        
        st.divider()
        
        # 主题切换
        st.markdown("### 🎨 主题")
        
        from utils.theme import render_theme_toggle
        render_theme_toggle()
        
        st.divider()
        
        # 关于信息
        st.markdown("### ℹ️ 关于")
        
        st.markdown(
            """
            <div class="sidebar-info">
                <div><strong>版本:</strong> v0.3.2</div>
                <div><strong>GitHub:</strong> bobipika2026/openfinagent</div>
                <div style="margin-top: 10px;">
                    <a href="https://github.com/bobipika2026/openfinagent" target="_blank">查看文档</a>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # 实时状态
        st.divider()
        st.markdown("### 🟢 系统状态")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("策略数", "6+")
        with col2:
            st.metric("数据源", "2")


def render_header(title: str, subtitle: str = ""):
    """渲染页面头部"""
    
    st.markdown(
        f"""
        <style>
            .page-header {{
                text-align: center;
                padding: 20px 0;
                margin-bottom: 30px;
            }}
            .page-title {{
                font-size: 2.5rem;
                font-weight: bold;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 10px;
            }}
            .page-subtitle {{
                font-size: 1.2rem;
                color: #666;
            }}
        </style>
        <div class="page-header">
            <div class="page-title">{title}</div>
            <div class="page-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_breadcrumb(pages: list):
    """渲染面包屑导航"""
    
    breadcrumb_html = '<div style="margin-bottom: 20px; font-size: 0.9rem; color: #666;">'
    breadcrumb_html += ' > '.join(pages)
    breadcrumb_html += '</div>'
    
    st.markdown(breadcrumb_html, unsafe_allow_html=True)
