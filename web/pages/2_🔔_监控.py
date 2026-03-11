"""
监控中心页面 - 监控任务管理、实时信号、通知历史、设置配置
"""

import streamlit as st
from pathlib import Path
import sys
import pandas as pd
from datetime import datetime, timedelta

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def show():
    """显示监控中心页面"""
    st.markdown('<p class="main-header">🔔 监控中心</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">7x24 小时行情监控，实时捕捉交易信号</p>', unsafe_allow_html=True)
    
    st.divider()
    
    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 监控任务",
        "⚡ 实时信号",
        "📜 通知历史",
        "⚙️ 通知设置"
    ])
    
    with tab1:
        show_monitoring_tasks()
    
    with tab2:
        show_realtime_signals()
    
    with tab3:
        show_notification_history()
    
    with tab4:
        show_notification_settings()


def show_monitoring_tasks():
    """监控任务列表"""
    st.markdown("### 📋 监控任务列表")
    
    # 加载监控任务
    try:
        from src.monitor import MonitorCenter
        center = MonitorCenter()
        tasks = center.list_tasks()
        
        if not tasks:
            # 空状态优化
            st.info("""
            ### 📭 监控任务为空
            
            还没有创建任何监控任务，快来创建你的第一个监控任务吧！
            
            **快速开始**:
            1. 在下方"新建监控任务"表单中填写任务名称
            2. 选择要监控的策略和标的
            3. 设置监控间隔和通知方式
            4. 点击"🚀 创建监控任务"
            """)
            tasks = []
    except Exception as e:
        st.error(f"❌ 操作失败：{str(e)}")
        with st.expander("💡 可能的解决方案"):
            st.markdown("""
            1. 检查网络连接
            2. 确认数据源可用
            3. 查看日志文件：`~/.openfinagent/logs/`
            """)
        if st.button("🔄 重试", key="retry_load_tasks"):
            st.rerun()
        tasks = []
    
    # 显示任务
    if tasks:
        for i, task in enumerate(tasks, 1):
            status_emoji = "🟢" if task.get('status') == 'running' else "🔴"
            status_text = "运行中" if task.get('status') == 'running' else "已停止"
            
            with st.expander(
                f"{status_emoji} {task.get('task_name', '未命名')} - {task.get('symbols', [])} - {status_text}",
                expanded=False
            ):
                st.markdown(f"**任务 ID**: {task.get('task_id', 'N/A')}")
                st.markdown(f"**策略 ID**: {task.get('strategy_id', 'N/A')}")
                st.markdown(f"**监控间隔**: {task.get('interval', 60)}秒")
                st.markdown(f"**创建时间**: {task.get('created_at', 'N/A')}")
                st.markdown(f"**信号数量**: {task.get('signal_count', 0)}")
                
                # 操作按钮
                col1, col2 = st.columns(2)
                with col1:
                    if task.get('status') == 'running':
                        if st.button("⏸️ 停止任务", key=f"task_stop_{i}"):
                            stop_task(task.get('task_id'))
                    else:
                        if st.button("▶️ 启动任务", key=f"task_start_{i}"):
                            start_task(task.get('task_id'))
                with col2:
                    if st.button("🗑️ 删除任务", key=f"task_delete_{i}"):
                        delete_task(task.get('task_id'))
    
    st.divider()
    
    # 新建任务
    st.markdown("### ➕ 新建监控任务")
    
    with st.form("new_task_form"):
        col1, col2 = st.columns(2)
        with col1:
            task_name = st.text_input("任务名称", placeholder="例如：茅台监控任务", key="new_task_name")
        with col2:
            interval = st.number_input("监控间隔 (秒)", min_value=10, max_value=3600, value=60, step=10, key="new_task_interval")
        
        # 选择策略
        strategies = []
        try:
            from src.strategy_factory import StrategyFactory
            factory = StrategyFactory()
            strategies = factory.list_strategies()
        except:
            pass
        
        if strategies:
            strategy_options = {f"{s.name or '', '未命名')} ({s.id or None, 'N/A')})": s.id or None) for s in strategies}
            selected_strategy = st.selectbox("选择策略", options=list(strategy_options.keys()), key="new_task_strategy")
            strategy_id = strategy_options[selected_strategy]
        else:
            st.warning("⚠️ 暂无可用策略，请先在策略工厂创建")
            strategy_id = None
        
        # 选择标的
        symbols = st.text_area(
            "监控标的 (每行一个)",
            placeholder="600519.SH\n000001.SZ\n300750.SZ",
            height=100,
            key="new_task_symbols"
        )
        
        # 通知设置
        notify_enabled = st.checkbox("启用通知", value=True, key="new_task_notify")
        notify_channels = st.multiselect(
            "通知渠道",
            ["APP", "邮件", "短信", "微信"],
            default=["APP"],
            key="new_task_channels"
        )
        
        submit_button = st.form_submit_button("🚀 创建监控任务", type="primary", use_container_width=True)
        
        if submit_button:
            if task_name and symbols and strategy_id:
                symbol_list = [s.strip() for s in symbols.split('\n') if s.strip()]
                create_task(task_name, strategy_id, symbol_list, interval, notify_enabled, notify_channels)
            else:
                st.error("❌ 请填写完整信息")


