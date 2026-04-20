"""
HomeNet - Main Window
Main application window with sidebar navigation
"""

import customtkinter as ctk
from PIL import Image
import logging
import threading
from datetime import datetime

from .dashboard import DashboardView
from .hosts import HostsView
from .traffic import TrafficView
from .rules import RulesView
from .alerts import AlertsView
from .settings import SettingsView


class MainWindow(ctk.CTkFrame):
    """Main window with navigation sidebar."""

    def __init__(self, parent, db, config):
        super().__init__(parent, fg_color="#1A1A2E")
        self.parent = parent
        self.db = db
        self.config = config
        self.logger = logging.getLogger("HomeNet.MainWindow")

        # State
        self.current_view = None
        self.lang = config.get('language', 'en')
        self.translations = self.get_translations()

        # Components
        self.network_scanner = None
        self.traffic_monitor = None
        self.blocker = None

        self.setup_ui()
        self.load_components()
        self.show_view('dashboard')

        # Start background tasks
        self.start_background_tasks()

    def get_translations(self):
        """Get translations."""
        translations = {
            'en': {
                'dashboard': 'Dashboard',
                'hosts': 'Hosts',
                'traffic': 'Traffic',
                'rules': 'Rules',
                'alerts': 'Alerts',
                'settings': 'Settings',
                'about': 'About',
                'blocking': 'Blocking',
                'blocking_active': 'Blocking Active',
                'blocking_inactive': 'Blocking Inactive',
                'enable': 'Enable',
                'disable': 'Disable',
                'language': 'Language',
                'logout': 'Logout',
                'network': 'Network',
                'connected': 'Connected',
                'disconnected': 'Disconnected',
                'hosts_count': 'Hosts',
                'total_traffic': 'Total Traffic',
                'speed': 'Speed'
            },
            'ar': {
                'dashboard': 'لوحة التحكم',
                'hosts': 'الأجهزة',
                'traffic': 'البيانات',
                'rules': 'القواعد',
                'alerts': 'التنبيهات',
                'settings': 'الإعدادات',
                'about': 'حول',
                'blocking': 'الحظر',
                'blocking_active': 'الحظر نشط',
                'blocking_inactive': 'الحظر غير نشط',
                'enable': 'تفعيل',
                'disable': 'إلغاء',
                'language': 'اللغة',
                'logout': 'تسجيل الخروج',
                'network': 'الشبكة',
                'connected': 'متصل',
                'disconnected': 'غير متصل',
                'hosts_count': 'الأجهزة',
                'total_traffic': 'إجمالي البيانات',
                'speed': 'السرعة'
            }
        }
        return translations.get(self.lang, translations['en'])

    def setup_ui(self):
        """Setup main window UI."""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.setup_sidebar()

        # Main content area
        self.content_frame = ctk.CTkFrame(self, fg_color="#1A1A2E")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)

        # Status bar
        self.setup_status_bar()

    def setup_sidebar(self):
        """Setup sidebar navigation."""
        sidebar = ctk.CTkFrame(self, width=220, fg_color="#16213E", corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(7, weight=1)

        # Logo section
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.grid(row=0, pady=20, padx=10)

        logo_label = ctk.CTkLabel(
            logo_frame,
            text="🌐 HomeNet",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#1E88E5"
        )
        logo_label.pack()

        version_label = ctk.CTkLabel(
            logo_frame,
            text="v1.0.0 | UAE, Al Ain",
            font=ctk.CTkFont(size=10),
            text_color="#606060"
        )
        version_label.pack()

        # Navigation buttons
        self.nav_buttons = {}

        nav_items = [
            ('dashboard', '🏠', 1),
            ('hosts', '💻', 2),
            ('traffic', '📊', 3),
            ('rules', '🛡️', 4),
            ('alerts', '🔔', 5),
            ('settings', '⚙️', 6),
        ]

        for item_id, icon, row in nav_items:
            btn = ctk.CTkButton(
                sidebar,
                text=f"{icon}  {self.translations.get(item_id, item_id)}",
                anchor="w",
                height=44,
                corner_radius=8,
                fg_color="transparent",
                hover_color="#0F3460",
                text_color="#FFFFFF",
                font=ctk.CTkFont(size=14),
                command=lambda i=item_id: self.show_view(i)
            )
            btn.grid(row=row, column=0, sticky="ew", padx=10, pady=2)
            self.nav_buttons[item_id] = btn

        # Blocking toggle section
        blocking_frame = ctk.CTkFrame(sidebar, fg_color="#0F3460", corner_radius=8)
        blocking_frame.grid(row=8, padx=10, pady=10, sticky="ew")

        blocking_label = ctk.CTkLabel(
            blocking_frame,
            text=self.translations['blocking'],
            font=ctk.CTkFont(size=12),
            text_color="#B0B0B0"
        )
        blocking_label.pack(pady=(12, 4))

        self.blocking_toggle = ctk.CTkSwitch(
            blocking_frame,
            text=self.translations['blocking_inactive'],
            onvalue=1,
            offvalue=0,
            command=self.toggle_blocking,
            progress_color="#43A047"
        )
        self.blocking_toggle.pack(pady=(0, 12), padx=10)

        # Language toggle at bottom
        lang_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        lang_frame.grid(row=9, pady=10, padx=10, sticky="ew")

        lang_label = ctk.CTkLabel(
            lang_frame,
            text=f"🌍 {self.translations.get('language', 'Language')}",
            font=ctk.CTkFont(size=12),
            text_color="#B0B0B0"
        )
        lang_label.pack()

        self.lang_toggle = ctk.CTkSegmentedButton(
            lang_frame,
            values=["EN", "AR"],
            selected_color="#1E88E5",
            command=self.change_language
        )
        self.lang_toggle.pack(pady=8)
        self.lang_toggle.set("EN" if self.lang == 'en' else "AR")

    def setup_status_bar(self):
        """Setup status bar."""
        status_bar = ctk.CTkFrame(self, height=30, fg_color="#0F3460", corner_radius=0)
        status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        status_bar.grid_propagate(False)

        # Network status
        self.network_indicator = ctk.CTkLabel(
            status_bar,
            text="● " + self.translations['connected'],
            font=ctk.CTkFont(size=11),
            text_color="#43A047"
        )
        self.network_indicator.pack(side="left", padx=15, pady=2)

        # Time
        self.time_label = ctk.CTkLabel(
            status_bar,
            text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            font=ctk.CTkFont(size=11),
            text_color="#B0B0B0"
        )
        self.time_label.pack(side="right", padx=15, pady=2)

        # Update time
        self.update_time()

    def update_time(self):
        """Update status bar time."""
        if hasattr(self, 'time_label'):
            self.time_label.configure(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            self.after(1000, self.update_time)

    def load_components(self):
        """Load network components."""
        try:
            from core.network import NetworkScanner
            from core.monitor import TrafficMonitor
            from core.blocker import TrafficBlocker

            self.network_scanner = NetworkScanner()
            self.traffic_monitor = TrafficMonitor(self.db)
            self.blocker = TrafficBlocker(self.db)

            self.logger.info("Network components loaded")
        except Exception as e:
            self.logger.error(f"Error loading components: {e}")

    def start_background_tasks(self):
        """Start background monitoring tasks."""
        # Start traffic monitoring
        if self.traffic_monitor:
            self.traffic_monitor.start_monitoring(interval=5)

        # Schedule periodic network scan
        self.after(60000, self.periodic_scan)

    def periodic_scan(self):
        """Periodic network scan."""
        if self.network_scanner and hasattr(self, 'current_view'):
            try:
                hosts = self.network_scanner.full_scan()
                # Update hosts in database
                for host in hosts:
                    self.db.add_host(
                        mac_address=host.get('mac_address'),
                        ip_address=host.get('ip_address'),
                        hostname=host.get('hostname')
                    )

                # Refresh view if on hosts page
                if hasattr(self.current_view, 'refresh_hosts'):
                    self.current_view.refresh_hosts()

                # Check for new hosts
                existing_macs = {h['mac_address'] for h in self.db.get_hosts()}
                for host in hosts:
                    mac = host.get('mac_address')
                    if mac and mac not in existing_macs:
                        self.db.add_alert(
                            'new_host',
                            'New Device Connected',
                            f"A new device ({host.get('hostname', 'Unknown')}) connected to the network",
                            'warning'
                        )

            except Exception as e:
                self.logger.error(f"Periodic scan error: {e}")

        # Schedule next scan
        self.after(60000, self.periodic_scan)

    def show_view(self, view_name):
        """Show specified view."""
        # Update navigation
        for name, btn in self.nav_buttons.items():
            if name == view_name:
                btn.configure(fg_color="#1E88E5")
            else:
                btn.configure(fg_color="transparent")

        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Load view
        views = {
            'dashboard': DashboardView,
            'hosts': HostsView,
            'traffic': TrafficView,
            'rules': RulesView,
            'alerts': AlertsView,
            'settings': SettingsView,
        }

        view_class = views.get(view_name)
        if view_class:
            try:
                self.current_view = view_class(
                    self.content_frame,
                    self.db,
                    self.config,
                    self.network_scanner,
                    self.traffic_monitor,
                    self.blocker,
                    self.lang
                )
                self.current_view.pack(fill="both", expand=True)
            except Exception as e:
                self.logger.error(f"Error loading view {view_name}: {e}")

    def toggle_blocking(self):
        """Toggle blocking on/off."""
        if self.blocking_toggle.get():
            if self.blocker:
                self.blocker.enable_blocking()
                # Block all hosts marked as blocked
                hosts = self.db.get_hosts()
                for host in hosts:
                    if host.get('blocked'):
                        self.blocker.block_ip(host.get('ip_address'))
                self.blocking_toggle.configure(text=self.translations['blocking_active'])
                self.logger.info("Blocking enabled")
        else:
            if self.blocker:
                self.blocker.disable_blocking()
                self.blocking_toggle.configure(text=self.translations['blocking_inactive'])
                self.logger.info("Blocking disabled")

    def change_language(self, lang):
        """Change application language."""
        new_lang = 'en' if lang == 'EN' else 'ar'
        self.config.set('language', new_lang)
        self.lang = new_lang

        # Reload application
        self.parent.show_login()
