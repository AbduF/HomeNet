"""
HomeNet - Dashboard View
Main dashboard with network overview
"""

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import logging
from datetime import datetime


class DashboardView(ctk.CTkFrame):
    """Dashboard view with network overview."""

    def __init__(self, parent, db, config, scanner, monitor, blocker, lang='en'):
        super().__init__(parent, fg_color="#1A1A2E")
        self.parent = parent
        self.db = db
        self.config = config
        self.scanner = scanner
        self.monitor = monitor
        self.blocker = blocker
        self.lang = lang
        self.logger = logging.getLogger("HomeNet.Dashboard")

        self.translations = self.get_translations()
        self.setup_ui()
        self.refresh_data()

    def get_translations(self):
        """Get translations."""
        translations = {
            'en': {
                'title': 'Dashboard',
                'overview': 'Network Overview',
                'hosts': 'Active Hosts',
                'blocking': 'Blocking Status',
                'traffic': 'Traffic Summary',
                'recent_alerts': 'Recent Alerts',
                'download': 'Download',
                'upload': 'Upload',
                'speed': 'Speed',
                'total': 'Total',
                'blocked': 'Blocked',
                'trusted': 'Trusted',
                'active': 'Active',
                'inactive': 'Inactive',
                'quick_actions': 'Quick Actions',
                'scan_network': 'Scan Network',
                'run_speedtest': 'Speed Test',
                'clear_alerts': 'Clear Alerts',
                'no_alerts': 'No recent alerts'
            },
            'ar': {
                'title': 'لوحة التحكم',
                'overview': 'نظرة عامة على الشبكة',
                'hosts': 'الأجهزة النشطة',
                'blocking': 'حالة الحظر',
                'traffic': 'ملخص البيانات',
                'recent_alerts': 'التنبيهات الأخيرة',
                'download': 'تحميل',
                'upload': 'رفع',
                'speed': 'السرعة',
                'total': 'الإجمالي',
                'blocked': 'محظور',
                'trusted': 'موثوق',
                'active': 'نشط',
                'inactive': 'غير نشط',
                'quick_actions': 'إجراءات سريعة',
                'scan_network': 'فحص الشبكة',
                'run_speedtest': 'اختبار السرعة',
                'clear_alerts': 'مسح التنبيهات',
                'no_alerts': 'لا توجد تنبيهات'
            }
        }
        return translations.get(self.lang, translations['en'])

    def setup_ui(self):
        """Setup dashboard UI."""
        # Title
        title = ctk.CTkLabel(
            self,
            text=self.translations['title'],
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFFFFF"
        )
        title.pack(anchor="w", padx=24, pady=(20, 10))

        # Main content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=10)

        # Configure grid
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        content.grid_columnconfigure(2, weight=1)
        content.grid_rowconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)

        # Stats cards row
        self.create_stat_card(content, 0, 0, "hosts", "💻", self.translations['hosts'], "0")
        self.create_stat_card(content, 0, 1, "blocking", "🛡️", self.translations['blocking'], self.translations['inactive'])
        self.create_stat_card(content, 0, 2, "alerts", "🔔", self.translations['recent_alerts'], "0")

        # Speed card
        self.create_speed_card(content, 1, 0)

        # Traffic card
        self.create_traffic_card(content, 1, 1)

        # Quick actions card
        self.create_actions_card(content, 1, 2)

    def create_stat_card(self, parent, row, col, card_id, icon, title, value):
        """Create a statistics card."""
        card = ctk.CTkFrame(parent, fg_color="#16213E", corner_radius=12)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        # Icon
        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=36)
        )
        icon_label.pack(pady=(20, 10))

        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14),
            text_color="#B0B0B0"
        )
        title_label.pack()

        # Value
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#1E88E5"
        )
        value_label.pack(pady=(10, 20))

        # Store reference
        setattr(self, f"{card_id}_value", value_label)

    def create_speed_card(self, parent, row, col):
        """Create speed monitoring card."""
        card = ctk.CTkFrame(parent, fg_color="#16213E", corner_radius=12)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        # Title
        title = ctk.CTkLabel(
            card,
            text=f"📡 {self.translations['speed']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#FFFFFF"
        )
        title.pack(anchor="w", padx=16, pady=(16, 8))

        # Speed labels
        self.download_label = ctk.CTkLabel(
            card,
            text=f"↓ {self.translations['download']}: 0 Mbps",
            font=ctk.CTkFont(size=14),
            text_color="#43A047"
        )
        self.download_label.pack(anchor="w", padx=16, pady=4)

        self.upload_label = ctk.CTkLabel(
            card,
            text=f"↑ {self.translations['upload']}: 0 Mbps",
            font=ctk.CTkFont(size=14),
            text_color="#FF7043"
        )
        self.upload_label.pack(anchor="w", padx=16, pady=4)

        # Update button
        update_btn = ctk.CTkButton(
            card,
            text=self.translations['run_speedtest'],
            width=120,
            height=32,
            corner_radius=8,
            fg_color="#1E88E5",
            command=self.run_speedtest
        )
        update_btn.pack(pady=16)

        # Store reference
        self.speed_card = card

    def create_traffic_card(self, parent, row, col):
        """Create traffic summary card."""
        card = ctk.CTkFrame(parent, fg_color="#16213E", corner_radius=12)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        # Title
        title = ctk.CTkLabel(
            card,
            text=f"📊 {self.translations['traffic']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#FFFFFF"
        )
        title.pack(anchor="w", padx=16, pady=(16, 8))

        # Total
        self.total_label = ctk.CTkLabel(
            card,
            text=f"{self.translations['total']}: 0 MB",
            font=ctk.CTkFont(size=14),
            text_color="#FFFFFF"
        )
        self.total_label.pack(anchor="w", padx=16, pady=4)

        # Host breakdown
        self.top_host_label = ctk.CTkLabel(
            card,
            text="Top: -",
            font=ctk.CTkFont(size=12),
            text_color="#B0B0B0"
        )
        self.top_host_label.pack(anchor="w", padx=16, pady=4)

        # Update button
        update_btn = ctk.CTkButton(
            card,
            text="↻ Refresh",
            width=120,
            height=32,
            corner_radius=8,
            fg_color="#0F3460",
            command=self.refresh_data
        )
        update_btn.pack(pady=16)

    def create_actions_card(self, parent, row, col):
        """Create quick actions card."""
        card = ctk.CTkFrame(parent, fg_color="#16213E", corner_radius=12)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        # Title
        title = ctk.CTkLabel(
            card,
            text=f"⚡ {self.translations['quick_actions']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#FFFFFF"
        )
        title.pack(anchor="w", padx=16, pady=(16, 16))

        # Buttons
        scan_btn = ctk.CTkButton(
            card,
            text=f"🔍 {self.translations['scan_network']}",
            width=180,
            height=40,
            corner_radius=8,
            fg_color="#1E88E5",
            anchor="w",
            command=self.scan_network
        )
        scan_btn.pack(pady=6, padx=16)

        speedtest_btn = ctk.CTkButton(
            card,
            text=f"📡 {self.translations['run_speedtest']}",
            width=180,
            height=40,
            corner_radius=8,
            fg_color="#43A047",
            anchor="w",
            command=self.run_speedtest
        )
        speedtest_btn.pack(pady=6, padx=16)

        alerts_btn = ctk.CTkButton(
            card,
            text=f"🔔 {self.translations['clear_alerts']}",
            width=180,
            height=40,
            corner_radius=8,
            fg_color="#FF7043",
            anchor="w",
            command=self.clear_alerts
        )
        alerts_btn.pack(pady=6, padx=16)

    def refresh_data(self):
        """Refresh dashboard data."""
        try:
            # Get hosts count
            hosts = self.db.get_hosts()
            active_hosts = len([h for h in hosts if h.get('last_seen')])

            # Update hosts count
            if hasattr(self, 'hosts_value'):
                self.hosts_value.configure(text=str(active_hosts))

            # Update blocking status
            blocking_active = self.blocker and self.blocker.is_blocking_active()
            if hasattr(self, 'blocking_value'):
                status = self.translations['active'] if blocking_active else self.translations['inactive']
                color = "#43A047" if blocking_active else "#E53935"
                self.blocking_value.configure(text=status, text_color=color)

            # Get alerts count
            alerts = self.db.get_alerts(acknowledged=False)
            if hasattr(self, 'alerts_value'):
                self.alerts_value.configure(text=str(len(alerts)))

            # Update traffic stats
            stats = self.monitor.get_total_traffic() if self.monitor else None
            if stats:
                total = self.monitor.format_bytes(stats.get('bytes_received', 0) + stats.get('bytes_sent', 0))
                if hasattr(self, 'total_label'):
                    self.total_label.configure(text=f"{self.translations['total']}: {total}")

            # Update speed
            if self.monitor:
                speed = self.monitor.get_speed(interval=1)
                if speed and hasattr(self, 'download_label'):
                    down = f"{speed['download_speed_mbps']:.1f}"
                    up = f"{speed['upload_speed_mbps']:.1f}"
                    self.download_label.configure(text=f"↓ {self.translations['download']}: {down} Mbps")
                    self.upload_label.configure(text=f"↑ {self.translations['upload']}: {up} Mbps")

            # Get top consumer
            top_consumers = self.db.get_top_consumers(limit=1)
            if top_consumers and hasattr(self, 'top_host_label'):
                top = top_consumers[0]
                hostname = top.get('hostname', 'Unknown')
                self.top_host_label.configure(text=f"Top: {hostname}")

        except Exception as e:
            self.logger.error(f"Error refreshing data: {e}")

        # Schedule next refresh
        self.after(5000, self.refresh_data)

    def scan_network(self):
        """Scan network for devices."""
        if not self.scanner:
            return

        try:
            hosts = self.scanner.full_scan()

            # Update database
            for host in hosts:
                self.db.add_host(
                    mac_address=host.get('mac_address'),
                    ip_address=host.get('ip_address'),
                    hostname=host.get('hostname')
                )

            # Update display
            if hasattr(self, 'hosts_value'):
                self.hosts_value.configure(text=str(len(hosts)))

            self.logger.info(f"Network scan complete: {len(hosts)} hosts found")

        except Exception as e:
            self.logger.error(f"Scan error: {e}")

    def run_speedtest(self):
        """Run internet speed test."""
        try:
            from core.speedtest import SpeedTest
            st = SpeedTest()
            result = st.run_test()

            if result and hasattr(self, 'download_label'):
                down = f"{result['download_mbps']:.1f}"
                up = f"{result['upload_mbps']:.1f}"
                self.download_label.configure(text=f"↓ {self.translations['download']}: {down} Mbps")
                self.upload_label.configure(text=f"↑ {self.translations['upload']}: {up} Mbps")

        except Exception as e:
            self.logger.error(f"Speed test error: {e}")

    def clear_alerts(self):
        """Clear all alerts."""
        self.db.acknowledge_all_alerts()
        if hasattr(self, 'alerts_value'):
            self.alerts_value.configure(text="0")
