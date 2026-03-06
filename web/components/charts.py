"""
图表组件 - 增强的可视化
"""

import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any


def create_equity_chart(
    equity_data: pd.DataFrame,
    title: str = "权益曲线",
    height: int = 400,
    show_initial: bool = True,
    initial_value: float = None
):
    """创建权益曲线图"""
    try:
        import plotly.graph_objects as go
        
        fig = go.Figure()
        
        # 权益曲线
        fig.add_trace(go.Scatter(
            x=equity_data.index if hasattr(equity_data.index, 'strftime') else range(len(equity_data)),
            y=equity_data['equity'] if 'equity' in equity_data.columns else equity_data.iloc[:, 0],
            mode='lines',
            name='权益',
            line=dict(color='#2E86AB', width=3),
            hovertemplate='<b>%{x}</b><br>权益：¥%{y:,.2f}<extra></extra>'
        ))
        
        # 初始资金线
        if show_initial and initial_value:
            fig.add_trace(go.Scatter(
                x=equity_data.index if hasattr(equity_data.index, 'strftime') else range(len(equity_data)),
                y=[initial_value] * len(equity_data),
                mode='lines',
                name='初始资金',
                line=dict(color='gray', width=2, dash='dash'),
                hovertemplate='初始资金：¥%{y:,.2f}<extra></extra>'
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title='日期',
            yaxis_title='资金 (元)',
            hovermode='x unified',
            height=height,
            template='plotly_white',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    except Exception as e:
        st.error(f"图表渲染失败：{e}")
        return None


def create_drawdown_chart(
    equity_data: pd.DataFrame,
    title: str = "回撤分析",
    height: int = 400
):
    """创建回撤图"""
    try:
        import plotly.graph_objects as go
        
        # 计算回撤
        if 'equity' in equity_data.columns:
            equity = equity_data['equity']
        else:
            equity = equity_data.iloc[:, 0]
        
        peak = equity.cummax()
        drawdown = (equity - peak) / peak * 100
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=equity_data.index if hasattr(equity_data.index, 'strftime') else range(len(equity_data)),
            y=drawdown,
            mode='lines',
            name='回撤',
            line=dict(color='#E63946', width=2),
            fill='tozeroy',
            hovertemplate='<b>%{x}</b><br>回撤：%{y:.2f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='日期',
            yaxis_title='回撤 (%)',
            hovermode='x unified',
            height=height,
            template='plotly_white'
        )
        
        return fig
    
    except Exception as e:
        st.error(f"图表渲染失败：{e}")
        return None


def create_radar_chart(
    metrics: Dict[str, float],
    title: str = "策略指标雷达图",
    height: int = 500
):
    """创建雷达图"""
    try:
        import plotly.graph_objects as go
        import numpy as np
        
        # 选择关键指标
        categories = list(metrics.keys())[:6]  # 最多 6 个指标
        values = [metrics[cat] for cat in categories]
        
        # 归一化到 0-1
        normalized_values = []
        for val in values:
            if abs(val) > 100:
                normalized_values.append(min(max(val / 100, 0), 1))
            elif abs(val) > 10:
                normalized_values.append(min(max(val / 10, 0), 1))
            else:
                normalized_values.append(min(max(val, 0), 1))
        
        # 闭合雷达图
        normalized_values += normalized_values[:1]
        categories += categories[:1]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=normalized_values,
            theta=categories,
            fill='toself',
            name='策略指标',
            line=dict(color='#2E86AB', width=2),
            fillcolor='rgba(46, 134, 171, 0.25)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=False,
            title=title,
            height=height
        )
        
        return fig
    
    except Exception as e:
        st.error(f"图表渲染失败：{e}")
        return None


def create_kline_chart(
    data: pd.DataFrame,
    title: str = "K 线图",
    height: int = 600
):
    """创建 K 线图（蜡烛图）"""
    try:
        import plotly.graph_objects as go
        
        # 检查必要列
        required_cols = ['open', 'high', 'low', 'close']
        if not all(col in data.columns for col in required_cols):
            st.warning("数据缺少必要的 OHLC 列")
            return None
        
        fig = go.Figure()
        
        # K 线图
        fig.add_trace(go.Candlestick(
            x=data.index if hasattr(data.index, 'strftime') else range(len(data)),
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            name='K 线',
            increasing_line_color='#26A69A',
            decreasing_line_color='#EF5350'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='日期',
            yaxis_title='价格',
            height=height,
            template='plotly_white',
            xaxis_rangeslider_visible=False
        )
        
        return fig
    
    except Exception as e:
        st.error(f"图表渲染失败：{e}")
        return None


def create_bar_chart(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str = "柱状图",
    height: int = 400,
    color: str = '#667eea'
):
    """创建柱状图"""
    try:
        import plotly.graph_objects as go
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=data[x_col],
            y=data[y_col],
            name=y_col,
            marker_color=color
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title=x_col,
            yaxis_title=y_col,
            height=height,
            template='plotly_white'
        )
        
        return fig
    
    except Exception as e:
        st.error(f"图表渲染失败：{e}")
        return None


def create_comparison_chart(
    data_dict: Dict[str, pd.DataFrame],
    value_col: str,
    title: str = "对比图",
    height: int = 500
):
    """创建多系列对比图"""
    try:
        import plotly.graph_objects as go
        
        fig = go.Figure()
        
        colors = ['#2E86AB', '#E63946', '#2A9D8F', '#F4A261', '#8338EC', '#3A86FF']
        
        for i, (name, data) in enumerate(data_dict.items()):
            color = colors[i % len(colors)]
            
            fig.add_trace(go.Scatter(
                x=data.index if hasattr(data.index, 'strftime') else range(len(data)),
                y=data[value_col] if value_col in data.columns else data.iloc[:, 0],
                mode='lines',
                name=name,
                line=dict(color=color, width=2),
                hovertemplate='<b>%{fullData.name}</b><br>%{x}<br>%{y:.2f}<extra></extra>'
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title='日期',
            yaxis_title=value_col,
            hovermode='x unified',
            height=height,
            template='plotly_white',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    except Exception as e:
        st.error(f"图表渲染失败：{e}")
        return None


def export_chart_to_image(fig, filename: str = "chart.png"):
    """导出图表为图片"""
    try:
        fig.write_image(filename)
        return filename
    except Exception as e:
        st.error(f"导出失败：{e}")
        return None


def export_chart_to_pdf(fig, filename: str = "chart.pdf"):
    """导出图表为 PDF"""
    try:
        fig.write_image(filename, format="pdf")
        return filename
    except Exception as e:
        st.error(f"导出失败：{e}")
        return None
