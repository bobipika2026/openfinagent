"""
加载动画组件
"""

import streamlit as st
import time


def show_loading_spinner(message: str = "加载中...", duration: float = None):
    """显示加载旋转器"""
    with st.spinner(message):
        if duration:
            time.sleep(duration)
        yield


def show_progress_bar(message: str = "处理中...", progress: float = 0):
    """显示进度条"""
    progress_bar = st.progress(progress)
    if progress < 1.0:
        return progress_bar
    else:
        progress_bar.empty()


def show_skeleton_loader(lines: int = 3):
    """显示骨架屏"""
    for _ in range(lines):
        st.markdown(
            """
            <style>
                @keyframes shimmer {
                    0% { background-position: -1000px 0; }
                    100% { background-position: 1000px 0; }
                }
                .skeleton {
                    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                    background-size: 1000px 100%;
                    animation: shimmer 2s infinite linear;
                    border-radius: 4px;
                    height: 20px;
                    margin: 8px 0;
                }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.markdown('<div class="skeleton"></div>', unsafe_allow_html=True)


def show_page_loader():
    """显示页面加载动画"""
    st.markdown(
        """
        <style>
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            @keyframes bounce {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-10px); }
            }
            .loader-container {
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 50px;
            }
            .loader-dots {
                display: flex;
                gap: 10px;
            }
            .loader-dot {
                width: 20px;
                height: 20px;
                border-radius: 50%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                animation: bounce 1.4s infinite ease-in-out both;
            }
            .loader-dot:nth-child(1) { animation-delay: -0.32s; }
            .loader-dot:nth-child(2) { animation-delay: -0.16s; }
            .loader-text {
                text-align: center;
                margin-top: 20px;
                color: #667eea;
                font-size: 1.2rem;
                animation: pulse 2s infinite;
            }
        </style>
        <div class="loader-container">
            <div>
                <div class="loader-dots">
                    <div class="loader-dot"></div>
                    <div class="loader-dot"></div>
                    <div class="loader-dot"></div>
                </div>
                <div class="loader-text">正在加载...</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def show_chart_loader():
    """显示图表加载动画"""
    st.markdown(
        """
        <style>
            @keyframes chart-loading {
                0% { transform: scaleY(0.1); opacity: 0; }
                50% { opacity: 1; }
                100% { transform: scaleY(1); opacity: 0; }
            }
            .chart-loader {
                display: flex;
                justify-content: center;
                align-items: flex-end;
                height: 100px;
                gap: 5px;
                padding: 20px;
            }
            .chart-bar {
                width: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 4px 4px 0 0;
                animation: chart-loading 1.5s infinite ease-in-out;
            }
            .chart-bar:nth-child(1) { height: 40px; animation-delay: 0s; }
            .chart-bar:nth-child(2) { height: 60px; animation-delay: 0.2s; }
            .chart-bar:nth-child(3) { height: 80px; animation-delay: 0.4s; }
            .chart-bar:nth-child(4) { height: 50px; animation-delay: 0.6s; }
            .chart-bar:nth-child(5) { height: 70px; animation-delay: 0.8s; }
        </style>
        <div class="chart-loader">
            <div class="chart-bar"></div>
            <div class="chart-bar"></div>
            <div class="chart-bar"></div>
            <div class="chart-bar"></div>
            <div class="chart-bar"></div>
        </div>
        """,
        unsafe_allow_html=True
    )


def show_data_loader():
    """显示数据加载动画"""
    st.markdown(
        """
        <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .data-loader {
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 40px;
            }
            .spinner {
                width: 50px;
                height: 50px;
                border: 5px solid #f3f3f3;
                border-top: 5px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
        </style>
        <div class="data-loader">
            <div class="spinner"></div>
        </div>
        """,
        unsafe_allow_html=True
    )
