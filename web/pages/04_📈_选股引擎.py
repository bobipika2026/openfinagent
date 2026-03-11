"""
选股引擎页面 - 策略选择、条件配置、批量回测、股票池管理
"""

import streamlit as st
from pathlib import Path
import sys
import pandas as pd
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def show():
    """显示选股引擎页面"""
    st.markdown('<p class="main-header">📈 选股引擎</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">基于策略自动筛选股票，支持批量回测和股票池管理</p>', unsafe_allow_html=True)
    
    st.divider()
    
    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 策略选择",
        "⚙️ 条件配置",
        "📊 批量回测",
        "💼 股票池"
    ])
    
    with tab1:
        show_strategy_selector()
    
    with tab2:
        show_condition_config()
    
    with tab3:
        show_batch_backtest()
    
    with tab4:
        show_stock_pool()


def show_strategy_selector():
    """策略选择器"""
    st.markdown("### 🎯 选择策略")
    
    # 从策略库加载策略
    try:
        from src.strategy_factory import StrategyFactory
        factory = StrategyFactory()
        strategies = factory.list_strategies()
        
        if not strategies:
            # 空状态优化
            st.info("""
            ### 📭 策略库为空
            
            还没有创建任何策略，快来创建你的第一个策略吧！
            
            **快速开始**:
            1. 点击左侧导航栏的"🤖 策略工厂"
            2. 输入策略描述（例如：5 日均线上穿 20 日均线时买入）
            3. 点击"创建并回测"
            """)
            if st.button("✨ 创建第一个策略", key="empty_state_create_from_selector"):
                st.switch_page("pages/03_🤖_策略工厂.py")
            strategies = []
    except Exception as e:
        st.error(f"❌ 操作失败：{str(e)}")
        with st.expander("💡 可能的解决方案"):
            st.markdown("""
            1. 检查网络连接
            2. 确认数据源可用
            3. 查看日志文件：`~/.openfinagent/logs/`
            """)
        if st.button("🔄 重试", key="retry_load_strategies"):
            st.rerun()
        strategies = []
    
    # 策略选择
    if strategies:
        strategy_options = {f"{s.get('name', '未命名')} ({s.get('id', 'N/A')})": s for s in strategies}
        selected_name = st.selectbox(
            "选择策略",
            options=list(strategy_options.keys()),
            key="stock_strategy_select"
        )
        selected_strategy = strategy_options[selected_name]
        
        # 显示策略详情
        with st.expander("📋 查看策略详情", expanded=False):
            st.markdown(f"**策略 ID**: {selected_strategy.get('id', 'N/A')}")
            st.markdown(f"**创建时间**: {selected_strategy.get('created_at', 'N/A')}")
            
            if selected_strategy.get('backtest_result'):
                result = selected_strategy['backtest_result']
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("总收益率", f"{result.get('total_return', 0):.2f}%")
                with col2:
                    st.metric("夏普比率", f"{result.get('sharpe_ratio', 0):.2f}")
                with col3:
                    st.metric("胜率", f"{result.get('win_rate', 0):.2f}%")
    else:
        selected_strategy = None
        st.info("👈 请先在'策略工厂'页面创建策略")
    
    st.divider()
    
    # 市场选择
    st.markdown("### 🌍 选择市场")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        market = st.radio(
            "市场",
            ["A 股", "港股", "美股"],
            horizontal=True,
            key="stock_market_select"
        )
    with col2:
        st.markdown("**板块**")
        sector = st.multiselect(
            "选择板块",
            ["主板", "创业板", "科创板", "北交所"],
            default=["主板"],
            key="stock_sector_select"
        )
    with col3:
        st.markdown("**行业**")
        industry = st.multiselect(
            "选择行业",
            ["科技", "消费", "医药", "金融", "制造", "能源", "其他"],
            key="stock_industry_select"
        )
    
    # 下一步按钮
    if st.button("⏭️ 下一步：配置选股条件", type="primary", use_container_width=True, key="stock_next_condition"):
        st.session_state.selected_strategy = selected_strategy
        st.session_state.selected_market = market
        st.session_state.selected_sector = sector
        st.session_state.selected_industry = industry
        st.rerun()


