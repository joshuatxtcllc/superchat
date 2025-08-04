
import streamlit as st
from usage_monitor import usage_monitor

def render_usage_widget():
    """Render a compact usage monitoring widget"""
    
    # Get current status
    service_status = usage_monitor.is_service_blocked()
    metrics = usage_monitor.metrics
    limits = usage_monitor.limits
    
    # Status indicator
    if service_status['any_blocked']:
        st.error("🚨 Usage limits exceeded - Services blocked")
    else:
        # Calculate usage percentages
        api_pct = (metrics.api_calls / limits.daily_api_calls * 100) if limits.daily_api_calls > 0 else 0
        cost_pct = (metrics.total_cost / limits.daily_cost * 100) if limits.daily_cost > 0 else 0
        
        if api_pct >= 90 or cost_pct >= 90:
            st.warning(f"⚠️ High usage: API {api_pct:.0f}% | Cost {cost_pct:.0f}%")
        elif api_pct >= 75 or cost_pct >= 75:
            st.info(f"📊 Usage: API {api_pct:.0f}% | Cost {cost_pct:.0f}%")
        else:
            st.success(f"✅ Usage: API {api_pct:.0f}% | Cost {cost_pct:.0f}%")
    
    # Quick stats in expander
    with st.expander("📈 Today's Usage Summary"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("API Calls", f"{metrics.api_calls:,}")
            st.metric("Tokens", f"{metrics.tokens_used:,}")
        
        with col2:
            st.metric("Images", f"{metrics.images_generated}")
            st.metric("Conversations", f"{metrics.conversation_count}")
        
        with col3:
            st.metric("Cost", f"${metrics.total_cost:.2f}")
            st.metric("Users", f"{metrics.daily_active_users}")
        
        # Quick controls
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Reset Daily", key="widget_reset"):
                usage_monitor.reset_daily_metrics()
                st.success("Reset complete!")
                st.rerun()
        
        with col2:
            if service_status['any_blocked']:
                if st.button("🔓 Emergency Override", key="widget_override"):
                    usage_monitor.limits.daily_api_calls *= 2
                    usage_monitor.limits.daily_cost *= 2
                    usage_monitor.save_limits()
                    st.success("Limits increased!")
                    st.rerun()
