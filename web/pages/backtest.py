"""
回测页面 - 运行策略回测并展示结果
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
    """显示回测页面"""
    
    st.markdown('<p class="main-header">📈 回测分析</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">选择股票和时间范围，运行策略回测</p>', unsafe_allow_html=True)
    
    st.divider()
    
    # 检查是否有已创建的策略
    if 'current_strategy' not in st.session_state:
        st.warning("""
        ⚠️ **尚未创建策略**
        
        请先切换到 [创建策略](pages/create.py) 页面创建一个策略，或从示例策略中选择。
        """)
        
        # 提供快速创建示例策略的选项
        if st.button("✨ 快速创建示例策略"):
            try:
                from src.strategy.builder import StrategyBuilder
                strategy = StrategyBuilder.create('ma_cross', short_window=5, long_window=20, initial_capital=100000)
                st.session_state['current_strategy'] = strategy
                st.success("✅ 已创建示例均线交叉策略！")
                st.rerun()
            except Exception as e:
                st.error(f"创建失败：{e}")
        
        st.stop()
    
    # 侧边栏配置
    with st.sidebar:
        st.markdown("### 🎛️ 回测配置")
        
        # 显示当前策略信息
        strategy = st.session_state['current_strategy']
        st.info(f"**当前策略**: {strategy.name}")
        
        st.divider()
        
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
        
        # 默认过去一年
        end_date = st.date_input("结束日期", value=datetime.now().date())
        start_date = st.date_input(
            "开始日期",
            value=end_date - timedelta(days=365),
            max_value=end_date
        )
        
        # 高级设置
        with st.expander("⚙️ 高级设置"):
            commission_rate = st.number_input(
                "手续费率 (万分之)",
                min_value=0.0,
                max_value=10.0,
                value=3.0,
                step=0.1,
                help="默认万分之三"
            ) / 10000.0
            
            slippage = st.number_input(
                "滑点 (%)",
                min_value=0.0,
                max_value=1.0,
                value=0.1,
                step=0.01,
                help="默认 0.1%"
            ) / 100.0
        
        # 运行回测按钮
        run_button = st.button("▶️ 运行回测", use_container_width=True, type="primary")
    
    # 主内容区
    if run_button:
        run_backtest(
            strategy=strategy,
            symbol=symbol,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            data_source=data_source,
            commission_rate=commission_rate,
            slippage=slippage
        )
    else:
        # 显示提示信息
        show_backtest_info()


def show_backtest_info():
    """显示回测说明信息"""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📚 回测说明")
        
        st.markdown("""
        **回测流程**：
        
        1. **选择股票** - 输入 6 位股票代码（如 000001）
        2. **设置时间范围** - 选择回测的起止日期
        3. **配置参数** - 可选调整手续费率和滑点
        4. **运行回测** - 点击运行按钮，等待结果
        
        **回测指标**：
        
        - 总收益率、年化收益率
        - 夏普比率、索提诺比率
        - 最大回撤、回撤恢复时间
        - 胜率、盈亏比
        - 交易次数
        
        **图表展示**：
        
        - 权益曲线图
        - 回撤分析图
        - 交易分布图
        - 指标雷达图
        """)
    
    with col2:
        st.markdown("### 💡 小贴士")
        
        st.info("""
        - 首次运行可能需要加载数据，请耐心等待
        - 模拟数据用于快速测试，实盘回测请用真实数据
        - 手续费和滑点会影响回测结果，建议设置合理值
        - 回测结果不代表未来收益，仅供策略验证参考
        """)


def run_backtest(strategy, symbol, start_date, end_date, data_source, commission_rate, slippage):
    """运行回测并展示结果"""
    
    try:
        from src.backtest.engine import BacktestEngine, load_data
        from src.visualization.plotter import StrategyPlotter
        
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
        
        # 运行回测
        with st.spinner("🔄 正在运行回测..."):
            engine = BacktestEngine(
                commission_rate=commission_rate,
                slippage=slippage
            )
            
            results = engine.run(
                strategy=strategy,
                data=data,
                show_progress=False
            )
        
        st.success("✅ 回测完成！")
        
        # 存储结果到 session
        st.session_state['current_backtest_results'] = results
        st.session_state['current_data'] = data
        
        # 展示结果
        display_backtest_results(results, data)
        
    except Exception as e:
        st.error(f"❌ 回测失败：{str(e)}")
        import traceback
        st.code(traceback.format_exc())


def display_backtest_results(results, data):
    """展示回测结果"""
    
    # 指标摘要
    st.markdown("### 📊 回测结果摘要")
    
    metrics = results.metrics
    
    if metrics:
        # 关键指标
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_return = metrics.get('总收益 (%)', 0)
            color = "🟢" if total_return > 0 else "🔴"
            st.metric(f"{color} 总收益", f"{total_return:.2f}%")
        
        with col2:
            annual_return = metrics.get('年化收益 (%)', 0)
            color = "🟢" if annual_return > 0 else "🔴"
            st.metric(f"{color} 年化收益", f"{annual_return:.2f}%")
        
        with col3:
            sharpe = metrics.get('夏普比率', 0)
            color = "🟢" if sharpe > 1 else "🟡" if sharpe > 0 else "🔴"
            st.metric(f"{color} 夏普比率", f"{sharpe:.2f}")
        
        with col4:
            max_drawdown = metrics.get('最大回撤 (%)', 0)
            color = "🔴" if max_drawdown < -20 else "🟡" if max_drawdown < -10 else "🟢"
            st.metric(f"{color} 最大回撤", f"{max_drawdown:.2f}%")
        
        st.divider()
        
        # 详细指标
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 收益指标")
            st.write(f"- 初始资金：¥{results.initial_capital:,.2f}")
            st.write(f"- 最终权益：¥{results.equity_curve[-1]['equity']:,.2f}")
            st.write(f"- 绝对收益：¥{results.equity_curve[-1]['equity'] - results.initial_capital:,.2f}")
            st.write(f"- 总收益率：{metrics.get('总收益 (%)', 0):.2f}%")
            st.write(f"- 年化收益率：{metrics.get('年化收益 (%)', 0):.2f}%")
        
        with col2:
            st.markdown("#### 风险指标")
            st.write(f"- 最大回撤：{metrics.get('最大回撤 (%)', 0):.2f}%")
            st.write(f"- 夏普比率：{metrics.get('夏普比率', 0):.2f}")
            st.write(f"- 索提诺比率：{metrics.get('索提诺比率', 0):.2f}")
            st.write(f"- 波动率：{metrics.get('年化波动率 (%)', 0):.2f}%")
        
        st.divider()
        
        # 交易统计
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 交易统计")
            total_trades = len(results.trades)
            st.write(f"- 总交易次数：{total_trades}")
            
            buy_trades = [t for t in results.trades if t.get('type') == 'buy']
            sell_trades = [t for t in results.trades if t.get('type') == 'sell']
            st.write(f"- 买入次数：{len(buy_trades)}")
            st.write(f"- 卖出次数：{len(sell_trades)}")
        
        with col2:
            st.markdown("#### 胜率分析")
            win_rate = metrics.get('胜率 (%)', 0)
            st.write(f"- 胜率：{win_rate:.2f}%")
            
            profit_factor = metrics.get('盈亏比', 0)
            st.write(f"- 盈亏比：{profit_factor:.2f}")
        
        with col3:
            st.markdown("#### 其他指标")
            st.write(f"- 平均持仓天数：{metrics.get('平均持仓天数', 0):.1f}")
            st.write(f"- 月均交易次数：{metrics.get('月均交易次数', 0):.1f}")
    
    st.divider()
    
    # 图表展示
    st.markdown("### 📈 可视化分析")
    
    tab1, tab2, tab3 = st.tabs(["权益曲线", "回撤分析", "指标雷达图"])
    
    with tab1:
        show_equity_chart(results)
    
    with tab2:
        show_drawdown_chart(results)
    
    with tab3:
        show_radar_chart(results)
    
    # 交易记录
    st.divider()
    st.markdown("### 📝 交易记录")
    
    if results.trades:
        trades_df = pd.DataFrame(results.trades)
        
        # 格式化显示
        display_df = trades_df.copy()
        if 'timestamp' in display_df.columns:
            display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d')
        
        # 重命名列
        column_names = {
            'timestamp': '日期',
            'type': '类型',
            'price': '价格',
            'shares': '股数',
            'commission': '手续费',
            'cost': '成本',
            'revenue': '收入'
        }
        display_df = display_df.rename(columns=column_names)
        
        st.dataframe(
            display_df[['日期', '类型', '价格', '股数', '手续费']],
            use_container_width=True,
            hide_index=True
        )
        
        # 下载按钮
        csv = trades_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 下载交易记录 (CSV)",
            data=csv,
            file_name=f"{strategy.name}_trades.csv",
            mime="text/csv"
        )
    else:
        st.info("ℹ️ 回测期间无交易")


def show_equity_chart(results):
    """显示权益曲线图"""
    
    try:
        import plotly.graph_objects as go
        
        equity_df = pd.DataFrame(results.equity_curve)
        equity_df.set_index('timestamp', inplace=True)
        
        fig = go.Figure()
        
        # 权益曲线
        fig.add_trace(go.Scatter(
            x=equity_df.index,
            y=equity_df['equity'],
            mode='lines',
            name='权益',
            line=dict(color='#2E86AB', width=2)
        ))
        
        # 初始资金线
        fig.add_trace(go.Scatter(
            x=equity_df.index,
            y=[results.initial_capital] * len(equity_df),
            mode='lines',
            name='初始资金',
            line=dict(color='gray', width=2, dash='dash')
        ))
        
        fig.update_layout(
            title='权益曲线',
            xaxis_title='日期',
            yaxis_title='资金 (元)',
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"图表渲染失败：{e}")


def show_drawdown_chart(results):
    """显示回撤图"""
    
    try:
        import plotly.graph_objects as go
        
        equity_df = pd.DataFrame(results.equity_curve)
        equity_df.set_index('timestamp', inplace=True)
        
        # 计算回撤
        equity_df['peak'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['peak']) / equity_df['peak'] * 100
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=equity_df.index,
            y=equity_df['drawdown'],
            mode='lines',
            name='回撤',
            line=dict(color='#E63946', width=2),
            fill='tozeroy'
        ))
        
        fig.update_layout(
            title='回撤分析',
            xaxis_title='日期',
            yaxis_title='回撤 (%)',
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"图表渲染失败：{e}")


def show_radar_chart(results):
    """显示指标雷达图"""
    
    try:
        import plotly.graph_objects as go
        import numpy as np
        
        metrics = results.metrics
        
        if not metrics:
            st.info("无指标数据")
            return
        
        # 选择关键指标
        categories = ['总收益', '夏普比率', '胜率', '回撤控制']
        
        # 归一化指标到 0-1
        values = [
            min(max(metrics.get('总收益 (%)', 0), -100), 100) / 100,
            min(max(metrics.get('夏普比率', 0), -2), 3) / 3,
            min(max(metrics.get('胜率 (%)', 0), 0), 100) / 100,
            max(1 + min(max(metrics.get('最大回撤 (%)', 0), -100), 0) / 100, 0),
        ]
        
        # 闭合雷达图
        values += values[:1]
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=[cat for cat in categories] + [categories[0]],
            fill='toself',
            name='策略指标',
            line=dict(color='#2E86AB', width=2)
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=False,
            title='策略指标雷达图',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"图表渲染失败：{e}")
