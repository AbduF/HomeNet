"""
HomeNet — Alert Manager
Handles system alerts, notifications, and email alerts.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Callable
from .database import DatabaseManager
from .config import ConfigManager


class AlertManager:
    """Manages alerts and notifications."""

    def __init__(self, db: DatabaseManager, config: ConfigManager):
        self.db = db
        self.config = config
        self.callbacks: list = []

    def register_callback(self, callback: Callable) -> None:
        """Register a callback for new alerts."""
        self.callbacks.append(callback)

    def notify_new_host(self, ip: str, hostname: str = "", mac: str = "") -> int:
        """Create alert for newly discovered host."""
        message = f"New device connected: {hostname or ip}"
        if mac:
            message += f" (MAC: {mac})"

        alert_id = self.db.add_alert(
            "new_host", message, "warning", ip
        )

        self._send_notifications("new_host", message, "warning", ip)
        return alert_id

    def notify_high_traffic(self, ip: str, bytes_total: int) -> int:
        """Create alert for high traffic volume."""
        threshold = self.config.get("alerts.high_traffic_threshold_mb", 500) * 1_048_576
        if bytes_total > threshold:
            message = f"High traffic detected: {ip} - {bytes_total / 1_048_576:.1f} MB"
            alert_id = self.db.add_alert(
                "high_traffic", message, "critical", ip
            )
            self._send_notifications("high_traffic", message, "critical", ip)
            return alert_id
        return 0

    def notify_blocking_activated(self) -> int:
        """Alert when time-based blocking is activated."""
        return self.db.add_alert(
            "blocking_activated",
            "Time-based internet blocking is now ACTIVE",
            "info"
        )

    def notify_blocking_deactivated(self) -> int:
        """Alert when time-based blocking is deactivated."""
        return self.db.add_alert(
            "blocking_deactivated",
            "Time-based internet blocking is now INACTIVE",
            "info"
        )

    def _send_notifications(self, alert_type: str, message: str,
                            severity: str, host_ip: str) -> None:
        """Send notifications via all configured channels."""
        # Desktop notifications
        if self.config.get("alerts.desktop_notifications", True):
            self._desktop_notify(message, severity)

        # Email notifications
        if self.config.get("alerts.email_alerts", False):
            self._email_notify(message, severity)

        # Callbacks
        for cb in self.callbacks:
            try:
                cb(alert_type, message, severity, host_ip)
            except Exception:
                pass

    def _desktop_notify(self, message: str, severity: str) -> None:
        """Send desktop notification."""
        try:
            from plyer import notification
            severity_icons = {
                "info": "ℹ️",
                "warning": "⚠️",
                "critical": "🚨",
            }
            notification.notify(
                title=f"HomeNet {severity_icons.get(severity, '')}",
                message=message,
                app_name="HomeNet",
                timeout=10,
            )
        except Exception:
            pass  # plyer not available or not supported

    def _email_notify(self, message: str, severity: str) -> None:
        """Send email notification."""
        email = self.config.get("general.recovery_email", "")
        if not email:
            return

        try:
            msg = MIMEMultipart()
            msg["From"] = "HomeNet <alerts@homenetservice.local>"
            msg["To"] = email
            msg["Subject"] = f"HomeNet Alert [{severity.upper()}]"
            msg.attach(MIMEText(message, "plain"))

            # Note: SMTP configuration would need to be added
            # For now, this is a placeholder
            # server = smtplib.SMTP("smtp.gmail.com", 587)
            # server.starttls()
            # server.login(username, password)
            # server.send_message(msg)
            # server.quit()
        except Exception:
            pass

    def get_unread_count(self) -> int:
        """Get count of unread alerts."""
        return self.db.get_unread_count()

    def get_recent_alerts(self, limit: int = 20) -> list:
        """Get recent alerts."""
        return self.db.get_alerts(limit=limit)

    def mark_all_read(self) -> None:
        """Mark all alerts as read."""
        self.db.mark_alerts_read()