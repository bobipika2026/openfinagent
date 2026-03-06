"""
策略创建页面 - 通过自然语言或参数配置创建策略
"""

import streamlit as st
from pathlib import Path
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def show():
    """显示策略创建页面"""
    
    st.markdown('<p class="main-header">✨ 创建策略</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">用自然语言描述你的交易想法，AI 自动生成策略</p>', unsafe_allow_html=True)
    
    st.divider()
    
    # 创建方式选择
    tab1, tab2 = st.tabs(["📝 自然语言创建", "⚙️ 参数配置"])
    
    with tab1:
        show_natural_language_creator()
    
    with tab2:
        show_parameter_creator()


def show_natural_language_creator():
    """自然语言策略创建器"""
    
    st.markdown("### 🗣️ 输入你的策略想法")
    
    st.markdown("""
    **提示**：用中文描述你的交易策略，包括：
    - 买入条件（例如：均线上穿、RSI 超卖等）
    - 卖出条件（例如：均线下穿、RSI 超买等）
    - 初始资金（可选，默认 10 万元）
    - 策略名称（可选）
    """)
    
    # 示例模板
    with st.expander("📋 查看示例模板", expanded=False):
        st.markdown("""
        **示例 1 - 均线交叉**：
        ```
        当 5 日均线上穿 20 日均线时买入
        当 5 日均线下穿 20 日均线时卖出
        初始资金 10 万元
        ```
        
        **示例 2 - RSI 策略**：
        ```
        当 RSI 低于 30 时买入（超卖）
        当 RSI 高于 70 时卖出（超买）
        RSI 周期 14 天
        初始资金 50 万元
        ```
        
        **示例 3 - 动量策略**：
        ```
        当 20 日收益率超过 5% 时买入
        当 20 日收益率低于 -5% 时卖出
        初始资金 100 万元
        ```
        """)
    
    # 自然语言输入框
    strategy_description = st.text_area(
        "策略描述",
        placeholder="请输入你的策略想法，例如：当 5 日均线上穿 20 日均线时买入，下穿时卖出，初始资金 10 万元",
        height=150,
        key="nl_description"
    )
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🔮 AI 解析并创建", use_container_width=True, type="primary"):
            if strategy_description.strip():
                try:
                    from src.strategy.builder import StrategyBuilder
                    
                    with st.spinner("正在解析策略描述..."):
                        strategy = StrategyBuilder.from_natural_language(strategy_description)
                    
                    st.success(f"✅ 策略创建成功：**{strategy.name}**")
                    
                    # 存储策略到 session
                    st.session_state['current_strategy'] = strategy
                    st.session_state['strategy_description'] = strategy_description
                    
                    # 显示策略预览
                    show_strategy_preview(strategy)
                    
                except Exception as e:
                    st.error(f"❌ 创建失败：{str(e)}")
                    st.info("💡 请检查描述格式，或切换到「参数配置」模式手动创建")
            else:
                st.warning("⚠️ 请输入策略描述")
    
    with col2:
        if st.button("🧹 清空重置", use_container_width=True):
            st.session_state.pop('current_strategy', None)
            st.session_state.pop('strategy_description', None)
            st.rerun()


def show_parameter_creator():
    """参数配置策略创建器"""
    
    st.markdown("### ⚙️ 选择策略类型并配置参数")
    
    # 策略类型选择
    strategy_types = {
        'ma_cross': '均线交叉策略',
        'momentum': '动量策略',
        'rsi': 'RSI 超买超卖策略',
        'macd': 'MACD 金叉死叉策略',
        'bollinger': '布林带策略',
        'dual_ma_volume': '双均线 + 成交量策略'
    }
    
    selected_type = st.selectbox(
        "策略类型",
        options=list(strategy_types.keys()),
        format_func=lambda x: strategy_types[x],
        key="strategy_type_select"
    )
    
    st.divider()
    
    # 根据策略类型显示不同参数
    if selected_type == 'ma_cross':
        params = show_ma_cross_params()
    elif selected_type == 'momentum':
        params = show_momentum_params()
    elif selected_type == 'rsi':
        params = show_rsi_params()
    elif selected_type == 'macd':
        params = show_macd_params()
    elif selected_type == 'bollinger':
        params = show_bollinger_params()
    elif selected_type == 'dual_ma_volume':
        params = show_dual_ma_volume_params()
    else:
        params = {}
    
    # 通用参数
    st.markdown("### 📊 通用设置")
    col1, col2 = st.columns(2)
    
    with col1:
        strategy_name = st.text_input("策略名称", value="", placeholder="留空自动生成")
    
    with col2:
        initial_capital = st.number_input(
            "初始资金 (元)",
            min_value=10000,
            max_value=10000000,
            value=100000,
            step=10000
        )
    
    params['name'] = strategy_name if strategy_name.strip() else None
    params['initial_capital'] = initial_capital
    
    st.divider()
    
    # 创建按钮
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("✅ 创建策略", use_container_width=True, type="primary"):
            try:
                from src.strategy.builder import StrategyBuilder
                
                with st.spinner("正在创建策略..."):
                    strategy = StrategyBuilder.create(selected_type, **params)
                
                st.success(f"✅ 策略创建成功：**{strategy.name}**")
                
                # 存储策略到 session
                st.session_state['current_strategy'] = strategy
                st.session_state['strategy_description'] = f"参数配置：{strategy_types[selected_type]}"
                
                # 显示策略预览
                show_strategy_preview(strategy)
                
            except Exception as e:
                st.error(f"❌ 创建失败：{str(e)}")
    
    with col2:
        if st.button("🧹 重置参数", use_container_width=True):
            st.rerun()


