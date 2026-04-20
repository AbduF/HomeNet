"""
HomeNet - Alerts View
System alerts and notifications
"""

import customtkinter as ctk
import logging
from datetime import datetime


class AlertsView(ctk.CTkFrame):
    """Alerts management view."""

    def __init__(self, parent, db, config, scanner, monitor, blocker, lang='en'):
        super().__init__(parent, fg_color="#1A1A2E")
        self.parent = parent
        self.db = db
        self.config = config
        self.scanner = scanner
        self.monitor = monitor
        self.blocker = blocker
        self.lang = lang
        self.logger = logging.getLogger("HomeNet.Alerts")

        self.translations = self.get_translations()
        self.setup_ui()
        self.load_alerts()

    def get_translations(self):
        """Get translations."""
        translations = {
            'en': {
                'title': 'System Alerts',
                'all': 'All',
                'unread': 'Unread',
                'new_host': 'New Host',
                'high_traffic': 'High Traffic',
                'blocked': 'Blocked',
                'system': 'System',
                'acknowledge': 'Acknowledge',
                'acknowledge_all': 'Acknowledge All',
                'clear': 'Clear',
                'no_alerts': 'No alerts',
                'severity_info': 'Info',
                'severity_warning': 'Warning',
                'severity_critical': 'Critical',
                'time': 'Time',
                'type': 'Type',
                'message': 'Message',
                'host': 'Host'
            },
            'ar': {
                'title': 'التنبيهات النظام',
                'all': 'الكل',
                'unread': 'غير مقروء',
                'new_host': 'جهاز جديد',
                'high_traffic': 'بيانات عالية',
                'blocked': 'محظور',
                'system': 'النظام',
                'acknowledge': 'تم الاطلاع',
                'acknowledge_all': 'الاطلاع على الكل',
                'clear': 'مسح',
                'no_alerts': 'لا توجد تنبيهات',
                'severity_info': 'معلومات',
                'severity_warning': 'تحذير',
                'severity_critical': 'حرج',
                'time': 'الوقت',
                'type': 'النوع',
                'message': 'الرسالة',
                'host': 'الجهاز'
            }
        }
        return translations.get(self.lang, translations['en'])

    def setup_ui(self):
        """Setup alerts view UI."""
        # Title
        title = ctk.CTkLabel(
            self,
            text=self.translations['title'],
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFFFFF"
        )
        title.pack(anchor="w", padx=24, pady=(20, 10))

        # Toolbar
        toolbar = ctk.CTkFrame(self, fg_color="#16213E", corner_radius=8)
        toolbar.pack(fill="x", padx=20, pady=(0, 10))

        # Filter tabs
        self.filter_var = ctk.StringVar(value="all")

        all_btn = ctk.CTkButton(
            toolbar,
            text=self.translations['all'],
            width=80,
            height=32,
            corner_radius=6,
            fg_color="#1E88E5",
            command=lambda: self.filter_alerts("all")
        )
        all_btn.pack(side="left", padx=8, pady=8)

        unread_btn = ctk.CTkButton(
            toolbar,
            text=self.translations['unread'],
            width=80,
            height=32,
            corner_radius=6,
            fg_color="#0F3460",
            command=lambda: self.filter_alerts("unread")
        )
        unread_btn.pack(side="left", padx=4, pady=8)

        # Acknowledge all button
        ack_all_btn = ctk.CTkButton(
            toolbar,
            text=f"✓ {self.translations['acknowledge_all']}",
            width=140,
            height=32,
            corner_radius=6,
            fg_color="#43A047",
            command=self.acknowledge_all
        )
        ack_all_btn.pack(side="right", padx=8, pady=8)

        # Clear button
        clear_btn = ctk.CTkButton(
            toolbar,
            text=f"🗑️ {self.translations['clear']}",
            width=100,
            height=32,
            corner_radius=6,
            fg_color="#E53935",
            command=self.clear_acknowledged
        )
        clear_btn.pack(side="right", padx=8, pady=8)

        # Alerts list
        self.alerts_list = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.alerts_list.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # No alerts placeholder
        self.no_alerts_label = ctk.CTkLabel(
            self.alerts_list,
            text=f"📭 {self.translations['no_alerts']}",
            font=ctk.CTkFont(size=16),
            text_color="#606060"
        )
        self.no_alerts_label.pack(pady=40)

    def load_alerts(self):
        """Load alerts from database."""
        try:
            alerts = self.db.get_alerts(limit=100)
            self.refresh_alerts(alerts)
        except Exception as e:
            self.logger.error(f"Error loading alerts: {e}")

    def refresh_alerts(self, alerts):
        """Refresh alerts display."""
        # Clear existing
        for widget in self.alerts_list.winfo_children():
            widget.destroy()

        if not alerts:
            self.no_alerts_label = ctk.CTkLabel(
                self.alerts_list,
                text=f"📭 {self.translations['no_alerts']}",
                font=ctk.CTkFont(size=16),
                text_color="#606060"
            )
            self.no_alerts_label.pack(pady=40)
            return

        # Add alerts
        for alert in alerts:
            self.add_alert_item(alert)

    def add_alert_item(self, alert):
        """Add alert item to list."""
        severity = alert.get('severity', 'info')
        alert_type = alert.get('type', 'system')

        # Colors based on severity
        colors = {
            'info': ('#1E88E5', '#1565C0'),
            'warning': ('#FF7043', '#E64A19'),
            'critical': ('#E53935', '#C62828')
        }
        bg_color, hover_color = colors.get(severity, colors['info'])

        # Icons based on type
        icons = {
            'new_host': '🖥️',
            'high_traffic': '📊',
            'blocked': '🛡️',
            'system': '⚙️'
        }
        icon = icons.get(alert_type, '📢')

        # Unread indicator
        if not alert.get('acknowledged'):
            item = ctk.CTkFrame(self.alerts_list, fg_color="#2D2D4D", corner_radius=8)
        else:
            item = ctk.CTkFrame(self.alerts_list, fg_color="#16213E", corner_radius=8)

        item.pack(fill="x", pady=4)

        # Icon
        icon_label = ctk.CTkLabel(
            item,
            text=icon,
            font=ctk.CTkFont(size=24),
            width=50
        )
        icon_label.pack(side="left", padx=12, pady=12)

        # Content
        content = ctk.CTkFrame(item, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        # Title
        title_label = ctk.CTkLabel(
            content,
            text=alert.get('title', 'Alert'),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#FFFFFF",
            anchor="w"
        )
        title_label.pack(fill="x")

        # Message
        msg_label = ctk.CTkLabel(
            content,
            text=alert.get('message', ''),
            font=ctk.CTkFont(size=12),
            text_color="#B0B0B0",
            anchor="w",
            wraplength=500
        )
        msg_label.pack(fill="x")

        # Time and severity
        meta_frame = ctk.CTkFrame(content, fg_color="transparent")
        meta_frame.pack(fill="x", pady=(4, 0))

        # Timestamp
        timestamp = alert.get('timestamp', '')
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                time_str = str(timestamp)
        else:
            time_str = ''

        time_label = ctk.CTkLabel(
            meta_frame,
            text=f"🕐 {time_str}",
            font=ctk.CTkFont(size=10),
            text_color="#808080"
        )
        time_label.pack(side="left")

        # Severity badge
        severity_label = ctk.CTkLabel(
            meta_frame,
            text=self.translations.get(f'severity_{severity}', severity.upper()),
            font=ctk.CTkFont(size=10),
            text_color="#FFFFFF",
            fg_color=bg_color,
            corner_radius=4,
            width=70,
            height=18
        )
        severity_label.pack(side="right")

        # Acknowledge button
        if not alert.get('acknowledged'):
            ack_btn = ctk.CTkButton(
                item,
                text=f"✓ {self.translations['acknowledge']}",
                width=100,
                height=32,
                corner_radius=6,
                fg_color=bg_color,
                hover_color=hover_color,
                command=lambda a=alert: self.acknowledge_alert(a)
            )
            ack_btn.pack(side="right", padx=12, pady=8)

    def filter_alerts(self, filter_type):
        """Filter alerts."""
        try:
            if filter_type == "unread":
                alerts = self.db.get_alerts(acknowledged=False)
            else:
                alerts = self.db.get_alerts()

            self.refresh_alerts(alerts)
        except Exception as e:
            self.logger.error(f"Error filtering alerts: {e}")

    def acknowledge_alert(self, alert):
        """Acknowledge single alert."""
        self.db.acknowledge_alert(alert['id'])
        self.load_alerts()

    def acknowledge_all(self):
        """Acknowledge all alerts."""
        self.db.acknowledge_all_alerts()
        self.load_alerts()

    def clear_acknowledged(self):
        """Clear acknowledged alerts."""
        # This would need a delete method in database
        self.load_alerts()