def show_condition_config():
    """选股条件配置"""
    st.markdown("### ⚙️ 选股条件配置")
    
    # 检查前置条件
    if 'selected_strategy' not in st.session_state:
        st.warning("⚠️ 请先选择策略")
        return
    
    st.markdown(f"**当前策略**: {st.session_state.selected_strategy.get('name', '未命名')}")
    st.markdown(f"**市场**: {st.session_state.selected_market}")
    
    st.divider()
    
    # 基本面条件
    st.markdown("### 📊 基本面条件")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        pe_min = st.number_input("市盈率 (PE) 最小值", min_value=0.0, value=0.0, step=1.0, key="cond_pe_min")
        pe_max = st.number_input("市盈率 (PE) 最大值", min_value=0.0, value=100.0, step=1.0, key="cond_pe_max")
    with col2:
        pb_min = st.number_input("市净率 (PB) 最小值", min_value=0.0, value=0.0, step=0.1, key="cond_pb_min")
        pb_max = st.number_input("市净率 (PB) 最大值", min_value=0.0, value=20.0, step=0.1, key="cond_pb_max")
    with col3:
        market_cap_min = st.number_input("市值最小值 (亿元)", min_value=0.0, value=50.0, step=10.0, key="cond_cap_min")
        market_cap_max = st.number_input("市值最大值 (亿元)", min_value=0.0, value=5000.0, step=100.0, key="cond_cap_max")
    
    st.divider()
    
    # 技术面条件
    st.markdown("### 📈 技术面条件")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        ma_period = st.number_input("均线周期", min_value=5, value=20, step=5, key="cond_ma_period")
        ma_above = st.checkbox("股价在均线上方", value=True, key="cond_ma_above")
    with col2:
        volume_ratio_min = st.number_input("量比最小值", min_value=0.0, value=1.0, step=0.1, key="cond_volume_min")
        volume_ratio_max = st.number_input("量比最大值", min_value=0.0, value=10.0, step=0.1, key="cond_volume_max")
    with col3:
        change_min = st.number_input("涨跌幅最小值 (%)", min_value=-20.0, value=-5.0, step=1.0, key="cond_change_min")
        change_max = st.number_input("涨跌幅最大值 (%)", min_value=-20.0, value=20.0, step=1.0, key="cond_change_max")
    
    st.divider()
    
    # 其他条件
    st.markdown("### 🔧 其他条件")
    
    col1, col2 = st.columns(2)
    with col1:
        exclude_st = st.checkbox("排除 ST 股票", value=True, key="cond_exclude_st")
        exclude_new = st.checkbox("排除新股", value=False, key="cond_exclude_new")
    with col2:
        max_stocks = st.number_input("最大选股数量", min_value=1, value=100, step=10, key="cond_max_stocks")
    
    # 条件汇总
    st.divider()
    st.markdown("### 📋 条件汇总")
    
    conditions = {
        "pe_ratio": {"min": pe_min, "max": pe_max},
        "pb_ratio": {"min": pb_min, "max": pb_max},
        "market_cap": {"min": market_cap_min, "max": market_cap_max},
        "ma_condition": {"period": ma_period, "above": ma_above},
        "volume_ratio": {"min": volume_ratio_min, "max": volume_ratio_max},
        "change_percent": {"min": change_min, "max": change_max},
        "exclude_st": exclude_st,
        "exclude_new": exclude_new,
        "max_stocks": max_stocks,
    }
    
    st.json(conditions)
    
    # 开始选股
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 开始选股", type="primary", use_container_width=True, key="stock_start_select"):
            run_stock_selection(conditions)
    with col2:
        if st.button("💾 保存选股方案", use_container_width=True, key="stock_save_plan"):
            save_stock_plan(conditions)


def run_stock_selection(conditions):
    """执行选股"""
    with st.spinner("🔍 正在筛选股票..."):
        try:
            # TODO: 调用选股引擎
            from src.stock_selector import StockSelector
            
            selector = StockSelector()
            result = selector.select_stocks(
                strategy_id=st.session_state.selected_strategy.get('id'),
                conditions=conditions,
                market=st.session_state.selected_market
            )
            
            # 保存到 session state
            st.session_state.selected_stocks = result.get('stocks', [])
            st.session_state.selection_time = datetime.now()
            
            st.success(f"✅ 选股完成！共筛选出 {len(result.get('stocks', []))} 只股票")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ 操作失败：{str(e)}")
            with st.expander("💡 可能的解决方案"):
                st.markdown("""
                1. 检查网络连接
                2. 确认数据源可用
                3. 查看日志文件：`~/.openfinagent/logs/`
                4. 确认选股服务正常运行
                """)
            if st.button("🔄 重试", key="retry_stock_selection"):
                st.rerun()