def show_ma_cross_params():
    """均线交叉策略参数"""
    st.markdown("#### 📈 均线参数")
    
    col1, col2 = st.columns(2)
    
    with col1:
        short_window = st.number_input(
            "短期均线周期",
            min_value=1,
            max_value=60,
            value=5,
            help="例如：5 日均线"
        )
    
    with col2:
        long_window = st.number_input(
            "长期均线周期",
            min_value=short_window + 1,
            max_value=250,
            value=20,
            help="例如：20 日均线"
        )
    
    return {'short_window': short_window, 'long_window': long_window}


def show_momentum_params():
    """动量策略参数"""
    st.markdown("#### 📈 动量参数")
    
    col1, col2 = st.columns(2)
    
    with col1:
        lookback_period = st.number_input(
            "回看周期 (天)",
            min_value=5,
            max_value=120,
            value=20
        )
    
    with col2:
        threshold = st.number_input(
            "收益率阈值 (%)",
            min_value=1.0,
            max_value=50.0,
            value=5.0,
            step=0.5
        ) / 100.0
    
    return {'lookback_period': lookback_period, 'threshold': threshold}


def show_rsi_params():
    """RSI 策略参数"""
    st.markdown("#### 📈 RSI 参数")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        period = st.number_input(
            "RSI 周期",
            min_value=5,
            max_value=30,
            value=14
        )
    
    with col2:
        oversold = st.number_input(
            "超卖线",
            min_value=10,
            max_value=40,
            value=30
        )
    
    with col3:
        overbought = st.number_input(
            "超买线",
            min_value=60,
            max_value=90,
            value=70
        )
    
    return {'period': period, 'oversold': oversold, 'overbought': overbought}


def show_macd_params():
    """MACD 策略参数"""
    st.markdown("#### 📈 MACD 参数")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fast_period = st.number_input(
            "快线周期",
            min_value=5,
            max_value=20,
            value=12
        )
    
    with col2:
        slow_period = st.number_input(
            "慢线周期",
            min_value=20,
            max_value=60,
            value=26
        )
    
    with col3:
        signal_period = st.number_input(
            "信号线周期",
            min_value=5,
            max_value=15,
            value=9
        )
    
    return {'fast_period': fast_period, 'slow_period': slow_period, 'signal_period': signal_period}


def show_bollinger_params():
    """布林带策略参数"""
    st.markdown("#### 📈 布林带参数")
    
    col1, col2 = st.columns(2)
    
    with col1:
        window = st.number_input(
            "周期",
            min_value=10,
            max_value=60,
            value=20
        )
    
    with col2:
        std_dev = st.number_input(
            "标准差倍数",
            min_value=1.0,
            max_value=3.0,
            value=2.0,
            step=0.1
        )
    
    return {'window': window, 'std_dev': std_dev}


def show_dual_ma_volume_params():
    """双均线 + 成交量策略参数"""
    st.markdown("#### 📈 双均线参数")
    
    col1, col2 = st.columns(2)
    
    with col1:
        short_window = st.number_input(
            "短期均线周期",
            min_value=1,
            max_value=60,
            value=5
        )
    
    with col2:
        long_window = st.number_input(
            "长期均线周期",
            min_value=short_window + 1,
            max_value=250,
            value=20
        )
    
    st.markdown("#### 📊 成交量参数")
    
    col3, col4 = st.columns(2)
    
    with col3:
        volume_ma_period = st.number_input(
            "成交量均线周期",
            min_value=5,
            max_value=60,
            value=20
        )
    
    with col4:
        volume_multiplier = st.number_input(
            "成交量倍数阈值",
            min_value=1.0,
            max_value=5.0,
            value=1.5,
            step=0.1
        )
    
    return {
        'short_window': short_window,
        'long_window': long_window,
        'volume_ma_period': volume_ma_period,
        'volume_multiplier': volume_multiplier
    }


def show_strategy_preview(strategy):
    """显示策略预览"""
    
    st.markdown("### 👁️ 策略预览")
    
    # 策略信息卡片
    with st.container():
        st.markdown(f"**策略名称**: {strategy.name}")
        st.markdown(f"**初始资金**: ¥{strategy.initial_capital:,.2f}")
        
        # 显示策略参数
        st.markdown("**策略参数**:")
        params = strategy.__dict__
        for key, value in params.items():
            if not key.startswith('_') and key not in ['name', 'initial_capital', 'cash', 'positions']:
                st.markdown(f"- {key}: {value}")
    
    # 下一步操作提示
    st.info("""
    💡 **下一步**：
    1. 切换到「回测分析」页面，选择股票和时间范围运行回测
    2. 或切换到「策略对比」页面，与其他策略进行对比
    """)
