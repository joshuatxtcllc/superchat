
import time
import threading
from datetime import datetime, timedelta
from usage_monitor import usage_monitor
import logging

class UsageAlertSystem:
    """Automated usage monitoring and alerting system"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.check_interval = 300  # 5 minutes
        self.logger = logging.getLogger(__name__)
        
    def start_monitoring(self):
        """Start the automated monitoring system"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.thread.start()
            self.logger.info("Usage alert system started")
    
    def stop_monitoring(self):
        """Stop the automated monitoring system"""
        self.running = False
        if self.thread:
            self.thread.join()
        self.logger.info("Usage alert system stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                self._check_usage_patterns()
                self._check_daily_reset()
                self._send_scheduled_reports()
                time.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait a minute before retrying
    
    def _check_usage_patterns(self):
        """Check for unusual usage patterns"""
        metrics = usage_monitor.metrics
        
        # Check for rapid usage spikes
        current_time = datetime.now()
        
        # Example: Alert if more than 100 API calls in 5 minutes
        # This would require tracking timestamps, simplified here
        
        # Check for cost anomalies
        if metrics.total_cost > usage_monitor.limits.daily_cost * 0.5:
            # Half daily budget used
            usage_monitor.send_alert(
                "Budget Alert",
                f"50% of daily budget consumed: ${metrics.total_cost:.2f}"
            )
    
    def _check_daily_reset(self):
        """Check if daily metrics should be reset"""
        if usage_monitor.metrics.last_reset:
            last_reset = datetime.fromisoformat(usage_monitor.metrics.last_reset)
            if datetime.now().date() > last_reset.date():
                # It's a new day, reset metrics
                usage_monitor.reset_daily_metrics()
                usage_monitor.send_alert("Daily Reset", "Daily usage metrics have been reset")
    
    def _send_scheduled_reports(self):
        """Send scheduled usage reports"""
        if usage_monitor.notifications.daily_reports:
            # Send daily report at 9 AM
            now = datetime.now()
            if now.hour == 9 and now.minute < 5:  # 5-minute window
                report = usage_monitor.get_usage_report()
                usage_monitor.send_alert(
                    "Daily Usage Report",
                    f"Daily usage summary:\n{report}"
                )

# Global alert system instance
alert_system = UsageAlertSystem()

# Auto-start when imported
alert_system.start_monitoring()
