"""
卡片组件 - 信息展示卡片
"""

import streamlit as st
from typing import Optional


def render_metric_card(
    title: str,
    value: str,
    delta: Optional[str] = None,
    delta_color: str = "normal",
    icon: str = "📊"
):
    """渲染指标卡片"""
    
    col = st.columns(1)[0]
    
    with col:
        st.markdown(
            f"""
            <style>
                .metric-card {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 20px;
                    border-radius: 12px;
                    color: white;
                    text-align: center;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    transition: transform 0.3s ease;
                }}
                .metric-card:hover {{
                    transform: translateY(-5px);
                }}
                .metric-icon {{
                    font-size: 2rem;
                    margin-bottom: 10px;
                }}
                .metric-title {{
                    font-size: 0.9rem;
                    opacity: 0.9;
                    margin-bottom: 5px;
                }}
                .metric-value {{
                    font-size: 2rem;
                    font-weight: bold;
                    margin: 10px 0;
                }}
                .metric-delta {{
                    font-size: 0.85rem;
                    opacity: 0.8;
                }}
            </style>
            <div class="metric-card">
                <div class="metric-icon">{icon}</div>
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
                {f'<div class="metric-delta">{delta}</div>' if delta else ''}
            </div>
            """,
            unsafe_allow_html=True
        )


def render_info_card(
    title: str,
    content: str,
    icon: str = "ℹ️",
    color: str = "blue"
):
    """渲染信息卡片"""
    
    color_map = {
        "blue": "#667eea",
        "green": "#28a745",
        "red": "#dc3545",
        "yellow": "#ffc107",
        "purple": "#764ba2"
    }
    
    bg_color = color_map.get(color, color_map["blue"])
    
    st.markdown(
        f"""
        <style>
            .info-card {{
                background: linear-gradient(135deg, {bg_color} 0%, {bg_color}cc 100%);
                padding: 20px;
                border-radius: 12px;
                color: white;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .info-card-title {{
                font-size: 1.2rem;
                font-weight: bold;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            .info-card-content {{
                font-size: 0.95rem;
                line-height: 1.6;
            }}
        </style>
        <div class="info-card">
            <div class="info-card-title">
                <span>{icon}</span>
                <span>{title}</span>
            </div>
            <div class="info-card-content">
                {content}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_strategy_card(
    name: str,
    description: str,
    params: dict,
    on_select=None
):
    """渲染策略卡片"""
    
    st.markdown(
        f"""
        <style>
            .strategy-card {{
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                padding: 20px;
                margin: 10px 0;
                transition: all 0.3s ease;
                cursor: pointer;
            }}
            .strategy-card:hover {{
                border-color: #667eea;
                box-shadow: 0 6px 12px rgba(102, 126, 234, 0.2);
                transform: translateY(-2px);
            }}
            .strategy-name {{
                font-size: 1.3rem;
                font-weight: bold;
                color: #333;
                margin-bottom: 10px;
            }}
            .strategy-description {{
                font-size: 0.9rem;
                color: #666;
                margin-bottom: 15px;
                line-height: 1.5;
            }}
            .strategy-params {{
                font-size: 0.85rem;
                color: #888;
                background: #f8f9fa;
                padding: 10px;
                border-radius: 6px;
            }}
        </style>
        <div class="strategy-card">
            <div class="strategy-name">📈 {name}</div>
            <div class="strategy-description">{description}</div>
            <div class="strategy-params">
                <strong>参数:</strong><br>
                {'<br>'.join([f"• {k}: {v}" for k, v in params.items()])}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if on_select:
        if st.button("选择此策略", key=f"select_{name}", use_container_width=True):
            on_select(name, params)


def render_feature_card(
    icon: str,
    title: str,
    description: str,
    features: list
):
    """渲染功能卡片"""
    
    features_html = ''.join([f"<li>{f}</li>" for f in features])
    
    st.markdown(
        f"""
        <style>
            .feature-card {{
                background: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease;
                height: 100%;
            }}
            .feature-card:hover {{
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
                transform: translateY(-3px);
            }}
            .feature-icon {{
                font-size: 2.5rem;
                margin-bottom: 15px;
            }}
            .feature-title {{
                font-size: 1.3rem;
                font-weight: bold;
                color: #333;
                margin-bottom: 10px;
            }}
            .feature-description {{
                font-size: 0.95rem;
                color: #666;
                margin-bottom: 15px;
                line-height: 1.6;
            }}
            .feature-list {{
                list-style: none;
                padding: 0;
                margin: 0;
            }}
            .feature-list li {{
                padding: 5px 0;
                color: #555;
                font-size: 0.9rem;
            }}
            .feature-list li:before {{
                content: "✓ ";
                color: #28a745;
                font-weight: bold;
            }}
        </style>
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <div class="feature-title">{title}</div>
            <div class="feature-description">{description}</div>
            <ul class="feature-list">
                {features_html}
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_stat_card(
    label: str,
    value: str,
    trend: Optional[str] = None,
    trend_up: bool = True
):
    """渲染统计卡片"""
    
    trend_color = "#28a745" if trend_up else "#dc3545"
    trend_icon = "↑" if trend_up else "↓"
    
    st.markdown(
        f"""
        <style>
            .stat-card {{
                text-align: center;
                padding: 20px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }}
            .stat-label {{
                font-size: 0.9rem;
                color: #666;
                margin-bottom: 10px;
            }}
            .stat-value {{
                font-size: 2rem;
                font-weight: bold;
                color: #333;
                margin-bottom: 5px;
            }}
            .stat-trend {{
                font-size: 0.85rem;
                color: {trend_color};
                font-weight: bold;
            }}
        </style>
        <div class="stat-card">
            <div class="stat-label">{label}</div>
            <div class="stat-value">{value}</div>
            {f'<div class="stat-trend">{trend_icon} {trend}</div>' if trend else ''}
        </div>
        """,
        unsafe_allow_html=True
    )
