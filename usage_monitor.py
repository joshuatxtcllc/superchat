
import streamlit as st
import json
import os
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import logging

@dataclass
class UsageMetrics:
    """Track various usage metrics"""
    api_calls: int = 0
    tokens_used: int = 0
    images_generated: int = 0
    file_uploads: int = 0
    conversation_count: int = 0
    daily_active_users: int = 0
    total_cost: float = 0.0
    last_reset: str = ""

@dataclass
class UsageLimits:
    """Define usage limits and thresholds"""
    daily_api_calls: int = 1000
    daily_tokens: int = 100000
    daily_images: int = 50
    daily_cost: float = 10.0
    monthly_api_calls: int = 30000
    monthly_tokens: int = 3000000
    monthly_images: int = 1500
    monthly_cost: float = 300.0
    
    # Notification thresholds (percentage of limit)
    warning_threshold: float = 0.75
    critical_threshold: float = 0.90
    
    # Auto-cutoff settings
    enable_auto_cutoff: bool = True
    cutoff_threshold: float = 0.95

@dataclass
class NotificationSettings:
    """Notification configuration"""
    email_enabled: bool = True
    admin_email: str = ""
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    
    # Notification types
    daily_reports: bool = True
    usage_warnings: bool = True
    limit_breaches: bool = True
    system_alerts: bool = True

