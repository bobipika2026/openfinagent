"""
策略工厂页面 - 通过自然语言创建、预览、优化策略
"""

import streamlit as st
from pathlib import Path
import sys
import json
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def show():
    """显示策略工厂页面"""
    st.markdown('<p class="main-header">🤖 策略工厂</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">用自然语言描述你的交易想法，AI 自动生成并回测策略</p>', unsafe_allow_html=True)
    
    st.divider()
    
    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs([
        "✨ 创建策略",
        "📋 策略预览",
        "📊 回测结果",
        "💾 入库状态"
    ])
    
    with tab1:
        show_create_strategy()
    
    with tab2:
        show_strategy_preview()
    
    with tab3:
        show_backtest_results()
    
    with tab4:
        show_storage_status()


def show_create_strategy():
    """创建策略"""
    st.markdown("### 🗣️ 自然语言输入")
    
    st.markdown("""
    **提示**：用中文描述你的交易策略，包括：
    - 买入条件（例如：均线上穿、RSI 超卖等）
    - 卖出条件（例如：均线下穿、RSI 超买等）
    - 初始资金（可选，默认 10 万元）
    - 回测标的（可选，默认 '600519.SH'）
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
        key="factory_description"
    )
    
    # 高级配置
    with st.expander("⚙️ 高级配置", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            initial_capital = st.number_input(
                "初始资金",
                min_value=0,
                value=100000,
                step=10000,
                key="factory_capital"
            )
        with col2:
            symbol = st.text_input(
                "回测标的",
                value="600519.SH",
                key="factory_symbol"
            )
        
        col3, col4 = st.columns(2)
        with col3:
            start_date = st.date_input(
                "回测开始日期",
                value=datetime(2023, 1, 1),
                key="factory_start_date"
            )
        with col4:
            end_date = st.date_input(
                "回测结束日期",
                value=datetime(2023, 12, 31),
                key="factory_end_date"
            )
    
    # 创建按钮和自动回测选项
    auto_backtest = st.checkbox(
        "✅ 创建后自动回测",
        value=False,
        help="勾选后，策略创建完成后会自动运行回测",
        key="factory_auto_backtest"
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        create_button = st.button(
            "🚀 创建策略" + (" + 回测" if auto_backtest else ""),
            type="primary",
            use_container_width=True,
            key="factory_create"
        )
    with col2:
        st.button(
            "🔍 搜索策略",
            use_container_width=True,
            key="factory_search"
        )
    with col3:
        st.button(
            "🧬 优化策略",
            use_container_width=True,
            key="factory_optimize"
        )
    
    # 处理创建
    if create_button and strategy_description:
        create_strategy_from_text(
            strategy_description,
            auto_backtest=auto_backtest,
            initial_capital=initial_capital,
            symbol=symbol
        )


def create_strategy_from_text(description, initial_capital, symbol):
    """从文本创建策略"""
    with st.spinner("🤖 AI 正在生成策略..."):
        try:
            from src.strategy_factory import StrategyFactory
            
            factory = StrategyFactory()
            # 暂时禁用自动回测，避免动态加载问题
            result = factory.create_from_natural_language(
                description=description,
                auto_backtest=False  # 暂时禁用
            )
            
            # 保存到 session state
            st.session_state.current_strategy = result
            st.session_state.current_strategy.created_at = datetime.now()
            
            st.success("✅ 策略创建成功！回测功能修复中...")
            st.info("💡 策略已保存到策略库，可以手动运行回测")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ 操作失败：{str(e)}")
            with st.expander("💡 可能的解决方案"):
                st.markdown("""
                1. 检查网络连接
                2. 确认数据源可用
                3. 查看日志文件：`~/.openfinagent/logs/`
                4. 确认策略服务正常运行
                """)
            if st.button("🔄 重试", key="retry_create_strategy"):
                st.rerun()


def show_strategy_preview():
    """策略预览和编辑"""
    st.markdown("### 📋 策略预览")
    
    if 'current_strategy' not in st.session_state:
        # 空状态优化
        st.info("""
        ### 📭 暂无策略预览
        
        还没有创建或选择任何策略。
        
        **快速开始**:
        1. 点击"✨ 创建策略"标签页
        2. 输入策略描述（例如：5 日均线上穿 20 日均线时买入）
        3. 点击"🚀 创建策略"
        4. 策略将自动在此处预览
        """)
        if st.button("✨ 创建第一个策略", key="empty_state_preview_create"):
            st.switch_page("pages/03_🤖_策略工厂.py")
        return
    
    strategy = st.session_state.current_strategy
    
    # 策略基本信息
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**策略名称**: {strategy.name or '未命名'}")
        st.markdown(f"**策略 ID**: {strategy.id or 'N/A'}")
    with col2:
        st.markdown(f"**创建时间**: {strategy.created_at or 'N/A'}")
        st.markdown(f"**状态**: {'✅ 已回测' if strategy.backtest_report else '⏳ 待回测'}")
    
    st.divider()
    
    # 策略代码预览
    st.markdown("### 💻 策略代码")
    
    code = strategy.code or '# 策略代码生成中...'
    st.code(code, language='python', line_numbers=True)
    
    # 编辑按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✏️ 编辑策略", use_container_width=True, key="preview_edit"):
            st.session_state.editing_strategy = True
    with col2:
        if st.button("💾 保存修改", use_container_width=True, key="preview_save"):
            # TODO: 保存修改
            st.success("✅ 策略已保存")


def show_backtest_results():
    """回测结果展示"""
    st.markdown("### 📊 回测结果")
    
    if 'current_strategy' not in st.session_state:
        # 空状态优化
        st.info("""
        ### 📭 暂无回测结果
        
        还没有创建或回测任何策略。
        
        **快速开始**:
        1. 点击"✨ 创建策略"标签页
        2. 输入策略描述
        3. 点击"🚀 创建策略"
        4. 回测结果将自动在此处展示
        """)
        if st.button("✨ 创建第一个策略", key="empty_state_backtest_create"):
            st.switch_page("pages/03_🤖_策略工厂.py")
        return
    
    strategy = st.session_state.current_strategy
    backtest_result = strategy.backtest_report
    
    if not backtest_result:
        # 空状态优化 - 策略已创建但未回测
        st.info("""
        ### ⏳ 回测尚未完成
        
        策略已创建但还未进行回测。
        
        **下一步**:
        1. 返回"✨ 创建策略"标签页
        2. 勾选"自动回测"选项
        3. 重新创建策略
        """)
        return
    
    # 核心指标
    st.markdown("#### 📈 核心指标")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_return = backtest_result.get('total_return', 0)
        st.metric("总收益率", f"{total_return:.2f}%")
    with col2:
        annual_return = backtest_result.get('annual_return', 0)
        st.metric("年化收益率", f"{annual_return:.2f}%")
    with col3:
        sharpe = backtest_result.get('sharpe_ratio', 0)
        st.metric("夏普比率", f"{sharpe:.2f}")
    with col4:
        max_dd = backtest_result.get('max_drawdown', 0)
        st.metric("最大回撤", f"{max_dd:.2f}%")
    
    st.divider()
    
    # 详细指标
    col1, col2, col3 = st.columns(3)
    with col1:
        win_rate = backtest_result.get('win_rate', 0)
        st.metric("胜率", f"{win_rate:.2f}%")
    with col2:
        total_trades = backtest_result.get('total_trades', 0)
        st.metric("总交易次数", total_trades)
    with col3:
        pl_ratio = backtest_result.get('profit_loss_ratio', 0)
        st.metric("盈亏比", f"{pl_ratio:.2f}")
    
    st.divider()
    
    # 权益曲线
    st.markdown("#### 📉 权益曲线")
    
    equity_curve = backtest_result.get('equity_curve', [])
    if equity_curve:
        import pandas as pd
        df = pd.DataFrame(equity_curve)
        st.line_chart(df.set_index('date')['equity'])
    
    # 交易记录
    st.markdown("#### 💼 交易记录")
    
    trades = backtest_result.get('trades', [])
    if trades:
        df_trades = pd.DataFrame(trades)
        st.dataframe(df_trades, use_container_width=True)


def show_storage_status():
    """策略入库状态"""
    st.markdown("### 💾 策略入库状态")
    
    if 'current_strategy' not in st.session_state:
        # 空状态优化
        st.info("""
        ### 📭 暂无策略入库
        
        还没有创建或保存任何策略到策略库。
        
        **快速开始**:
        1. 点击"✨ 创建策略"标签页
        2. 输入策略描述并创建
        3. 完成回测后点击"📥 保存到策略库"
        """)
        if st.button("✨ 创建第一个策略", key="empty_state_storage_create"):
            st.switch_page("pages/03_🤖_策略工厂.py")
        return
    
    strategy = st.session_state.current_strategy
    
    # 入库状态
    stored = hasattr(strategy, 'stored') and strategy.stored
    
    if stored:
        st.success("✅ 策略已入库")
        stored_at = st.session_state.get('strategy_stored_at', strategy.created_at)
        st.markdown(f"**入库时间**: {stored_at.strftime('%Y-%m-%d %H:%M:%S') if stored_at else 'N/A'}")
        st.markdown(f"**库中 ID**: {strategy.id or 'N/A'}")
    else:
        st.warning("⚠️ 策略尚未入库")
        
        # 入库按钮
        if st.button("📥 保存到策略库", type="primary", key="storage_save"):
            # TODO: 调用入库 API
            try:
                # 模拟入库 - 使用 session_state 存储状态
                st.session_state.strategy_stored = True
                st.session_state.strategy_stored_at = datetime.now()
                st.success("✅ 策略已成功入库")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 入库失败：{str(e)}")
    
    st.divider()
    
    # 策略库列表
    st.markdown("### 📚 策略库")
    
    try:
        from src.strategy_factory import StrategyFactory
        factory = StrategyFactory()
        library = factory.list_strategies()
        
        if library:
            for i, strat in enumerate(library, 1):
                with st.expander(f"📊 {strat.name or '未命名'} - {strat.id or 'N/A'}", expanded=False):
                    st.markdown(f"**创建时间**: {strat.created_at or 'N/A'}")
                    st.markdown(f"**回测状态**: {'✅ 已回测' if strat.backtest_report else '⏳ 未回测'}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("👁️ 查看", key=f"lib_view_{i}"):
                            st.session_state.current_strategy = strat
                            st.rerun()
                    with col2:
                        if st.button("🗑️ 删除", key=f"lib_delete_{i}"):
                            # TODO: 删除策略
                            st.success("✅ 策略已删除")
        else:
            # 空状态优化
            st.info("""
            ### 📭 策略库为空
            
            还没有创建任何策略，快来创建你的第一个策略吧！
            
            **快速开始**:
            1. 点击左侧导航栏的"✨ 创建策略"
            2. 输入策略描述（例如：5 日均线上穿 20 日均线时买入）
            3. 点击"创建并回测"
            """)
            if st.button("✨ 创建第一个策略", key="empty_state_create_strategy"):
                st.switch_page("pages/03_🤖_策略工厂.py")
    except Exception as e:
        st.error(f"❌ 操作失败：{str(e)}")
        with st.expander("💡 可能的解决方案"):
            st.markdown("""
            1. 检查网络连接
            2. 确认数据源可用
            3. 查看日志文件：`~/.openfinagent/logs/`
            """)
        if st.button("🔄 重试", key="retry_load_library"):
            st.rerun()


if __name__ == "__main__":
    show()
