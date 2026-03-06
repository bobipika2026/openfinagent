"""
主题管理 - 深色/浅色主题切换
"""

import streamlit as st


def get_theme_config():
    """获取当前主题配置"""
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    return st.session_state.theme


def set_theme(theme: str):
    """设置主题"""
    st.session_state.theme = theme


def toggle_theme():
    """切换主题"""
    current = get_theme_config()
    set_theme('dark' if current == 'light' else 'light')


def get_theme_css():
    """获取主题 CSS"""
    theme = get_theme_config()
    
    if theme == 'dark':
        return """
        <style>
            /* 深色主题 */
            .main {
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                color: #e0e0e0;
            }
            
            .stApp {
                background-color: #0f0f1a;
            }
            
            /* 侧边栏 */
            [data-testid="stSidebar"] {
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            }
            
            /* 卡片样式 */
            .metric-card {
                background: linear-gradient(135deg, #2d2d44 0%, #1a1a2e 100%);
                border: 1px solid #3d3d5c;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            }
            
            /* 按钮样式 */
            .stButton>button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                transition: all 0.3s ease;
            }
            
            .stButton>button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
            }
            
            /* 输入框 */
            .stTextInput>div>div>input,
            .stNumberInput>div>div>input,
            .stTextArea>div>div>textarea {
                background-color: #2d2d44;
                color: #e0e0e0;
                border: 1px solid #3d3d5c;
            }
            
            /* 下拉框 */
            .stSelectbox>div>div>select {
                background-color: #2d2d44;
                color: #e0e0e0;
            }
            
            /* 表格 */
            .dataframe {
                background-color: #1a1a2e;
                color: #e0e0e0;
            }
            
            .dataframe th {
                background-color: #2d2d44;
                color: #e0e0e0;
            }
            
            .dataframe td {
                border-color: #3d3d5c;
            }
            
            /* 警告框 */
            .stAlert {
                background-color: #2d2d44;
                border: 1px solid #3d3d5c;
            }
            
            /* 成功提示 */
            .stAlert[data-testid="stAlertSuccess"] {
                background-color: rgba(40, 167, 69, 0.2);
                border-color: #28a745;
            }
            
            /* 错误提示 */
            .stAlert[data-testid="stAlertError"] {
                background-color: rgba(220, 53, 69, 0.2);
                border-color: #dc3545;
            }
            
            /* 标签页 */
            .stTabs [data-baseweb="tab-list"] {
                background-color: #1a1a2e;
            }
            
            .stTabs [data-baseweb="tab"] {
                background-color: #2d2d44;
                color: #e0e0e0;
            }
            
            .stTabs [aria-selected="true"] {
                background-color: #667eea;
            }
            
            /* 进度条 */
            .stProgress > div > div > div > div {
                background-color: #667eea;
            }
            
            /* 分割线 */
            hr {
                border-color: #3d3d5c;
            }
            
            /* 链接 */
            a {
                color: #667eea;
            }
            
            /* 代码块 */
            pre {
                background-color: #0f0f1a;
                border: 1px solid #3d3d5c;
            }
            
            code {
                background-color: #2d2d44;
                color: #e0e0e0;
            }
        </style>
        """
    else:
        return """
        <style>
            /* 浅色主题 */
            .main {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            }
            
            /* 卡片样式 */
            .metric-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            
            /* 按钮样式 */
            .stButton>button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                transition: all 0.3s ease;
            }
            
            .stButton>button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
            }
            
            /* 进度条 */
            .stProgress > div > div > div > div {
                background-color: #667eea;
            }
        </style>
        """


def render_theme_toggle():
    """渲染主题切换按钮"""
    from streamlit_javascript import st_javascript
    
    theme = get_theme_config()
    icon = "🌙" if theme == 'light' else "☀️"
    label = "切换到深色模式" if theme == 'light' else "切换到浅色模式"
    
    if st.button(f"{icon} {label}", key="theme_toggle", use_container_width=True):
        toggle_theme()
        st.rerun()