class UsageMonitor:
    """Comprehensive usage monitoring and management system"""
    
    def __init__(self):
        self.metrics_file = "usage_metrics.json"
        self.limits_file = "usage_limits.json"
        self.notifications_file = "notification_settings.json"
        self.log_file = "usage_monitor.log"
        
        # Setup logging
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        self.metrics = self.load_metrics()
        self.limits = self.load_limits()
        self.notifications = self.load_notifications()
        
    def load_metrics(self) -> UsageMetrics:
        """Load usage metrics from file"""
        try:
            if os.path.exists(self.metrics_file):
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)
                    return UsageMetrics(**data)
        except Exception as e:
            self.logger.error(f"Error loading metrics: {e}")
        return UsageMetrics()
    
    def load_limits(self) -> UsageLimits:
        """Load usage limits from file"""
        try:
            if os.path.exists(self.limits_file):
                with open(self.limits_file, 'r') as f:
                    data = json.load(f)
                    return UsageLimits(**data)
        except Exception as e:
            self.logger.error(f"Error loading limits: {e}")
        return UsageLimits()
    
    def load_notifications(self) -> NotificationSettings:
        """Load notification settings from file"""
        try:
            if os.path.exists(self.notifications_file):
                with open(self.notifications_file, 'r') as f:
                    data = json.load(f)
                    return NotificationSettings(**data)
        except Exception as e:
            self.logger.error(f"Error loading notifications: {e}")
        return NotificationSettings()
    
    def save_metrics(self):
        """Save usage metrics to file"""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(asdict(self.metrics), f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving metrics: {e}")
    
    def save_limits(self):
        """Save usage limits to file"""
        try:
            with open(self.limits_file, 'w') as f:
                json.dump(asdict(self.limits), f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving limits: {e}")
    
    def save_notifications(self):
        """Save notification settings to file"""
        try:
            with open(self.notifications_file, 'w') as f:
                json.dump(asdict(self.notifications), f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving notifications: {e}")
    
    def track_usage(self, usage_type: str, amount: int = 1, cost: float = 0.0):
        """Track usage event"""
        if usage_type == "api_call":
            self.metrics.api_calls += amount
        elif usage_type == "tokens":
            self.metrics.tokens_used += amount
        elif usage_type == "image":
            self.metrics.images_generated += amount
        elif usage_type == "file_upload":
            self.metrics.file_uploads += amount
        elif usage_type == "conversation":
            self.metrics.conversation_count += amount
        elif usage_type == "user":
            self.metrics.daily_active_users += amount
        
        self.metrics.total_cost += cost
        self.save_metrics()
        
        # Check limits after tracking
        self.check_limits()
    
    def check_limits(self) -> Dict[str, bool]:
        """Check if usage is approaching or exceeding limits"""
        status = {
            'api_calls_warning': False,
            'api_calls_critical': False,
            'api_calls_cutoff': False,
            'tokens_warning': False,
            'tokens_critical': False,
            'tokens_cutoff': False,
            'cost_warning': False,
            'cost_critical': False,
            'cost_cutoff': False
        }
        
        # Check API calls
        api_ratio = self.metrics.api_calls / self.limits.daily_api_calls if self.limits.daily_api_calls > 0 else 0
        if api_ratio >= self.limits.cutoff_threshold:
            status['api_calls_cutoff'] = True
            self.send_alert("API Calls Cutoff", f"Daily API calls limit reached: {self.metrics.api_calls}/{self.limits.daily_api_calls}")
        elif api_ratio >= self.limits.critical_threshold:
            status['api_calls_critical'] = True
            self.send_alert("API Calls Critical", f"Daily API calls at {api_ratio*100:.1f}%: {self.metrics.api_calls}/{self.limits.daily_api_calls}")
        elif api_ratio >= self.limits.warning_threshold:
            status['api_calls_warning'] = True
            self.send_alert("API Calls Warning", f"Daily API calls at {api_ratio*100:.1f}%: {self.metrics.api_calls}/{self.limits.daily_api_calls}")
        
        # Check tokens
        token_ratio = self.metrics.tokens_used / self.limits.daily_tokens if self.limits.daily_tokens > 0 else 0
        if token_ratio >= self.limits.cutoff_threshold:
            status['tokens_cutoff'] = True
            self.send_alert("Tokens Cutoff", f"Daily token limit reached: {self.metrics.tokens_used}/{self.limits.daily_tokens}")
        elif token_ratio >= self.limits.critical_threshold:
            status['tokens_critical'] = True
        elif token_ratio >= self.limits.warning_threshold:
            status['tokens_warning'] = True
        
        # Check cost
        cost_ratio = self.metrics.total_cost / self.limits.daily_cost if self.limits.daily_cost > 0 else 0
        if cost_ratio >= self.limits.cutoff_threshold:
            status['cost_cutoff'] = True
            self.send_alert("Cost Cutoff", f"Daily cost limit reached: ${self.metrics.total_cost:.2f}/${self.limits.daily_cost:.2f}")
        elif cost_ratio >= self.limits.critical_threshold:
            status['cost_critical'] = True
        elif cost_ratio >= self.limits.warning_threshold:
            status['cost_warning'] = True
        
        return status
    
    def is_service_blocked(self) -> Dict[str, bool]:
        """Check if services should be blocked due to limits"""
        limits_status = self.check_limits()
        
        return {
            'api_blocked': limits_status['api_calls_cutoff'] and self.limits.enable_auto_cutoff,
            'tokens_blocked': limits_status['tokens_cutoff'] and self.limits.enable_auto_cutoff,
            'cost_blocked': limits_status['cost_cutoff'] and self.limits.enable_auto_cutoff,
            'any_blocked': any([
                limits_status['api_calls_cutoff'],
                limits_status['tokens_cutoff'],
                limits_status['cost_cutoff']
            ]) and self.limits.enable_auto_cutoff
        }
    
    def send_alert(self, alert_type: str, message: str):
        """Send email alert"""
        if not self.notifications.email_enabled or not self.notifications.admin_email:
            return
        
        try:
            msg = MimeMultipart()
            msg['From'] = self.notifications.smtp_username
            msg['To'] = self.notifications.admin_email
            msg['Subject'] = f"Usage Alert: {alert_type}"
            
            body = f"""
            Usage Alert: {alert_type}
            
            {message}
            
            Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            Current Usage:
            - API Calls: {self.metrics.api_calls}
            - Tokens Used: {self.metrics.tokens_used:,}
            - Images Generated: {self.metrics.images_generated}
            - Total Cost: ${self.metrics.total_cost:.2f}
            
            Daily Limits:
            - API Calls: {self.limits.daily_api_calls}
            - Tokens: {self.limits.daily_tokens:,}
            - Cost: ${self.limits.daily_cost:.2f}
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(self.notifications.smtp_server, self.notifications.smtp_port)
            server.starttls()
            server.login(self.notifications.smtp_username, self.notifications.smtp_password)
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Alert sent: {alert_type} - {message}")
            
        except Exception as e:
            self.logger.error(f"Failed to send alert: {e}")
    
    def reset_daily_metrics(self):
        """Reset daily usage metrics"""
        self.metrics.api_calls = 0
        self.metrics.tokens_used = 0
        self.metrics.images_generated = 0
        self.metrics.file_uploads = 0
        self.metrics.conversation_count = 0
        self.metrics.daily_active_users = 0
        self.metrics.total_cost = 0.0
        self.metrics.last_reset = datetime.now().isoformat()
        self.save_metrics()
        self.logger.info("Daily metrics reset")
    
    def get_usage_report(self) -> Dict:
        """Generate comprehensive usage report"""
        limits_status = self.check_limits()
        service_status = self.is_service_blocked()
        
        return {
            'metrics': asdict(self.metrics),
            'limits': asdict(self.limits),
            'status': limits_status,
            'services': service_status,
            'timestamp': datetime.now().isoformat()
        }
    
    def render_monitoring_dashboard(self):
        """Render Streamlit monitoring dashboard"""
        st.title("🔍 Usage Monitoring & Management")
        st.markdown("*Real-time usage tracking, limits, and automated controls*")
        
        # Main metrics display
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            api_ratio = self.metrics.api_calls / self.limits.daily_api_calls if self.limits.daily_api_calls > 0 else 0
            color = "normal" if api_ratio < 0.75 else "off" if api_ratio >= 0.95 else "inverse"
            st.metric(
                "API Calls", 
                f"{self.metrics.api_calls:,}", 
                f"{api_ratio*100:.1f}% of limit",
                delta_color=color
            )
        
        with col2:
            token_ratio = self.metrics.tokens_used / self.limits.daily_tokens if self.limits.daily_tokens > 0 else 0
            color = "normal" if token_ratio < 0.75 else "off" if token_ratio >= 0.95 else "inverse"
            st.metric(
                "Tokens Used", 
                f"{self.metrics.tokens_used:,}", 
                f"{token_ratio*100:.1f}% of limit",
                delta_color=color
            )
        
        with col3:
            st.metric("Images Generated", f"{self.metrics.images_generated:,}")
        
        with col4:
            cost_ratio = self.metrics.total_cost / self.limits.daily_cost if self.limits.daily_cost > 0 else 0
            color = "normal" if cost_ratio < 0.75 else "off" if cost_ratio >= 0.95 else "inverse"
            st.metric(
                "Daily Cost", 
                f"${self.metrics.total_cost:.2f}", 
                f"{cost_ratio*100:.1f}% of limit",
                delta_color=color
            )
        
        # Service status indicators
        service_status = self.is_service_blocked()
        if service_status['any_blocked']:
            st.error("🚨 Services are currently blocked due to limit breaches!")
            if service_status['api_blocked']:
                st.error("❌ API calls blocked")
            if service_status['cost_blocked']:
                st.error("❌ Cost limit exceeded")
        else:
            st.success("✅ All services operational")
        
        # Tabs for different sections
        tabs = st.tabs([
            "📊 Current Usage",
            "⚙️ Limits & Thresholds", 
            "📧 Notifications",
            "🔧 Controls",
            "📈 Reports"
        ])
        
        with tabs[0]:
            self._render_current_usage()
        
        with tabs[1]:
            self._render_limits_config()
        
        with tabs[2]:
            self._render_notification_config()
        
        with tabs[3]:
            self._render_controls()
        
        with tabs[4]:
            self._render_reports()
    
    def _render_current_usage(self):
        """Render current usage tab"""
        st.header("Current Usage Metrics")
        
        # Progress indicators
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Daily Usage")
            
            # API Calls progress
            api_progress = min(self.metrics.api_calls / self.limits.daily_api_calls, 1.0) if self.limits.daily_api_calls > 0 else 0
            st.progress(api_progress, text=f"API Calls: {self.metrics.api_calls:,} / {self.limits.daily_api_calls:,}")
            
            # Tokens progress
            token_progress = min(self.metrics.tokens_used / self.limits.daily_tokens, 1.0) if self.limits.daily_tokens > 0 else 0
            st.progress(token_progress, text=f"Tokens: {self.metrics.tokens_used:,} / {self.limits.daily_tokens:,}")
            
            # Cost progress
            cost_progress = min(self.metrics.total_cost / self.limits.daily_cost, 1.0) if self.limits.daily_cost > 0 else 0
            st.progress(cost_progress, text=f"Cost: ${self.metrics.total_cost:.2f} / ${self.limits.daily_cost:.2f}")
        
        with col2:
            st.subheader("Activity Summary")
            st.write(f"**Conversations:** {self.metrics.conversation_count:,}")
            st.write(f"**File Uploads:** {self.metrics.file_uploads:,}")
            st.write(f"**Active Users:** {self.metrics.daily_active_users:,}")
            
            if self.metrics.last_reset:
                reset_time = datetime.fromisoformat(self.metrics.last_reset)
                st.write(f"**Last Reset:** {reset_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def _render_limits_config(self):
        """Render limits configuration tab"""
        st.header("Usage Limits & Thresholds")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Daily Limits")
            self.limits.daily_api_calls = st.number_input(
                "Daily API Calls", 
                min_value=0, 
                value=self.limits.daily_api_calls
            )
            
            self.limits.daily_tokens = st.number_input(
                "Daily Tokens", 
                min_value=0, 
                value=self.limits.daily_tokens
            )
            
            self.limits.daily_images = st.number_input(
                "Daily Images", 
                min_value=0, 
                value=self.limits.daily_images
            )
            
            self.limits.daily_cost = st.number_input(
                "Daily Cost ($)", 
                min_value=0.0, 
                value=self.limits.daily_cost,
                step=0.01
            )
        
        with col2:
            st.subheader("Alert Thresholds")
            self.limits.warning_threshold = st.slider(
                "Warning Threshold (%)", 
                min_value=0.5, 
                max_value=1.0,
                value=self.limits.warning_threshold,
                step=0.05
            )
            
            self.limits.critical_threshold = st.slider(
                "Critical Threshold (%)", 
                min_value=0.7, 
                max_value=1.0,
                value=self.limits.critical_threshold,
                step=0.05
            )
            
            self.limits.cutoff_threshold = st.slider(
                "Auto-Cutoff Threshold (%)", 
                min_value=0.8, 
                max_value=1.0,
                value=self.limits.cutoff_threshold,
                step=0.05
            )
            
            self.limits.enable_auto_cutoff = st.checkbox(
                "Enable Automatic Service Cutoff", 
                value=self.limits.enable_auto_cutoff
            )
        
        if st.button("💾 Save Limits", type="primary"):
            self.save_limits()
            st.success("✅ Limits saved successfully!")
    
    def _render_notification_config(self):
        """Render notification configuration tab"""
        st.header("Notification Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Email Configuration")
            self.notifications.email_enabled = st.checkbox(
                "Enable Email Notifications", 
                value=self.notifications.email_enabled
            )
            
            if self.notifications.email_enabled:
                self.notifications.admin_email = st.text_input(
                    "Admin Email", 
                    value=self.notifications.admin_email
                )
                
                self.notifications.smtp_server = st.text_input(
                    "SMTP Server", 
                    value=self.notifications.smtp_server
                )
                
                self.notifications.smtp_port = st.number_input(
                    "SMTP Port", 
                    min_value=1, 
                    max_value=65535,
                    value=self.notifications.smtp_port
                )
                
                self.notifications.smtp_username = st.text_input(
                    "SMTP Username", 
                    value=self.notifications.smtp_username
                )
                
                self.notifications.smtp_password = st.text_input(
                    "SMTP Password", 
                    value=self.notifications.smtp_password,
                    type="password"
                )
        
        with col2:
            st.subheader("Notification Types")
            self.notifications.daily_reports = st.checkbox(
                "Daily Usage Reports", 
                value=self.notifications.daily_reports
            )
            
            self.notifications.usage_warnings = st.checkbox(
                "Usage Warnings", 
                value=self.notifications.usage_warnings
            )
            
            self.notifications.limit_breaches = st.checkbox(
                "Limit Breach Alerts", 
                value=self.notifications.limit_breaches
            )
            
            self.notifications.system_alerts = st.checkbox(
                "System Alerts", 
                value=self.notifications.system_alerts
            )
            
            if st.button("📧 Test Email", type="secondary"):
                self.send_alert("Test Alert", "This is a test notification from your usage monitoring system.")
                st.info("Test email sent! Check your inbox.")
        
        if st.button("💾 Save Notification Settings", type="primary"):
            self.save_notifications()
            st.success("✅ Notification settings saved!")
    
    def _render_controls(self):
        """Render control panel tab"""
        st.header("System Controls")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Reset Controls")
            if st.button("🔄 Reset Daily Metrics", type="secondary"):
                self.reset_daily_metrics()
                st.success("✅ Daily metrics reset!")
            
            if st.button("⚠️ Reset All Data", type="secondary"):
                if st.button("🚨 Confirm Reset All", type="secondary"):
                    self.metrics = UsageMetrics()
                    self.save_metrics()
                    st.success("✅ All data reset!")
        
        with col2:
            st.subheader("Service Controls")
            service_status = self.is_service_blocked()
            
            if service_status['any_blocked']:
                if st.button("🔓 Override Limits (Emergency)", type="primary"):
                    # Temporarily raise limits to unblock services
                    self.limits.daily_api_calls *= 2
                    self.limits.daily_tokens *= 2
                    self.limits.daily_cost *= 2
                    self.save_limits()
                    st.success("✅ Limits temporarily increased!")
            else:
                st.success("All services operational")
        
        with col3:
            st.subheader("Manual Tracking")
            track_type = st.selectbox(
                "Track Usage Type",
                ["api_call", "tokens", "image", "file_upload", "conversation", "user"]
            )
            
            track_amount = st.number_input("Amount", min_value=1, value=1)
            track_cost = st.number_input("Cost ($)", min_value=0.0, value=0.0, step=0.01)
            
            if st.button("📊 Track Usage"):
                self.track_usage(track_type, track_amount, track_cost)
                st.success(f"✅ Tracked {track_amount} {track_type}(s)")
    
    def _render_reports(self):
        """Render reports tab"""
        st.header("Usage Reports & Analytics")
        
        # Generate report
        report = self.get_usage_report()
        
        # Summary cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total API Calls Today", f"{report['metrics']['api_calls']:,}")
            st.metric("Total Tokens Today", f"{report['metrics']['tokens_used']:,}")
        
        with col2:
            st.metric("Images Generated", f"{report['metrics']['images_generated']:,}")
            st.metric("Active Conversations", f"{report['metrics']['conversation_count']:,}")
        
        with col3:
            st.metric("Total Cost Today", f"${report['metrics']['total_cost']:.2f}")
            efficiency = (report['metrics']['tokens_used'] / report['metrics']['api_calls']) if report['metrics']['api_calls'] > 0 else 0
            st.metric("Tokens per API Call", f"{efficiency:.1f}")
        
        # Detailed report
        with st.expander("📄 Detailed Usage Report"):
            st.json(report)
        
        # Export options
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Export JSON Report"):
                st.download_button(
                    label="Download Report",
                    data=json.dumps(report, indent=2),
                    file_name=f"usage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("📧 Email Report"):
                self.send_alert("Daily Usage Report", f"Usage Report Generated: {json.dumps(report, indent=2)}")
                st.success("✅ Report emailed!")

# Global usage monitor instance
usage_monitor = UsageMonitor()