def create_task(task_name, strategy_id, symbols, interval, notify_enabled, notify_channels):
    """创建监控任务"""
    try:
        from src.monitor import MonitorCenter
        
        center = MonitorCenter()
        task_id = center.start_task(
            task_name=task_name,
            strategy_id=strategy_id,
            symbols=symbols,
            interval=interval,
            notify_enabled=notify_enabled,
            notify_channels=notify_channels
        )
        
        st.success(f"✅ 监控任务已创建：{task_id}")
        st.rerun()
    except Exception as e:
        st.error(f"❌ 操作失败：{str(e)}")
        with st.expander("💡 可能的解决方案"):
            st.markdown("""
            1. 检查网络连接
            2. 确认数据源可用
            3. 查看日志文件：`~/.openfinagent/logs/`
            4. 确认监控服务正常运行
            """)
        if st.button("🔄 重试", key="retry_create_task"):
            st.rerun()


def start_task(task_id):
    """启动任务"""
    try:
        from src.monitor import MonitorCenter
        center = MonitorCenter()
        center.start_task(task_id=task_id)
        st.success("✅ 任务已启动")
        st.rerun()
    except Exception as e:
        st.error(f"❌ 操作失败：{str(e)}")
        with st.expander("💡 可能的解决方案"):
            st.markdown("""
            1. 检查网络连接
            2. 确认数据源可用
            3. 查看日志文件：`~/.openfinagent/logs/`
            """)
        if st.button("🔄 重试", key=f"retry_start_{task_id}"):
            st.rerun()


def stop_task(task_id):
    """停止任务"""
    try:
        from src.monitor import MonitorCenter
        center = MonitorCenter()
        center.stop_task(task_id=task_id)
        st.success("✅ 任务已停止")
        st.rerun()
    except Exception as e:
        st.error(f"❌ 操作失败：{str(e)}")
        with st.expander("💡 可能的解决方案"):
            st.markdown("""
            1. 检查网络连接
            2. 确认数据源可用
            3. 查看日志文件：`~/.openfinagent/logs/`
            """)
        if st.button("🔄 重试", key=f"retry_stop_{task_id}"):
            st.rerun()


def delete_task(task_id):
    """删除任务"""
    if st.confirm("确定要删除这个监控任务吗？"):
        try:
            from src.monitor import MonitorCenter
            center = MonitorCenter()
            center.delete_task(task_id=task_id)
            st.success("✅ 任务已删除")
            st.rerun()
        except Exception as e:
            st.error(f"❌ 操作失败：{str(e)}")
            with st.expander("💡 可能的解决方案"):
                st.markdown("""
                1. 检查网络连接
                2. 确认数据源可用
                3. 查看日志文件：`~/.openfinagent/logs/`
                """)
            if st.button("🔄 重试", key=f"retry_delete_{task_id}"):
                st.rerun()


