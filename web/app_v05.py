"""
OpenFinAgent Web UI v0.5.0 - 极简版

核心思想:
- 小白用户只关心赚钱
- 用户只需输入股票代码
- AI 自动选择最优策略
- 自动回测真实数据
- 直接告诉你能不能赚钱
"""

import streamlit as st
from pathlib import Path
import sys
import pandas as pd

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入极简 API
from api.agent_api_v05 import OpenFinAgentAPI_v05

# 初始化 API
api = OpenFinAgentAPI_v05()


# ==================== 页面配置 ====================
st.set_page_config(
    page_title="OpenFinAgent - AI 量化赚钱",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ==================== 首页 (极简版) ====================
def render_home():
    """极简首页 - 只关心赚钱"""
    
    # 大标题
    st.markdown("""
    <div style="text-align: center; padding: 50px 0;">
        <h1 style="font-size: 3.5rem; margin-bottom: 10px;">💰 OpenFinAgent</h1>
        <h2 style="font-size: 2rem; color: #666; margin-bottom: 30px;">AI 量化赚钱工具</h2>
        <p style="font-size: 1.2rem; color: #999;">输入股票代码，AI 自动帮你测试哪个策略最赚钱</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # 核心功能 - 极简输入
    st.markdown("""
    ### 🎯 3 步开始赚钱
    
    1. **输入股票代码** - 例如：600519.SH (贵州茅台)
    2. **点击"AI 自动回测"** - AI 测试多个策略
    3. **查看结果** - 直接告诉你能不能赚钱
    """)
    
    # 股票输入
    col1, col2 = st.columns([3, 1])
    with col1:
        symbol = st.text_input(
            "股票代码",
            value="600519.SH",
            placeholder="输入股票代码，例如：600519.SH",
            label_visibility="collapsed"
        )
    
    with col2:
        if st.button("🤖 AI 自动回测", type="primary", use_container_width=True, height=50):
            st.session_state.symbol = symbol
            st.session_state.show_result = True
            st.rerun()
    
    st.divider()
    
    # 热门股票推荐
    st.markdown("### 🔥 热门股票")
    
    hot_stocks = {
        '600519.SH': '贵州茅台 - A 股之王',
        '000001.SZ': '平安银行 - 银行龙头',
        '300750.SZ': '宁德时代 - 电池龙头',
        '000858.SZ': '五粮液 - 白酒龙头',
        '601318.SH': '中国平安 - 保险龙头'
    }
    
    cols = st.columns(5)
    for idx, (code, name) in enumerate(hot_stocks.items()):
        with cols[idx]:
            if st.button(f"{code}\n{name}", key=f"hot_{code}", use_container_width=True):
                st.session_state.symbol = code
                st.session_state.show_result = True
                st.rerun()
    
    st.divider()
    
    # 使用说明
    with st.expander("❓ 如何使用"):
        st.markdown("""
        ### 常见问题
        
        **Q: 我不会炒股，能用吗？**
        A: 可以！你只需要输入股票代码，AI 会自动测试哪个策略最赚钱。
        
        **Q: 需要懂策略吗？**
        A: 不需要！AI 会自动测试均线交叉、RSI 等多个策略，选择收益最好的。
        
        **Q: 数据真实吗？**
        A: 真实！使用历史真实行情数据回测。
        
        **Q: 保证赚钱吗？**
        A: 不保证！历史收益不代表未来表现，投资有风险。
        
        **Q: 支持哪些股票？**
        A: A 股、美股、加密货币都支持。
        """)
    
    # 页脚
    st.divider()
    st.markdown(
        """
        <div style="text-align: center; color: #666; padding: 20px;">
            OpenFinAgent v0.5.0 (极简版) | AI 量化赚钱工具 | 
            <a href="https://github.com/bobipika2026/openfinagent">GitHub</a>
        </div>
        """,
        unsafe_allow_html=True
    )


# ==================== 结果页面 ====================
def render_result():
    """结果页面 - 直接告诉你能不能赚钱"""
    
    symbol = st.session_state.get('symbol', '600519.SH')
    
    # 标题
    st.markdown(f'# 📊 {symbol} 回测结果')
    
    # 运行回测
    with st.spinner("🤖 AI 正在测试多个策略，寻找最优方案..."):
        result = api.auto_backtest(symbol)
    
    if result['success']:
        metrics = result['metrics']
        
        # 投资建议 (最显眼)
        st.markdown("### 🎯 AI 投资建议")
        
        recommendation = result['recommendation']
        if '强烈推荐' in recommendation:
            st.success(f"# {recommendation}", icon="🟢")
        elif '推荐' in recommendation:
            st.info(f"# {recommendation}", icon="🟡")
        elif '谨慎' in recommendation:
            st.warning(f"# {recommendation}", icon="🟠")
        else:
            st.error(f"# {recommendation}", icon="🔴")
        
        st.markdown(f"**AI 自动选择的最优策略**: {result['best_strategy']}")
        
        st.divider()
        
        # 核心指标
        st.markdown("### 📊 核心指标")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_return = metrics.get('总收益 (%)', 0)
            st.metric(
                "总收益",
                f"{total_return:.2f}%",
                delta="赚钱" if total_return > 0 else "亏损"
            )
        
        with col2:
            annual_return = metrics.get('年化收益 (%)', 0)
            st.metric(
                "年化收益",
                f"{annual_return:.2f}%",
                delta=f"{annual_return:.1f}%"
            )
        
        with col3:
            sharpe = metrics.get('夏普比率', 0)
            st.metric(
                "夏普比率",
                f"{sharpe:.2f}",
                delta="低风险" if sharpe > 1 else "高风险"
            )
        
        with col4:
            max_dd = metrics.get('最大回撤 (%)', 0)
            st.metric(
                "最大回撤",
                f"{max_dd:.2f}%",
                delta=f"{max_dd:.1f}%"
            )
        
        st.divider()
        
        # 收益说明
        st.markdown("### 💰 收益说明")
        
        initial = metrics.get('初始资金', 100000)
        final = metrics.get('最终资金', initial)
        profit = final - initial
        
        if profit > 0:
            st.success(f"""
            **如果投入 ¥{initial:,.0f}，最终收益 ¥{final:,.2f}**
            
            - 总收益：¥{profit:,.2f}
            - 收益率：{metrics.get('总收益 (%)', 0):.2f}%
            - 交易次数：{metrics.get('交易次数', 0)} 次
            - 胜率：{metrics.get('胜率 (%)', 0):.1f}%
            """)
        else:
            st.error(f"""
            **如果投入 ¥{initial:,.0f}，最终收益 ¥{final:,.2f}**
            
            - 总亏损：¥{abs(profit):,.2f}
            - 收益率：{metrics.get('总收益 (%)', 0):.2f}%
            - 交易次数：{metrics.get('交易次数', 0)} 次
            - 胜率：{metrics.get('胜率 (%)', 0):.1f}%
            """)
        
        st.divider()
        
        # 交易记录
        st.markdown("### 📝 最近交易")
        trades = result['trades']
        
        if trades:
            df_trades = pd.DataFrame(trades)
            
            # 格式化显示
            df_display = df_trades.copy()
            df_display['类型'] = df_display['类型'].apply(lambda x: '🟢 买入' if x == '买入' else '🔴 卖出')
            df_display['价格'] = df_display['价格'].apply(lambda x: f'¥{x:.2f}')
            df_display['盈亏'] = df_display['盈亏'].apply(lambda x: f"{'+' if x > 0 else ''}¥{x:.2f}")
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # 策略对比
        st.markdown("### ⚖️ 策略对比")
        st.markdown("AI 测试了多个策略，这是对比结果:")
        
        compare_result = api.compare_strategies(symbol)
        
        if compare_result['success']:
            df_compare = pd.DataFrame(compare_result['results'])
            
            # 格式化
            df_display = df_compare.copy()
            df_display['总收益 (%)'] = df_display['总收益 (%)'].apply(lambda x: f"{x:.2f}%")
            df_display['夏普比率'] = df_display['夏普比率'].apply(lambda x: f"{x:.2f}")
            df_display['最大回撤 (%)'] = df_display['最大回撤 (%)'].apply(lambda x: f"{x:.2f}%")
            df_display['胜率 (%)'] = df_display['胜率 (%)'].apply(lambda x: f"{x:.1f}%")
            
            # 高亮最优
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # 操作按钮
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 测试其他股票", use_container_width=True):
                st.session_state.show_result = False
                st.rerun()
        
        with col2:
            st.download_button(
                "📥 下载交易记录",
                data=pd.DataFrame(trades).to_csv(index=False),
                file_name=f"{symbol}_trades.csv",
                use_container_width=True
            )
        
        with col3:
            st.link_button(
                "📊 查看策略详情",
                "https://github.com/bobipika2026/openfinagent",
                use_container_width=True
            )
        
    else:
        st.error(f"❌ 回测失败：{result.get('error', '未知错误')}")
        
        if st.button("🔄 重试"):
            st.session_state.show_result = False
            st.rerun()


# ==================== 主程序 ====================
def main():
    """主函数"""
    
    # 检查是否显示结果
    if st.session_state.get('show_result', False):
        render_result()
    else:
        render_home()


if __name__ == "__main__":
    main()
