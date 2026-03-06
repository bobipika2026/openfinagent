"""
OpenFinAgent Web UI - 主应用入口 (增强版 v0.3.2)
AI 量化交易平台

功能增强:
- ✅ 主题切换 (深色/浅色)
- ✅ 加载动画
- ✅ 优化侧边栏导航
- ✅ 响应式布局
- ✅ 数据缓存
- ✅ 实时数据展示
- ✅ 策略模板库
- ✅ 回测结果导出
"""

import streamlit as st
from pathlib import Path
import sys
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入自定义组件和工具
from components import render_sidebar, render_header, show_page_loader
from utils import get_theme_css, get_theme_config


# ==================== 页面配置 ====================
st.set_page_config(
    page_title="OpenFinAgent - AI 量化交易平台",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/bobipika2026/openfinagent',
        'Report a bug': 'https://github.com/bobipika2026/openfinagent/issues',
        'About': "# OpenFinAgent v0.3.2\nAI 驱动的量化交易平台"
    }
)


# ==================== 初始化 Session State ====================
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

if 'page_load_time' not in st.session_state:
    st.session_state.page_load_time = datetime.now()


# ==================== 应用主题样式 ====================
st.markdown(get_theme_css(), unsafe_allow_html=True)

# 全局样式优化
st.markdown(
    """
    <style>
        /* 响应式布局优化 */
        @media (max-width: 768px) {
            .main-header { font-size: 1.8rem !important; }
            .sub-header { font-size: 1rem !important; }
        }
        
        /* 平滑滚动 */
        html {
            scroll-behavior: smooth;
        }
        
        /* 自定义滚动条 */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }
        ::-webkit-scrollbar-thumb {
            background: #667eea;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #764ba2;
        }
        
        /* 主标题样式 */
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-align: center;
            margin-bottom: 1rem;
        }
        
        /* 副标题样式 */
        .sub-header {
            font-size: 1.2rem;
            color: #666;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        /* 指标卡片 */
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 12px;
            color: white;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        }
        
        /* 按钮样式优化 */
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            font-weight: bold;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
        }
        
        /* 容器圆角 */
        .stApp div[data-testid="stVerticalBlock"] > div {
            border-radius: 8px;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ==================== 侧边栏 ====================
render_sidebar()


# ==================== 页面路由 ====================
def main():
    """主应用逻辑"""
    
    # 获取当前页面
    page = st.query_params.get("page", "home")
    
    # 页面映射
    pages = {
        "home": ("🏠 首页", "pages.home"),
        "create": ("✨ 创建策略", "pages.create"),
        "backtest": ("📈 回测分析", "pages.backtest"),
        "compare": ("⚖️ 策略对比", "pages.compare"),
        "templates": ("📚 策略模板", "pages.templates"),
        "monitor": ("📊 实时监控", "pages.monitor"),
    }
    
    # 获取当前页面信息
    page_info = pages.get(page, pages["home"])
    page_name, page_module = page_info
    
    # 显示页面头部
    render_header(page_name, "AI 驱动的量化交易平台")
    
    # 加载页面内容
    try:
        if page == "home":
            from pages import home
            home.show()
        elif page == "create":
            from pages import create
            create.show()
        elif page == "backtest":
            from pages import backtest
            backtest.show()
        elif page == "compare":
            from pages import compare
            compare.show()
        elif page == "templates":
            from pages import templates
            templates.show()
        elif page == "monitor":
            from pages import monitor
            monitor.show()
        else:
            from pages import home
            home.show()
    except ImportError as e:
        st.error(f"❌ 页面加载失败：{e}")
        st.info("💡 请确保页面文件存在")
        
        # 返回首页按钮
        if st.button("🏠 返回首页"):
            st.query_params["page"] = "home"
            st.rerun()


# ==================== 页脚 ====================
def render_footer():
    """渲染页脚"""
    st.markdown(
        """
        <style>
            .footer {
                text-align: center;
                padding: 20px;
                margin-top: 50px;
                border-top: 1px solid #e0e0e0;
                color: #666;
                font-size: 0.85rem;
            }
        </style>
        <div class="footer">
            <div>OpenFinAgent v0.3.2 | AI 量化交易平台</div>
            <div style="margin-top: 5px;">
                © 2026 OpenFinAgent | 
                <a href="https://github.com/bobipika2026/openfinagent" target="_blank">GitHub</a> | 
                <a href="https://github.com/bobipika2026/openfinagent/issues" target="_blank">问题反馈</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ==================== 运行应用 ====================
if __name__ == "__main__":
    main()
    render_footer()