def show_realtime_signals():
    """实时信号展示"""
    st.markdown("### ⚡ 实时信号")
    
    # 侧边栏配置
    st.sidebar.markdown("### 🔄 刷新设置")
    
    # 刷新间隔配置（5 秒/10 秒/30 秒/60 秒）
    refresh_interval = st.sidebar.selectbox(
        "自动刷新间隔",
        [5000, 10000, 30000, 60000],
        format_func=lambda x: f"{x//1000}秒",
        default=10000,
        key="signal_refresh_interval_select"
    )
    
    # 手动刷新按钮
    if st.sidebar.button("🔄 手动刷新", key="signal_manual_refresh"):
        st.session_state.signal_last_refresh = datetime.now()
        st.rerun()
    
    # 添加自动刷新
    st.autorefresh(refresh_interval)
    
    # 记录刷新时间
    if 'signal_last_refresh' not in st.session_state:
        st.session_state.signal_last_refresh = datetime.now()
    
    # 显示上次刷新时间
    st.caption(f"🕒 上次刷新：{st.session_state.signal_last_refresh.strftime('%H:%M:%S')}")
    st.session_state.signal_last_refresh = datetime.now()
    
    # 加载信号
    try:
        from src.monitor import MonitorCenter
        center = MonitorCenter()
        signals = center.get_signals()
        
        if not signals:
            # 空状态优化
            st.info("""
            ### 💤 暂无实时信号
            
            当前没有收到任何交易信号。
            
            **可能的原因**:
            1. 尚未创建监控任务
            2. 监控任务未运行
            3. 当前没有触发信号的股票
            
            **建议操作**:
            1. 前往"📋 监控任务"创建新任务
            2. 检查现有任务状态并启动
            3. 调整策略参数以生成更多信号
            """)
            if st.button("📋 创建监控任务", key="empty_state_create_task"):
                st.switch_page("pages/05_🔔_监控中心.py")
            signals = []
    except Exception as e:
        st.error(f"❌ 操作失败：{str(e)}")
        with st.expander("💡 可能的解决方案"):
            st.markdown("""
            1. 检查网络连接
            2. 确认数据源可用
            3. 查看日志文件：`~/.openfinagent/logs/`
            """)
        if st.button("🔄 重试", key="retry_load_signals"):
            st.rerun()
        signals = []
    
    # 信号筛选
    if signals:
        col1, col2, col3 = st.columns(3)
        with col1:
            signal_type_filter = st.multiselect(
                "信号类型",
                ["买入", "卖出", "预警"],
                default=["买入", "卖出", "预警"],
                key="signal_type_filter"
            )
        with col2:
            task_filter = st.multiselect(
                "监控任务",
                list(set(s.get('task_name', '') for s in signals)),
                default=list(set(s.get('task_name', '') for s in signals)),
                key="signal_task_filter"
            )
        with col3:
            time_filter = st.selectbox(
                "时间范围",
                ["最近 1 小时", "最近 6 小时", "最近 24 小时", "全部"],
                key="signal_time_filter"
            )
        
        # 筛选信号
        filtered_signals = signals
        
        if signal_type_filter:
            filtered_signals = [s for s in filtered_signals if s.get('signal_type') in signal_type_filter]
        
        if task_filter:
            filtered_signals = [s for s in filtered_signals if s.get('task_name') in task_filter]
        
        # 显示信号
        st.divider()
        st.markdown(f"共 {len(filtered_signals)} 个信号")
        
        for i, signal in enumerate(filtered_signals, 1):
            signal_type = signal.get('signal_type', '')
            type_emoji = "🟢" if signal_type == '买入' else ("🔴" if signal_type == '卖出' else "🟡")
            
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                with col1:
                    st.markdown(f"**{type_emoji} {signal.get('symbol', 'N/A')}**")
                    st.markdown(f"{signal.get('task_name', 'N/A')}")
                with col2:
                    st.markdown(f"**信号类型**: {signal_type}")
                    st.markdown(f"**信号价格**: {signal.get('price', 0):.2f}")
                with col3:
                    st.markdown(f"**信号强度**: {signal.get('strength', 0):.1f}%")
                    st.markdown(f"**时间**: {signal.get('timestamp', 'N/A')}")
                with col4:
                    if st.button("📊 详情", key=f"signal_detail_{i}"):
                        show_signal_detail(signal)
                
                st.divider()


def show_signal_detail(signal):
    """显示信号详情"""
    with st.expander("📊 信号详情", expanded=True):
        st.markdown(f"**信号 ID**: {signal.get('signal_id', 'N/A')}")
        st.markdown(f"**任务 ID**: {signal.get('task_id', 'N/A')}")
        st.markdown(f"**标的**: {signal.get('symbol', 'N/A')}")
        st.markdown(f"**类型**: {signal.get('signal_type', 'N/A')}")
        st.markdown(f"**价格**: {signal.get('price', 0):.2f}")
        st.markdown(f"**强度**: {signal.get('strength', 0):.1f}%")
        st.markdown(f"**时间**: {signal.get('timestamp', 'N/A')}")
        st.markdown(f"**说明**: {signal.get('message', 'N/A')}")


