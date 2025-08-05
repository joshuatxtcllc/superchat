
import streamlit as st
from datetime import datetime
import json
import os
from usage_monitor import usage_monitor

def health_check():
    """Production health check endpoint"""
    try:
        # Check critical systems
        checks = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "services": {
                "usage_monitor": "healthy" if usage_monitor else "unhealthy",
                "file_system": "healthy" if os.path.exists("app.py") else "unhealthy",
                "config": "healthy" if os.path.exists("white_label_config.json") else "unhealthy"
            },
            "metrics": {
                "api_calls_today": usage_monitor.metrics.api_calls,
                "cost_today": usage_monitor.metrics.total_cost,
                "conversations_active": len([f for f in os.listdir("conversation_history") if f.endswith(".json")])
            }
        }
        
        # Determine overall health
        unhealthy_services = [k for k, v in checks["services"].items() if v == "unhealthy"]
        if unhealthy_services:
            checks["status"] = "degraded"
            checks["issues"] = unhealthy_services
            
        return checks
        
    except Exception as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "unhealthy",
            "error": str(e)
        }

def render_health_dashboard():
    """Render health check dashboard"""
    st.title("🏥 System Health Dashboard")
    
    health = health_check()
    
    if health["status"] == "healthy":
        st.success("✅ All systems operational")
    elif health["status"] == "degraded":
        st.warning(f"⚠️ System degraded - Issues: {', '.join(health.get('issues', []))}")
    else:
        st.error("🚨 System unhealthy")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Service Status")
        for service, status in health["services"].items():
            if status == "healthy":
                st.success(f"✅ {service}")
            else:
                st.error(f"❌ {service}")
    
    with col2:
        st.subheader("System Metrics")
        metrics = health.get("metrics", {})
        st.metric("API Calls Today", metrics.get("api_calls_today", 0))
        st.metric("Cost Today", f"${metrics.get('cost_today', 0):.2f}")
        st.metric("Active Conversations", metrics.get("conversations_active", 0))
    
    with st.expander("Raw Health Data"):
        st.json(health)
    
    if st.button("🔄 Refresh Health Check"):
        st.rerun()
