"""
首页 - OpenFinAgent 项目介绍和快速入口
"""

import streamlit as st
from pathlib import Path
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def show():
    """显示首页内容"""
    
    # 主标题
    st.markdown('<p class="main-header">🚀 OpenFinAgent</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI 驱动的量化交易平台 - 让策略创作更简单</p>', unsafe_allow_html=True)
    
    st.divider()
    
    # 项目介绍
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 💡 平台特色")
        
        st.markdown("""
        **OpenFinAgent** 是一个强大的 AI 量化交易平台，支持：
        
        ✅ **自然语言创建策略** - 用中文描述你的交易想法，AI 自动生成策略代码
        
        ✅ **多策略支持** - 内置均线交叉、动量、RSI、MACD、布林带等多种经典策略
        
        ✅ **专业回测引擎** - 支持手续费、滑点等真实交易因素，提供详细绩效分析
        
        ✅ **可视化分析** - 权益曲线、回撤分析、交易分布、雷达图等多种图表
        
        ✅ **策略对比** - 同时对比多个策略表现，找到最优方案
        
        ✅ **A 股/美股数据** - 支持 Akshare（A 股）和 Yahoo Finance（美股）数据源
        """)
        
        st.info("💬 **示例**：*当 5 日均线上穿 20 日均线时买入，下穿时卖出，初始资金 10 万元*")
    
    with col2:
        st.markdown("### 🎯 快速开始")
        
        if st.button("✨ 创建第一个策略", use_container_width=True, type="primary"):
            st.switch_page("pages/create.py")
        
        if st.button("📈 运行回测", use_container_width=True):
            st.switch_page("pages/backtest.py")
        
        if st.button("⚖️ 策略对比", use_container_width=True):
            st.switch_page("pages/compare.py")
        
        st.divider()
        
        st.markdown("### 📚 可用策略")
        try:
            from src.strategy.builder import StrategyBuilder
            strategies = StrategyBuilder.list_strategies()
            
            strategy_names = {
                'ma_cross': '均线交叉',
                'momentum': '动量策略',
                'rsi': 'RSI 超买超卖',
                'macd': 'MACD 金叉死叉',
                'bollinger': '布林带',
                'dual_ma_volume': '双均线 + 成交量'
            }
            
            for strategy_id in strategies:
                name = strategy_names.get(strategy_id, strategy_id)
                st.markdown(f"• {name}")
        except Exception as e:
            st.markdown("• 加载中...")
    
    st.divider()
    
    # 示例策略展示
    st.markdown("### 🌟 示例策略展示")
    
    tab1, tab2, tab3 = st.tabs(["均线交叉策略", "动量策略", "RSI 策略"])
    
    with tab1:
        st.markdown("""
        **策略逻辑**：
        - 当短期均线上穿长期均线时 → 买入
        - 当短期均线下穿长期均线时 → 卖出
        
        **参数**：
        - 短期均线周期：5 日
        - 长期均线周期：20 日
        - 初始资金：10 万元
        
        **适用场景**：趋势明显的市场环境
        """)
    
    with tab2:
        st.markdown("""
        **策略逻辑**：
        - 当 N 日收益率超过阈值时 → 买入（追涨）
        - 当 N 日收益率低于负阈值时 → 卖出（杀跌）
        
        **参数**：
        - 回看周期：20 日
        - 收益率阈值：5%
        - 初始资金：10 万元
        
        **适用场景**：强势股跟踪
        """)
    
    with tab3:
        st.markdown("""
        **策略逻辑**：
        - 当 RSI < 30（超卖）时 → 买入
        - 当 RSI > 70（超买）时 → 卖出
        
        **参数**：
        - RSI 周期：14 日
        - 超卖线：30
        - 超买线：70
        - 初始资金：10 万元
        
        **适用场景**：震荡市、均值回归
        """)
    
    st.divider()
    
    # 底部信息
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("支持策略类型", "6+")
    
    with col2:
        st.metric("数据源", "A 股 / 美股")
    
    with col3:
        st.metric("回测指标", "10+")