def save_stock_plan(conditions):
    """保存选股方案"""
    plan_name = st.text_input("方案名称", placeholder="例如：价值投资选股方案", key="plan_name_input")
    
    if st.button("💾 保存", key="plan_save_confirm"):
        try:
            # TODO: 保存到数据库
            st.session_state.stock_plans = st.session_state.get('stock_plans', [])
            st.session_state.stock_plans.append({
                'name': plan_name,
                'conditions': conditions,
                'created_at': datetime.now()
            })
            st.success("✅ 方案已保存")
        except Exception as e:
            st.error(f"❌ 保存失败：{str(e)}")


def show_batch_backtest():
    """批量回测进度"""
    st.markdown("### 📊 批量回测")
    
    if 'selected_stocks' not in st.session_state or not st.session_state.selected_stocks:
        st.warning("⚠️ 请先进行选股")
        return
    
    stocks = st.session_state.selected_stocks
    
    st.markdown(f"**待回测股票数量**: {len(stocks)}")
    
    # 回测配置
    st.markdown("### ⚙️ 回测配置")
    
    col1, col2 = st.columns(2)
    with col1:
        backtest_period = st.selectbox(
            "回测周期",
            ["最近 1 年", "最近 2 年", "最近 3 年", "自定义"],
            key="batch_backtest_period"
        )
    with col2:
        initial_capital = st.number_input(
            "每只股票初始资金",
            min_value=0,
            value=100000,
            step=10000,
            key="batch_backtest_capital"
        )
    
    # 开始回测按钮和取消按钮
    col1, col2 = st.columns(2)
    with col1:
        start_button = st.button("🚀 开始批量回测", type="primary", use_container_width=True, key="batch_backtest_start")
    with col2:
        cancel_button = st.button("⏹️ 取消", use_container_width=True, key="batch_backtest_cancel", disabled=True)
    
    # 开始回测
    if start_button:
        # 启用取消按钮
        st.session_state.batch_backtest_cancel = False
        run_batch_backtest(stocks, initial_capital)
    
    # 检查取消状态
    if 'batch_backtest_cancel' not in st.session_state:
        st.session_state.batch_backtest_cancel = False
    
    # 显示进度
    if 'batch_backtest_progress' in st.session_state:
        progress = st.session_state.batch_backtest_progress
        
        st.markdown("### 📈 回测进度")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 动态显示进度（在实际回测过程中更新）
        if progress.get('status') == 'running':
            for i, stock in enumerate(stocks[:progress.get('current', 0)], 1):
                progress = value = i / progress['total']
                progress_bar.progress(progress)
                status_text.text(f"正在回测：{stock.get('symbol', 'N/A')} ({i}/{progress['total']})")
                
                # 检查是否取消
                if st.session_state.get('batch_backtest_cancel', False):
                    status_text.text("⏹️ 用户取消回测")
                    break
            
            if not st.session_state.get('batch_backtest_cancel', False):
                progress_bar.progress(1.0)
                status_text.text("✅ 批量回测完成！")
        else:
            # 已完成
            progress_bar.progress(1.0)
            status_text.text("✅ 批量回测完成！")
        
        # 显示结果
        if progress.get('status') == 'completed':
            show_batch_results(progress.get('results', []))


def run_batch_backtest(stocks, initial_capital):
    """执行批量回测 - 带进度跟踪和取消支持"""
    try:
        from src.backtest import BatchBacktest
        
        batch = BatchBacktest()
        results = []
        total = len(stocks)
        
        # 初始化进度状态
        st.session_state.batch_backtest_progress = {
            'total': total,
            'current': 0,
            'status': 'running',
            'results': []
        }
        
        # 逐个回测股票
        for i, stock in enumerate(stocks, 1):
            # 检查是否取消
            if st.session_state.get('batch_backtest_cancel', False):
                st.session_state.batch_backtest_progress = {
                    'total': total,
                    'current': i - 1,
                    'status': 'cancelled',
                    'results': results
                }
                st.warning(f"⏹️ 回测已取消，已完成 {i-1}/{total} 只股票")
                st.rerun()
                return
            
            # 执行单只股票回测
            try:
                result = batch.run([stock], initial_capital=initial_capital)
                results.extend(result)
                
                # 更新进度
                st.session_state.batch_backtest_progress = {
                    'total': total,
                    'current': i,
                    'status': 'running',
                    'results': results
                }
                
                # 强制刷新页面以显示进度
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ 股票 {stock.get('symbol', 'N/A')} 回测失败：{str(e)}")
                continue
        
        # 完成所有回测
        st.session_state.batch_backtest_progress = {
            'total': total,
            'current': total,
            'status': 'completed',
            'results': results
        }
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ 批量回测失败：{str(e)}")
        st.session_state.batch_backtest_progress = {
            'total': len(stocks),
            'current': 0,
            'status': 'failed',
            'results': []
        }


