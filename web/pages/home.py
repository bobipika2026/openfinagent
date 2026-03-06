"""
首页 - OpenFinAgent 项目介绍和快速入口 (增强版)
"""

import streamlit as st
from pathlib import Path
import sys
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入自定义组件
from components import render_feature_card, render_stat_card, render_info_card


def show():
    """显示首页内容"""
    
    # 页面加载时间
    load_time = datetime.now()
    st.session_state.page_load_time = load_time
    
    # 主标题 (已在 app.py 中渲染)
    
    # 快速操作按钮
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("✨ 创建第一个策略", use_container_width=True, type="primary", key="home_create"):
            st.query_params["page"] = "create"
            st.rerun()
    
    with col2:
        if st.button("📈 运行回测", use_container_width=True, key="home_backtest"):
            st.query_params["page"] = "backtest"
            st.rerun()
    
    with col3:
        if st.button("⚖️ 策略对比", use_container_width=True, key="home_compare"):
            st.query_params["page"] = "compare"
            st.rerun()
    
    st.divider()
    
    # 平台特色
    st.markdown("### 💡 平台特色")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_feature_card(
            icon="🤖",
            title="AI 智能创作",
            description="用自然语言描述交易想法，AI 自动生成策略代码",
            features=[
                "自然语言理解",
                "自动代码生成",
                "智能参数优化"
            ]
        )
    
    with col2:
        render_feature_card(
            icon="📊",
            title="专业回测引擎",
            description="支持手续费、滑点等真实交易因素",
            features=[
                "高精度回测",
                "多数据源支持",
                "详细绩效分析"
            ]
        )
    
    with col3:
        render_feature_card(
            icon="📈",
            title="可视化分析",
            description="丰富的图表展示策略表现",
            features=[
                "权益曲线",
                "回撤分析",
                "指标雷达图"
            ]
        )
    
    st.divider()
    
    # 实时数据展示
    st.markdown("### 📊 实时市场概览")
    
    # 模拟实时数据 (实际应用中应连接真实数据源)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_stat_card(
            label="上证指数",
            value="3,245.67",
            trend="0.52%",
            trend_up=True
        )
    
    with col2:
        render_stat_card(
            label="深证成指",
            value="10,234.89",
            trend="0.38%",
            trend_up=True
        )
    
    with col3:
        render_stat_card(
            label="创业板指",
            value="2,156.43",
            trend="-0.21%",
            trend_up=False
        )
    
    with col4:
        render_stat_card(
            label="活跃策略数",
            value="127",
            trend="今日 +12",
            trend_up=True
        )
    
    # 刷新按钮
    if st.button("🔄 刷新数据", key="refresh_market"):
        st.rerun()
    
    st.divider()
    
    # 可用策略展示
    st.markdown("### 📚 策略模板库")
    
    strategy_templates = {
        "均线交叉": {
            "description": "经典的趋势跟踪策略，当短期均线上穿长期均线时买入",
            "params": {"短期均线": "5 日", "长期均线": "20 日", "初始资金": "10 万元"},
            "difficulty": "⭐⭐",
            "icon": "📈"
        },
        "RSI 超买超卖": {
            "description": "基于 RSI 指标的均值回归策略，超卖买入，超买卖出",
            "params": {"RSI 周期": "14 日", "超卖线": "30", "超买线": "70"},
            "difficulty": "⭐⭐",
            "icon": "📊"
        },
        "MACD 金叉死叉": {
            "description": "利用 MACD 指标的金叉死叉信号进行交易",
            "params": {"快线": "12", "慢线": "26", "信号线": "9"},
            "difficulty": "⭐⭐⭐",
            "icon": "🎯"
        },
        "布林带策略": {
            "description": "基于布林带上下轨的突破或反转策略",
            "params": {"周期": "20 日", "标准差": "2.0"},
            "difficulty": "⭐⭐⭐",
            "icon": "📉"
        },
        "动量策略": {
            "description": "追涨杀跌的动量策略，捕捉强势股",
            "params": {"回看周期": "20 日", "收益率阈值": "5%"},
            "difficulty": "⭐⭐",
            "icon": "🚀"
        },
        "双均线 + 成交量": {
            "description": "结合均线和成交量的复合策略",
            "params": {"短均线": "5 日", "长均线": "20 日", "成交量倍数": "1.5"},
            "difficulty": "⭐⭐⭐⭐",
            "icon": "💹"
        }
    }
    
    # 策略选择
    selected_strategy = st.selectbox(
        "选择策略模板查看详情",
        list(strategy_templates.keys()),
        key="strategy_select"
    )
    
    if selected_strategy:
        template = strategy_templates[selected_strategy]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"#### {template['icon']} {selected_strategy}")
            st.markdown(template["description"])
            
            st.markdown("**默认参数:**")
            params_text = "\n".join([f"- {k}: {v}" for k, v in template["params"].items()])
            st.markdown(params_text)
        
        with col2:
            st.markdown("**难度等级:**")
            st.markdown(template["difficulty"])
            
            if st.button("使用此模板", key=f"use_{selected_strategy}", use_container_width=True):
                # 存储策略模板信息到 session
                st.session_state.selected_template = selected_strategy
                st.session_state.template_params = template["params"]
                st.query_params["page"] = "create"
                st.rerun()
    
    st.divider()
    
    # 示例策略展示
    st.markdown("### 🌟 示例策略展示")
    
    tab1, tab2, tab3 = st.tabs(["均线交叉策略", "动量策略", "RSI 策略"])
    
    with tab1:
        st.markdown("""
        **策略逻辑**:
        - 当短期均线上穿长期均线时 → 买入
        - 当短期均线下穿长期均线时 → 卖出
        
        **参数**:
        - 短期均线周期：5 日
        - 长期均线周期：20 日
        - 初始资金：10 万元
        
        **适用场景**: 趋势明显的市场环境
        
        **风险提示**: 震荡市可能频繁止损
        """)
    
    with tab2:
        st.markdown("""
        **策略逻辑**:
        - 当 N 日收益率超过阈值时 → 买入 (追涨)
        - 当 N 日收益率低于负阈值时 → 卖出 (杀跌)
        
        **参数**:
        - 回看周期：20 日
        - 收益率阈值：5%
        - 初始资金：10 万元
        
        **适用场景**: 强势股跟踪
        
        **风险提示**: 高位接盘风险
        """)
    
    with tab3:
        st.markdown("""
        **策略逻辑**:
        - 当 RSI < 30 (超卖) 时 → 买入
        - 当 RSI > 70 (超买) 时 → 卖出
        
        **参数**:
        - RSI 周期：14 日
        - 超卖线：30
        - 超买线：70
        - 初始资金：10 万元
        
        **适用场景**: 震荡市、均值回归
        
        **风险提示**: 单边行情可能持续超买/超卖
        """)
    
    st.divider()
    
    # 平台统计
    st.markdown("### 📈 平台统计")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("支持策略类型", "6+")
    
    with col2:
        st.metric("数据源", "A 股 / 美股")
    
    with col3:
        st.metric("回测指标", "10+")
    
    with col4:
        st.metric("图表类型", "5+")
    
    st.divider()
    
    # 快速入门指南
    render_info_card(
        title="💡 快速入门指南",
        content="""
        **第一步**: 在「创建策略」页面选择策略模板或用自然语言描述你的策略想法
        
        **第二步**: 在「回测分析」页面选择股票和时间范围，运行回测
        
        **第三步**: 在「策略对比」页面比较不同策略的表现，找到最优方案
        
        **提示**: 建议先用模拟数据测试，熟悉后再使用真实数据回测
        """,
        icon="🚀",
        color="blue"
    )


def show_quick_start():
    """显示快速入门向导"""
    st.markdown("### 🎯 快速开始")
    
    steps = [
        {"icon": "1️⃣", "title": "创建策略", "desc": "选择模板或自然语言描述"},
        {"icon": "2️⃣", "title": "配置参数", "desc": "设置股票和时间范围"},
        {"icon": "3️⃣", "title": "运行回测", "desc": "查看策略表现"},
        {"icon": "4️⃣", "title": "优化迭代", "desc": "调整参数持续改进"}
    ]
    
    cols = st.columns(4)
    for i, step in enumerate(steps):
        with cols[i]:
            st.markdown(f"**{step['icon']} {step['title']}**")
            st.markdown(step["desc"])
