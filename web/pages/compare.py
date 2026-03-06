"""
策略对比页面 - 对比多个策略的表现
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def show():
    """显示策略对比页面"""
    
    st.markdown('<p class="main-header">⚖️ 策略对比</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">同时对比多个策略的表现，找到最优方案</p>', unsafe_allow_html=True)
    
    st.divider()
    
    # 侧边栏配置
    with st.sidebar:
        st.markdown("### 🎛️ 对比配置")
        
        # 数据源选择
        data_source = st.selectbox(
            "数据源",
            options=['akshare', 'mock'],
            format_func=lambda x: 'A 股 (Akshare)' if x == 'akshare' else '模拟数据 (测试用)',
            help="A 股数据使用 Akshare，测试可用模拟数据"
        )
        
        # 股票代码输入
        if data_source == 'akshare':
            symbol = st.text_input(
                "股票代码",
                value="000001",
                placeholder="例如：000001 (平安银行)",
                help="输入 6 位股票代码，无需后缀"
            )
        else:
            symbol = "MOCK"
        
        # 时间范围
        st.markdown("#### 📅 时间范围")
        
        end_date = st.date_input("结束日期", value=datetime.now().date())
        start_date = st.date_input(
            "开始日期",
            value=end_date - timedelta(days=365),
            max_value=end_date
        )
        
        st.divider()
        
        # 运行对比按钮
        run_button = st.button("▶️ 运行对比", use_container_width=True, type="primary")
    
    # 主内容区
    if run_button:
        run_comparison(
            symbol=symbol,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            data_source=data_source
        )
    else:
        # 显示提示信息
        show_comparison_info()


def show_comparison_info():
    """显示对比说明信息"""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📚 对比说明")
        
        st.markdown("""
        **对比流程**：
        
        1. **选择股票** - 输入 6 位股票代码
        2. **设置时间范围** - 选择对比的起止日期
        3. **选择策略** - 从预设策略中选择要对比的策略
        4. **运行对比** - 点击运行按钮，查看对比结果
        
        **对比维度**：
        
        - 归一化权益曲线对比
        - 收益指标对比（总收益、年化收益）
        - 风险指标对比（最大回撤、夏普比率）
        - 交易统计对比（交易次数、胜率）
        
        **如何解读**：
        
        - 权益曲线越陡峭越好（收益高）
        - 曲线越平滑越好（波动小）
        - 回撤越小越好（风险低）
        - 夏普比率越高越好（风险调整后收益高）
        """)
    
    with col2:
        st.markdown("### 💡 小贴士")
        
        st.info("""
        - 建议选择 3-5 个策略进行对比，太多会影响可读性
        - 相同市场环境下对比更有意义
        - 关注风险调整后收益（夏普比率）
        - 回测结果不代表未来表现
        """)


def run_comparison(symbol, start_date, end_date, data_source):
    """运行策略对比"""
    
    try:
        from src.backtest.engine import BacktestEngine, load_data
        from src.strategy.builder import StrategyBuilder
        
        # 加载数据
        with st.spinner(f"📊 正在加载 {symbol} 的数据..."):
            try:
                data = load_data(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date,
                    source=data_source
                )
                
                if data is None or len(data) == 0:
                    st.error("❌ 数据加载失败，请检查股票代码或时间范围")
                    return
                
                st.success(f"✅ 成功加载 {len(data)} 条数据")
                
            except Exception as e:
                st.error(f"❌ 数据加载失败：{str(e)}")
                st.info("💡 自动切换到模拟数据...")
                data = load_data(symbol, start_date, end_date, source='mock')
        
        # 选择要对比的策略
        st.markdown("### 🎯 选择对比策略")
        
        strategy_options = {
            'ma_cross_5_20': ('均线交叉 (5,20)', {'strategy_type': 'ma_cross', 'short_window': 5, 'long_window': 20}),
            'ma_cross_10_50': ('均线交叉 (10,50)', {'strategy_type': 'ma_cross', 'short_window': 10, 'long_window': 50}),
            'momentum_20_5': ('动量策略 (20 日，5%)', {'strategy_type': 'momentum', 'lookback_period': 20, 'threshold': 0.05}),
            'rsi_14_30_70': ('RSI 策略 (14,30,70)', {'strategy_type': 'rsi', 'period': 14, 'oversold': 30, 'overbought': 70}),
            'macd_12_26_9': ('MACD 策略 (12,26,9)', {'strategy_type': 'macd', 'fast_period': 12, 'slow_period': 26, 'signal_period': 9}),
            'bollinger_20_2': ('布林带 (20,2)', {'strategy_type': 'bollinger', 'window': 20, 'std_dev': 2.0}),
            'dual_ma_vol': ('双均线 + 成交量', {'strategy_type': 'dual_ma_volume', 'short_window': 5, 'long_window': 20, 'volume_ma_period': 20, 'volume_multiplier': 1.5})
        }
        
        selected_strategies = st.multiselect(
            "选择要对比的策略（至少 2 个，最多 5 个）",
            options=list(strategy_options.keys()),
            format_func=lambda x: strategy_options[x][0],
            default=['ma_cross_5_20', 'rsi_14_30_70', 'momentum_20_5'],
            max_selections=5,
            min_selections=2
        )
        
        if len(selected_strategies) < 2:
            st.warning("⚠️ 请至少选择 2 个策略")
            st.stop()
        
        # 创建策略实例
        strategies = []
        for key in selected_strategies:
            name, params = strategy_options[key]
            try:
                strategy = StrategyBuilder.create(
                    params['strategy_type'],
                    **{k: v for k, v in params.items() if k != 'strategy_type'}
                )
                strategies.append(strategy)
            except Exception as e:
                st.warning(f"⚠️ 策略 {name} 创建失败：{e}")
        
        if len(strategies) < 2:
            st.error("❌ 成功创建的策略不足 2 个，无法对比")
            st.stop()
        
        # 运行回测对比
        with st.spinner("🔄 正在运行多策略回测..."):
            engine = BacktestEngine(commission_rate=0.0003, slippage=0.001)
            
            results_dict = {}
            progress_bar = st.progress(0)
            
            for i, strategy in enumerate(strategies):
                try:
                    results = engine.run(strategy, data, show_progress=False)
                    results_dict[strategy.name] = results
                    progress_bar.progress((i + 1) / len(strategies))
                except Exception as e:
                    st.warning(f"⚠️ 策略 {strategy.name} 回测失败：{e}")
            
            progress_bar.empty()
        
        if len(results_dict) < 2:
            st.error("❌ 成功回测的策略不足 2 个，无法对比")
            st.stop()
        
        st.success(f"✅ 完成 {len(results_dict)} 个策略的回测对比！")
        
        # 存储结果
        st.session_state['comparison_results'] = results_dict
        st.session_state['comparison_data'] = data
        
        # 展示对比结果
        display_comparison_results(results_dict, data)
        
    except Exception as e:
        st.error(f"❌ 对比失败：{str(e)}")
        import traceback
        st.code(traceback.format_exc())


def display_comparison_results(results_dict, data):
    """展示策略对比结果"""
    
    results_list = list(results_dict.values())
    
    # 1. 归一化权益曲线对比
    st.markdown("### 📈 权益曲线对比")
    
    show_comparison_chart(results_list)
    
    st.divider()
    
    # 2. 性能指标对比表格
    st.markdown("### 📊 性能指标对比")
    
    show_metrics_table(results_dict)
    
    st.divider()
    
    # 3. 详细对比分析
    st.markdown("### 🔍 详细分析")
    
    tabs = st.tabs(["收益对比", "风险对比", "交易统计"])
    
    with tabs[0]:
        show_return_comparison(results_dict)
    
    with tabs[1]:
        show_risk_comparison(results_dict)
    
    with tabs[2]:
        show_trading_comparison(results_dict)


def show_comparison_chart(results_list):
    """显示对比图表"""
    
    try:
        import plotly.graph_objects as go
        
        fig = go.Figure()
        
        colors = ['#2E86AB', '#E63946', '#2A9D8F', '#F4A261', '#8338EC']
        
        for i, results in enumerate(results_list):
            if not results.equity_curve:
                continue
            
            equity_df = pd.DataFrame(results.equity_curve)
            equity_df.set_index('timestamp', inplace=True)
            
            # 归一化到 100
            normalized = equity_df['equity'] / results.initial_capital * 100
            
            color = colors[i % len(colors)]
            
            fig.add_trace(go.Scatter(
                x=normalized.index,
                y=normalized,
                mode='lines',
                name=results.strategy_name,
                line=dict(color=color, width=2)
            ))
        
        fig.update_layout(
            title='策略归一化权益曲线对比',
            xaxis_title='日期',
            yaxis_title='归一化净值 (基准=100)',
            hovermode='x unified',
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"图表渲染失败：{e}")


def show_metrics_table(results_dict):
    """显示指标对比表格"""
    
    try:
        # 构建对比数据
        data = []
        
        for name, results in results_dict.items():
            metrics = results.metrics
            
            row = {
                '策略名称': name,
                '总收益 (%)': metrics.get('总收益 (%)', 0),
                '年化收益 (%)': metrics.get('年化收益 (%)', 0),
                '夏普比率': metrics.get('夏普比率', 0),
                '最大回撤 (%)': metrics.get('最大回撤 (%)', 0),
                '胜率 (%)': metrics.get('胜率 (%)', 0),
                '交易次数': len(results.trades),
                '最终权益': results.equity_curve[-1]['equity'] if results.equity_curve else 0
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # 格式化显示
        display_df = df.copy()
        display_df['总收益 (%)'] = display_df['总收益 (%)'].apply(lambda x: f"{x:.2f}%")
        display_df['年化收益 (%)'] = display_df['年化收益 (%)'].apply(lambda x: f"{x:.2f}%")
        display_df['夏普比率'] = display_df['夏普比率'].apply(lambda x: f"{x:.2f}")
        display_df['最大回撤 (%)'] = display_df['最大回撤 (%)'].apply(lambda x: f"{x:.2f}%")
        display_df['胜率 (%)'] = display_df['胜率 (%)'].apply(lambda x: f"{x:.2f}%")
        display_df['最终权益'] = display_df['最终权益'].apply(lambda x: f"¥{x:,.0f}")
        
        # 高亮最优值
        def highlight_best(col):
            if col.name in ['总收益 (%)', '年化收益 (%)', '夏普比率', '胜率 (%)']:
                # 数值越大越好
                max_val = df[col.name.replace('%', '').replace('(', '').replace(')', '').replace('最终权益', '最终权益')].max()
                return ['background-color: #d4edda' if df.loc[i, col.name.replace('%', '').replace('(', '').replace(')', '').replace('最终权益', '最终权益')] == max_val else '' for i in range(len(df))]
            elif col.name == '最大回撤 (%)':
                # 回撤越小越好（绝对值最小）
                min_val = df['最大回撤 (%)'].max()  # 因为是负数，所以 max 是绝对值最小
                return ['background-color: #d4edda' if df.loc[i, '最大回撤 (%)'] == min_val else '' for i in range(len(df))]
            return [''] * len(df)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
    except Exception as e:
        st.error(f"表格生成失败：{e}")


def show_return_comparison(results_dict):
    """显示收益对比"""
    
    try:
        import plotly.graph_objects as go
        
        strategies = list(results_dict.keys())
        returns = [results_dict[name].metrics.get('总收益 (%)', 0) for name in strategies]
        annual_returns = [results_dict[name].metrics.get('年化收益 (%)', 0) for name in strategies]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='总收益',
            x=strategies,
            y=returns,
            marker_color=['green' if r > 0 else 'red' for r in returns]
        ))
        
        fig.add_trace(go.Bar(
            name='年化收益',
            x=strategies,
            y=annual_returns,
            marker_color=['green' if r > 0 else 'red' for r in annual_returns]
        ))
        
        fig.update_layout(
            title='收益对比',
            xaxis_title='策略',
            yaxis_title='收益率 (%)',
            barmode='group',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"图表渲染失败：{e}")


def show_risk_comparison(results_dict):
    """显示风险对比"""
    
    try:
        import plotly.graph_objects as go
        
        strategies = list(results_dict.keys())
        max_drawdowns = [results_dict[name].metrics.get('最大回撤 (%)', 0) for name in strategies]
        sharpe_ratios = [results_dict[name].metrics.get('夏普比率', 0) for name in strategies]
        
        fig = make_subplots(rows=1, cols=2, subplot_titles=('最大回撤对比', '夏普比率对比'))
        
        # 最大回撤
        fig.add_trace(
            go.Bar(
                x=strategies,
                y=max_drawdowns,
                marker_color=['red' if abs(dd) > 20 else 'orange' if abs(dd) > 10 else 'green' for dd in max_drawdowns],
                name='最大回撤'
            ),
            row=1, col=1
        )
        
        # 夏普比率
        fig.add_trace(
            go.Bar(
                x=strategies,
                y=sharpe_ratios,
                marker_color=['green' if sr > 1 else 'orange' if sr > 0 else 'red' for sr in sharpe_ratios],
                name='夏普比率'
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except ImportError:
        # plotly.subplots 可能需要额外导入
        st.info("图表生成需要 plotly 支持")
    except Exception as e:
        st.error(f"图表渲染失败：{e}")


def show_trading_comparison(results_dict):
    """显示交易统计对比"""
    
    try:
        import plotly.graph_objects as go
        
        strategies = list(results_dict.keys())
        trade_counts = [len(results_dict[name].trades) for name in strategies]
        win_rates = [results_dict[name].metrics.get('胜率 (%)', 0) for name in strategies]
        
        fig = make_subplots(rows=1, cols=2, subplot_titles=('交易次数对比', '胜率对比'))
        
        # 交易次数
        fig.add_trace(
            go.Bar(
                x=strategies,
                y=trade_counts,
                marker_color='blue',
                name='交易次数'
            ),
            row=1, col=1
        )
        
        # 胜率
        fig.add_trace(
            go.Bar(
                x=strategies,
                y=win_rates,
                marker_color=['green' if wr > 50 else 'orange' if wr > 40 else 'red' for wr in win_rates],
                name='胜率'
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except ImportError:
        st.info("图表生成需要 plotly 支持")
    except Exception as e:
        st.error(f"图表渲染失败：{e}")


# 动态导入
try:
    from plotly.subplots import make_subplots
except ImportError:
    make_subplots = None