def show_notification_history():
    """通知历史记录"""
    st.markdown("### 📜 通知历史")
    
    # 加载通知历史
    try:
        from src.notification import NotificationService
        service = NotificationService()
        notifications = service.get_history(limit=100)
        
        if not notifications:
            # 空状态优化
            st.info("""
            ### 📭 暂无通知记录
            
            当前没有任何通知记录。
            
            **如何获取通知**:
            1. 创建监控任务并启用通知
            2. 等待交易信号触发
            3. 系统会自动发送通知到配置的渠道
            
            **配置通知**:
            前往"⚙️ 通知设置"配置通知渠道
            """)
            if st.button("⚙️ 配置通知", key="empty_state_config_notify"):
                st.switch_page("pages/05_🔔_监控中心.py")
            notifications = []
    except Exception as e:
        st.error(f"❌ 操作失败：{str(e)}")
        with st.expander("💡 可能的解决方案"):
            st.markdown("""
            1. 检查网络连接
            2. 确认数据源可用
            3. 查看日志文件：`~/.openfinagent/logs/`
            """)
        if st.button("🔄 重试", key="retry_load_notifications"):
            st.rerun()
        notifications = []
    
    # 筛选
    if notifications:
        col1, col2 = st.columns(2)
        with col1:
            channel_filter = st.multiselect(
                "通知渠道",
                ["APP", "邮件", "短信", "微信"],
                default=["APP", "邮件", "短信", "微信"],
                key="notif_channel_filter"
            )
        with col2:
            status_filter = st.multiselect(
                "发送状态",
                ["已发送", "发送失败"],
                default=["已发送", "发送失败"],
                key="notif_status_filter"
            )
        
        # 筛选
        filtered = notifications
        
        if channel_filter:
            filtered = [n for n in filtered if n.get('channel') in channel_filter]
        
        if status_filter:
            status_map = {"已发送": "sent", "发送失败": "failed"}
            filtered = [n for n in filtered if n.get('status') in [status_map.get(s) for s in status_filter]]
        
        # 显示
        st.divider()
        st.markdown(f"共 {len(filtered)} 条通知")
        
        for i, notif in enumerate(filtered, 1):
            status_emoji = "✅" if notif.get('status') == 'sent' else "❌"
            
            with st.expander(f"{status_emoji} {notif.get('content', 'N/A')[:50]}... - {notif.get('sent_at', 'N/A')}", expanded=False):
                st.markdown(f"**通知 ID**: {notif.get('notification_id', 'N/A')}")
                st.markdown(f"**任务 ID**: {notif.get('task_id', 'N/A')}")
                st.markdown(f"**信号 ID**: {notif.get('signal_id', 'N/A')}")
                st.markdown(f"**渠道**: {notif.get('channel', 'N/A')}")
                st.markdown(f"**内容**: {notif.get('content', 'N/A')}")
                st.markdown(f"**状态**: {notif.get('status', 'N/A')}")
                st.markdown(f"**时间**: {notif.get('sent_at', 'N/A')}")


def show_notification_settings():
    """通知设置配置"""
    st.markdown("### ⚙️ 通知设置")
    
    # APP 通知
    st.markdown("#### 📱 APP 通知")
    
    col1, col2 = st.columns(2)
    with col1:
        app_enabled = st.checkbox("启用 APP 通知", value=True, key="notif_app_enabled")
    with col2:
        app_sound = st.checkbox("播放提示音", value=True, key="notif_app_sound")
    
    st.divider()
    
    # 邮件通知
    st.markdown("#### 📧 邮件通知")
    
    col1, col2 = st.columns(2)
    with col1:
        email_enabled = st.checkbox("启用邮件通知", value=False, key="notif_email_enabled")
    with col2:
        email_addr = st.text_input("收件邮箱", placeholder="example@email.com", key="notif_email_addr")
    
    st.divider()
    
    # 短信通知
    st.markdown("#### 📱 短信通知")
    
    col1, col2 = st.columns(2)
    with col1:
        sms_enabled = st.checkbox("启用短信通知", value=False, key="notif_sms_enabled")
    with col2:
        sms_phone = st.text_input("接收手机号", placeholder="138****1234", key="notif_sms_phone")
    
    st.divider()
    
    # 微信通知
    st.markdown("#### 💬 微信通知")
    
    col1, col2 = st.columns(2)
    with col1:
        wechat_enabled = st.checkbox("启用微信通知", value=False, key="notif_wechat_enabled")
    with col2:
        st.markdown("**状态**: 未绑定")
    
    if st.button("绑定微信", key="notif_wechat_bind"):
        # TODO: 实现微信绑定
        st.info("🔲 功能开发中...")
    
    st.divider()
    
    # 保存设置
    if st.button("💾 保存设置", type="primary", use_container_width=True, key="notif_save_settings"):
        save_notification_settings({
            'app': {'enabled': app_enabled, 'sound': app_sound},
            'email': {'enabled': email_enabled, 'address': email_addr},
            'sms': {'enabled': sms_enabled, 'phone': sms_phone},
            'wechat': {'enabled': wechat_enabled}
        })


def save_notification_settings(settings):
    """保存通知设置"""
    try:
        from src.notification import NotificationService
        service = NotificationService()
        service.update_config(settings)
        
        st.success("✅ 设置已保存")
    except Exception as e:
        st.error(f"❌ 保存失败：{str(e)}")


if __name__ == "__main__":
    show()
