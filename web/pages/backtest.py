"""
回测页面 - 运行策略回测并展示结果 (增强版)

功能增强:
- ✅ 回测结果导出 (PDF/CSV/图片)
- ✅ 更多图表类型 (K 线图)
- ✅ 交互式图表
- ✅ 数据缓存
- ✅ 性能优化
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入自定义组件和工具
from components import render_header, create_equity_chart, create_drawdown_chart, create_radar_chart, create_kline_chart
from utils import export_all_results, export_results_to_pdf, export_results_to_csv, cache


def show():
    """显示回测页面"""
    
    # 页面头部
    render_header("📈 回测分析", "选择股票和时间范围，运行策略回测")
    
    st.divider()
    
    # 检查是否有已创建的策略
    if 'current_strategy' not in st.session_state:
        st.warning("""
        ⚠️ **尚未创建策略**
        
        请先切换到 [创建策略](pages/create.py) 页面创建一个策略，或从示例策略中选择。
        """)
        
        # 提供快速创建示例策略的选项
        if st.button("✨ 快速创建示例策略", key="quick_create_strategy"):
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
        
        st.divider()
        
        # 导出选项
        if 'current_backtest_results' in st.session_state:
            st.markdown("### 📥 导出结果")
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # CSV 导出
            if st.button("📊 导出 CSV", use_container_width=True):
                results = st.session_state['current_backtest_results']
                csv_data = export_results_to_csv(results)
                st.download_button(
                    label="⬇️ 下载 CSV",
                    data=csv_data,
                    file_name=f"backtest_{timestamp}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            # PDF 导出
            if st.button("📄 导出 PDF", use_container_width=True):
                results = st.session_state['current_backtest_results']
                pdf_data = export_results_to_pdf(results)
                if pdf_data:
                    st.download_button(
                        label="⬇️ 下载 PDF",
                        data=pdf_data,
                        file_name=f"backtest_report_{timestamp}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
    
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
        **回测流程**:
        
        1. **选择股票** - 输入 6 位股票代码 (如 000001)
        2. **设置时间范围** - 选择回测的起止日期
        3. **配置参数** - 可选调整手续费率和滑点
        4. **运行回测** - 点击运行按钮，等待结果
        
        **回测指标**:
        
        - 总收益率、年化收益率
        - 夏普比率、索提诺比率
        - 最大回撤、回撤恢复时间
        - 胜率、盈亏比
        - 交易次数
        
        **图表展示**:
        
        - 权益曲线图
        - 回撤分析图
        - 交易分布图
        - 指标雷达图
        - K 线图 (可选)
        """)
    
    with col2:
        st.markdown("### 💡 小贴士")
        
        st.info("""
        - 首次运行可能需要加载数据，请耐心等待
        - 模拟数据用于快速测试，实盘回测请用真实数据
        - 手续费和滑点会影响回测结果，建议设置合理值
        - 回测结果不代表未来收益，仅供策略验证参考
        - 支持导出 CSV/PDF 格式结果
        """)


