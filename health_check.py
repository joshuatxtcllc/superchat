
import streamlit as st
from datetime import datetime
import json
import os
import psutil
import sqlite3
from usage_monitor import usage_monitor
from auth_manager import auth_manager
from production_config import prod_config
import requests
import time

def health_check():
    """Enterprise health check endpoint"""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Check critical systems
        checks = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "environment": prod_config.environment,
            "system_metrics": {
                "cpu_usage_percent": cpu_percent,
                "memory_usage_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_usage_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2)
            },
            "services": {
                "usage_monitor": "healthy" if usage_monitor else "unhealthy",
                "authentication": "healthy" if auth_manager else "unhealthy",
                "file_system": "healthy" if os.path.exists("app.py") else "unhealthy",
                "config": "healthy" if os.path.exists("white_label_config.json") else "unhealthy",
                "database": _check_database_health(),
                "api_keys": _check_api_keys()
            },
            "usage_metrics": {
                "api_calls_today": usage_monitor.metrics.api_calls,
                "cost_today": usage_monitor.metrics.total_cost,
                "conversations_active": len([f for f in os.listdir("conversation_history") if f.endswith(".json")]) if os.path.exists("conversation_history") else 0,
                "uptime_hours": _get_uptime_hours()
            }
        }
        
        # Performance alerts
        alerts = []
        if cpu_percent > 80:
            alerts.append(f"High CPU usage: {cpu_percent}%")
        if memory.percent > 85:
            alerts.append(f"High memory usage: {memory.percent}%")
        if disk.percent > 90:
            alerts.append(f"Low disk space: {disk.percent}% used")
        
        if alerts:
            checks["alerts"] = alerts
        
        # Determine overall health
        unhealthy_services = [k for k, v in checks["services"].items() if v == "unhealthy"]
        if unhealthy_services or cpu_percent > 90 or memory.percent > 95:
            checks["status"] = "critical" if cpu_percent > 90 or memory.percent > 95 else "degraded"
            checks["issues"] = unhealthy_services
            
        return checks
        
    except Exception as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "unhealthy",
            "error": str(e)
        }

def _check_database_health():
    """Check database connectivity"""
    try:
        from database import engine
        connection = engine.connect()
        connection.execute("SELECT 1")
        connection.close()
        return "healthy"
    except Exception:
        return "unhealthy"

def _check_api_keys():
    """Check if essential API keys are configured"""
    openai_key = os.environ.get('OPENAI_API_KEY')
    anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
    
    if openai_key or anthropic_key:
        return "healthy"
    return "degraded"

def _get_uptime_hours():
    """Get system uptime in hours"""
    try:
        uptime_seconds = time.time() - psutil.boot_time()
        return round(uptime_seconds / 3600, 1)
    except:
        return 0

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