def show_batch_results(results):
    """显示批量回测结果"""
    st.markdown("### 📊 回测结果")
    
    if not results:
        return
    
    # 统计指标
    total_stocks = len(results)
    profitable = sum(1 for r in results if r.get('total_return', 0) > 0)
    avg_return = sum(r.get('total_return', 0) for r in results) / total_stocks
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("回测股票数", total_stocks)
    with col2:
        st.metric("盈利比例", f"{profitable/total_stocks*100:.1f}%")
    with col3:
        st.metric("平均收益率", f"{avg_return:.2f}%")
    
    # 结果表格
    st.markdown("### 📋 详细结果")
    
    df_results = pd.DataFrame(results)
    st.dataframe(df_results, use_container_width=True)
    
    # 导出按钮
    if st.button("📥 导出结果", key="batch_export"):
        csv = df_results.to_csv(index=False)
        st.download_button(
            label="下载 CSV",
            data=csv,
            file_name=f"batch_backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )


def show_stock_pool():
    """股票池展示和导出"""
    st.markdown("### 💼 股票池管理")
    
    # 加载股票池
    try:
        from src.stock_selector import StockSelector
        selector = StockSelector()
        pools = selector.list_pools()
        
        if not pools:
            # 空状态优化
            st.info("""
            ### 📭 股票池为空
            
            还没有创建任何股票池，快来筛选你的第一批股票吧！
            
            **快速开始**:
            1. 点击"🎯 策略选择"标签页
            2. 选择一个策略
            3. 配置选股条件并点击"🔍 开始选股"
            """)
            if st.button("🔍 开始选股", key="empty_state_start_selection"):
                st.switch_page("pages/04_📈_选股引擎.py")
            return
    except Exception as e:
        st.error(f"❌ 操作失败：{str(e)}")
        with st.expander("💡 可能的解决方案"):
            st.markdown("""
            1. 检查网络连接
            2. 确认数据源可用
            3. 查看日志文件：`~/.openfinagent/logs/`
            """)
        if st.button("🔄 重试", key="retry_load_pools"):
            st.rerun()
        return
    
    # 股票池列表
    st.markdown("### 📚 股票池列表")
    
    for i, pool in enumerate(pools, 1):
        with st.expander(f"📊 {pool.get('name', '未命名')} - {pool.get('stock_count', 0)}只股票", expanded=False):
            st.markdown(f"**创建时间**: {pool.get('created_at', 'N/A')}")
            st.markdown(f"**更新时间**: {pool.get('updated_at', 'N/A')}")
            
            # 股票列表
            stocks = pool.get('stocks', [])
            if stocks:
                df_stocks = pd.DataFrame(stocks)
                st.dataframe(df_stocks, use_container_width=True)
            
            # 操作按钮
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("👁️ 查看", key=f"pool_view_{i}"):
                    st.session_state.current_pool = pool
                    st.rerun()
            with col2:
                if st.button("📥 导出", key=f"pool_export_{i}"):
                    export_stock_pool(pool)
            with col3:
                if st.button("🗑️ 删除", key=f"pool_delete_{i}"):
                    delete_stock_pool(pool.get('pool_id'))
    
    # 当前股票池详情
    if 'current_pool' in st.session_state:
        st.markdown("### 📋 股票池详情")
        pool = st.session_state.current_pool
        
        st.markdown(f"**名称**: {pool.get('name', '未命名')}")
        st.markdown(f"**ID**: {pool.get('pool_id', 'N/A')}")
        st.markdown(f"**股票数量**: {pool.get('stock_count', 0)}")
        
        # 导出
        if st.button("📥 导出当前股票池", type="primary", key="current_pool_export"):
            export_stock_pool(pool)


def export_stock_pool(pool):
    """导出股票池"""
    try:
        stocks = pool.get('stocks', [])
        if not stocks:
            st.warning("⚠️ 股票池为空")
            return
        
        df = pd.DataFrame(stocks)
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        
        st.download_button(
            label="📥 下载 CSV",
            data=csv,
            file_name=f"{pool.get('name', 'stock_pool')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"❌ 导出失败：{str(e)}")


def delete_stock_pool(pool_id):
    """删除股票池"""
    if st.confirm("确定要删除这个股票池吗？"):
        try:
            from src.stock_selector import StockSelector
            selector = StockSelector()
            selector.delete_pool(pool_id)
            
            st.success("✅ 股票池已删除")
            del st.session_state.current_pool
            st.rerun()
        except Exception as e:
            st.error(f"❌ 删除失败：{str(e)}")


if __name__ == "__main__":
    show()