def run_backtest(strategy, symbol, start_date, end_date, data_source, commission_rate, slippage):
    """运行回测并展示结果"""
    
    try:
        from src.backtest.engine import BacktestEngine, load_data
        from src.visualization.plotter import StrategyPlotter
        
        # 加载数据 (带缓存)
        cache_key = f"data_{symbol}_{start_date}_{end_date}_{data_source}"
        data = cache.get(cache_key)
        
        if data is None:
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
                    
                    # 缓存数据
                    cache.set(cache_key, data)
                    st.success(f"✅ 成功加载 {len(data)} 条数据")
                    
                except Exception as e:
                    st.error(f"❌ 数据加载失败：{str(e)}")
                    st.info("💡 自动切换到模拟数据...")
                    data = load_data(symbol, start_date, end_date, source='mock')
        else:
            st.info(f"ℹ️ 使用缓存数据：{len(data)} 条")
        
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
    
    # 导出按钮 (顶部)
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.markdown("### 📊 回测结果摘要")
    
    with col2:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_data = export_results_to_csv(results)
        st.download_button(
            label="📥 CSV",
            data=csv_data,
            file_name=f"backtest_{timestamp}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col3:
        pdf_data = export_results_to_pdf(results)
        if pdf_data:
            st.download_button(
                label="📄 PDF",
                data=pdf_data,
                file_name=f"backtest_{timestamp}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    
    st.divider()
    
    # 指标摘要
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
    
    tab1, tab2, tab3, tab4 = st.tabs(["权益曲线", "回撤分析", "指标雷达图", "K 线图"])
    
    with tab1:
        show_equity_chart(results)
    
    with tab2:
        show_drawdown_chart(results)
    
    with tab3:
        show_radar_chart(results)
    
    with tab4:
        show_kline_with_signals(results, data)
    
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
    else:
        st.info("ℹ️ 回测期间无交易")


def show_equity_chart(results):
    """显示权益曲线图"""
    
    try:
        import plotly.graph_objects as go
        
        equity_df = pd.DataFrame(results.equity_curve)
        equity_df.set_index('timestamp', inplace=True)
        
        fig = create_equity_chart(equity_df, title="权益曲线", initial_value=results.initial_capital)
        
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            
            # 导出图表
            if st.button("📥 导出图表为图片", key="export_equity"):
                try:
                    fig.write_image("equity_chart.png")
                    with open("equity_chart.png", "rb") as f:
                        st.download_button(
                            label="⬇️ 下载图片",
                            data=f.read(),
                            file_name="equity_chart.png",
                            mime="image/png"
                        )
                except Exception as e:
                    st.error(f"导出失败：{e}")
        
    except Exception as e:
        st.error(f"图表渲染失败：{e}")


def show_drawdown_chart(results):
    """显示回撤图"""
    
    try:
        equity_df = pd.DataFrame(results.equity_curve)
        equity_df.set_index('timestamp', inplace=True)
        
        fig = create_drawdown_chart(equity_df, title="回撤分析")
        
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"图表渲染失败：{e}")


def show_radar_chart(results):
    """显示指标雷达图"""
    
    try:
        metrics = results.metrics
        
        if not metrics:
            st.info("无指标数据")
            return
        
        # 选择关键指标
        radar_metrics = {
            '总收益': metrics.get('总收益 (%)', 0),
            '夏普比率': metrics.get('夏普比率', 0),
            '胜率': metrics.get('胜率 (%)', 0),
            '回撤控制': abs(metrics.get('最大回撤 (%)', 0)),
        }
        
        fig = create_radar_chart(radar_metrics, title="策略指标雷达图")
        
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"图表渲染失败：{e}")


def show_kline_with_signals(results, data):
    """显示 K 线图和交易信号"""
    
    try:
        import plotly.graph_objects as go
        
        # 准备 K 线数据
        if isinstance(data, pd.DataFrame) and all(col in data.columns for col in ['open', 'high', 'low', 'close']):
            kline_df = data.copy()
            
            fig = go.Figure()
            
            # K 线图
            fig.add_trace(go.Candlestick(
                x=kline_df.index,
                open=kline_df['open'],
                high=kline_df['high'],
                low=kline_df['low'],
                close=kline_df['close'],
                name='K 线',
                increasing_line_color='#26A69A',
                decreasing_line_color='#EF5350'
            ))
            
            # 添加交易信号
            if results.trades:
                buy_signals = [t for t in results.trades if t.get('type') == 'buy']
                sell_signals = [t for t in results.trades if t.get('type') == 'sell']
                
                # 买入信号
                if buy_signals:
                    buy_x = [t.get('timestamp') for t in buy_signals]
                    buy_y = [t.get('price') for t in buy_signals]
                    fig.add_trace(go.Scatter(
                        x=buy_x,
                        y=buy_y,
                        mode='markers',
                        name='买入',
                        marker=dict(symbol='triangle-up', size=12, color='red')
                    ))
                
                # 卖出信号
                if sell_signals:
                    sell_x = [t.get('timestamp') for t in sell_signals]
                    sell_y = [t.get('price') for t in sell_signals]
                    fig.add_trace(go.Scatter(
                        x=sell_x,
                        y=sell_y,
                        mode='markers',
                        name='卖出',
                        marker=dict(symbol='triangle-down', size=12, color='green')
                    ))
            
            fig.update_layout(
                title='K 线图与交易信号',
                xaxis_title='日期',
                yaxis_title='价格',
                height=600,
                template='plotly_white',
                xaxis_rangeslider_visible=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ 数据格式不支持 K 线图显示")
        
    except Exception as e:
        st.error(f"图表渲染失败：{e}")
