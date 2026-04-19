"""
HomeNet — Modern Graphical User Interface
Built with CustomTkinter for a modern, responsive UI with full Arabic support.
"""

import tkinter as tk
import customtkinter as ctk
import threading
import time
import platform
from typing import Optional
from pathlib import Path

from .config import ConfigManager
from .database import DatabaseManager, init_db
from .network_scanner import NetworkScanner
from .traffic_monitor import TrafficMonitor
from .firewall_rules import FirewallManager
from .speed_test import SpeedTester
from .alerts import AlertManager
from .auth import AuthManager
from .utils import format_bytes, check_internet_connection, get_system_info
from .translations import TranslationManager

# Configure CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class HomeNetGUI(ctk.CTk):
    """Main HomeNet GUI Application."""

    def __init__(self):
        super().__init__()

        # Initialize managers
        self.db = init_db()
        self.config = ConfigManager()
        self.scanner = NetworkScanner()
        self.monitor = TrafficMonitor()
        self.firewall = FirewallManager(self.config, self.db)
        self.speed_tester = SpeedTester(self.db)
        self.alerts = AlertManager(self.db, self.config)
        self.auth = AuthManager(self.db)

        lang = self.config.get("general.language", "en")
        self.translations = TranslationManager(lang)
        self._ = self.translations.get

        # Window setup
        self.title(self._("app_title"))
        self.geometry("1200x750")
        self.minsize(900, 600)

        # RTL support for Arabic
        if self.translations.is_rtl():
            self.configure(direction="rtl")

        # Login state
        self.authenticated = False

        # Build UI
        self._build_ui()

        # Show login screen first
        self._show_login()

    def _build_ui(self):
        """Build the main UI layout."""
        # Main container
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Navigation frame
        self.nav_frame = ctk.CTkFrame(self.main_frame, width=200)
        self.nav_frame.pack(side="left", fill="y", padx=(0, 10))
        self.nav_frame.pack_propagate(False)

        # Content frame
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(side="right", fill="both", expand=True)

        # Build navigation
        self._build_navigation()

        # Build content pages (hidden initially)
        self._build_pages()

    def _build_navigation(self):
        """Build navigation sidebar."""
        # Logo/Title
        title_frame = ctk.CTkFrame(self.nav_frame)
        title_frame.pack(fill="x", padx=10, pady=(10, 20))

        ctk.CTkLabel(
            title_frame, text="🌐 HomeNet",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=5)

        ctk.CTkLabel(
            title_frame, text=self._("app_subtitle"),
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack()

        # Navigation buttons
        nav_items = [
            ("📊", self._("dashboard"), self._show_dashboard),
            ("🖥️", self._("hosts"), self._show_hosts),
            ("", self._("traffic"), self._show_traffic),
            ("🚫", self._("blocking"), self._show_blocking),
            ("🕐", self._("time_rules"), self._show_time_rules),
            ("📡", self._("speed_test"), self._show_speed_test),
            ("", self._("alerts"), self._show_alerts),
            ("⚙️", self._("settings"), self._show_settings),
            ("💻", self._("system"), self._show_system),
        ]

        for icon, label, command in nav_items:
            btn = ctk.CTkButton(
                self.nav_frame,
                text=f"  {icon}  {label}",
                command=command,
                fg_color="transparent",
                hover_color=("gray25", "gray35"),
                anchor="w",
                height=40,
            )
            btn.pack(fill="x", padx=5, pady=2)

        # Footer
        footer = ctk.CTkLabel(
            self.nav_frame,
            text=self._("footer"),
            font=ctk.CTkFont(size=9),
            text_color="gray50",
            justify="center",
        )
        footer.pack(side="bottom", pady=20, padx=10)

        # Language toggle
        lang_btn = ctk.CTkButton(
            self.nav_frame,
            text="🌍 EN / عربي",
            command=self._toggle_language,
            fg_color="transparent",
            hover_color=("gray25", "gray35"),
            height=30,
        )
        lang_btn.pack(side="bottom", pady=5)

    def _build_pages(self):
        """Build all content pages."""
        self.pages = {}

        # Dashboard page
        self.pages["dashboard"] = self._create_dashboard_page()

        # Hosts page
        self.pages["hosts"] = self._create_hosts_page()

        # Traffic page
        self.pages["traffic"] = self._create_traffic_page()

        # Blocking page
        self.pages["blocking"] = self._create_blocking_page()

        # Time Rules page
        self.pages["time_rules"] = self._create_time_rules_page()

        # Speed Test page
        self.pages["speed_test"] = self._create_speed_test_page()

        # Alerts page
        self.pages["alerts"] = self._create_alerts_page()

        # Settings page
        self.pages["settings"] = self._create_settings_page()

        # System page
        self.pages["system"] = self._create_system_page()

    # ─── Page Creators ───────────────────────────────────────────────────

    def _create_dashboard_page(self) -> ctk.CTkFrame:
        """Create dashboard page."""
        page = ctk.CTkFrame(self.content_frame)

        # Welcome banner
        banner = ctk.CTkFrame(page, fg_color=("blue", "darkblue"))
        banner.pack(fill="x", pady=(10, 20), padx=10)
        ctk.CTkLabel(
            banner, text=self._("welcome"),
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(pady=15)

        # Stats cards
        cards_frame = ctk.CTkFrame(page)
        cards_frame.pack(fill="x", padx=10, pady=10)

        self.card_total = self._create_stat_card(
            cards_frame, self._("total_hosts"), "0", "🖥️", row=0, col=0
        )
        self.card_active = self._create_stat_card(
            cards_frame, self._("active_hosts"), "0", "✅", row=0, col=1
        )
        self.card_blocked = self._create_stat_card(
            cards_frame, self._("blocked_hosts"), "0", "🚫", row=0, col=2
        )
        self.card_traffic = self._create_stat_card(
            cards_frame, self._("total_traffic"), "0 B", "📊", row=0, col=3
        )

        # Network status
        status_frame = ctk.CTkFrame(page)
        status_frame.pack(fill="x", padx=10, pady=10)

        self.lbl_connection = ctk.CTkLabel(
            status_frame, text=f"🌐 {self._('network_status')}: ---",
            font=ctk.CTkFont(size=14)
        )
        self.lbl_connection.pack(pady=5)

        self.lbl_blocking = ctk.CTkLabel(
            status_frame, text=f"🕐 {self._('time_blocking')}: ---",
            font=ctk.CTkFont(size=14)
        )
        self.lbl_blocking.pack(pady=5)

        self.lbl_time = ctk.CTkLabel(
            status_frame, text=f"🕐 {self._('current_time')}: ---",
            font=ctk.CTkFont(size=14)
        )
        self.lbl_time.pack(pady=5)

        # Quick actions
        actions_frame = ctk.CTkFrame(page)
        actions_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(
            actions_frame, text=f"🔍 {self._('scan_network')}",
            command=self._quick_scan, width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            actions_frame, text=f"📡 {self._('run_speed_test')}",
            command=self._quick_speed_test, width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            actions_frame, text=f"🔄 {self._('refresh')}",
            command=self._refresh_dashboard, width=150
        ).pack(side="left", padx=5)

        return page

    def _create_stat_card(self, parent, title, value, icon, row, col):
        """Create a statistics card widget."""
        card = ctk.CTkFrame(parent, width=200, height=120)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)

        ctk.CTkLabel(
            card, text=icon, font=ctk.CTkFont(size=30)
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            card, text=title, font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack()

        lbl = ctk.CTkLabel(
            card, text=value, font=ctk.CTkFont(size=24, weight="bold")
        )
        lbl.pack(pady=(5, 15))

        return {"frame": card, "label": lbl}

    def _create_hosts_page(self) -> ctk.CTkFrame:
        """Create hosts/devices page."""
        page = ctk.CTkFrame(self.content_frame)

        # Header
        header = ctk.CTkFrame(page)
        header.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            header, text=f"🖥️ {self._('hosts')}",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            header, text=f" {self._('scan_network')}",
            command=self._scan_network
        ).pack(side="right", padx=10)

        ctk.CTkButton(
            header, text=f"🔄 {self._('refresh')}",
            command=self._refresh_hosts
        ).pack(side="right", padx=5)

        # Hosts table
        table_frame = ctk.CTkFrame(page)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Table header
        headers_frame = ctk.CTkFrame(table_frame, fg_color=("gray30", "gray20"))
        headers_frame.pack(fill="x")

        headers = [
            self._("ip_address"), self._("mac_address"), self._("hostname"),
            self._("os_type"), self._("hardware"), self._("status"), self._("actions")
        ]
        for i, h in enumerate(headers):
            ctk.CTkLabel(
                headers_frame, text=h, font=ctk.CTkFont(weight="bold"),
                width=150
            ).grid(row=0, column=i, padx=5, pady=5, sticky="w")

        # Scrollable host list
        self.hosts_scroll = ctk.CTkScrollableFrame(table_frame, height=400)
        self.hosts_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        return page

    def _create_traffic_page(self) -> ctk.CTkFrame:
        """Create traffic monitoring page."""
        page = ctk.CTkFrame(self.content_frame)

        # Header
        header = ctk.CTkFrame(page)
        header.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            header, text=f"📈 {self._('traffic')}",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left", padx=10)

        self.btn_monitor = ctk.CTkButton(
            header, text=f"▶ {self._('start_monitoring')}",
            command=self._toggle_monitoring
        )
        self.btn_monitor.pack(side="right", padx=10)

        # Traffic table
        table_frame = ctk.CTkFrame(page)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        headers_frame = ctk.CTkFrame(table_frame, fg_color=("gray30", "gray20"))
        headers_frame.pack(fill="x")

        headers = [
            self._("ip_address"), self._("hostname"),
            self._("bytes_sent"), self._("bytes_recv"), self._("total_bytes")
        ]
        for i, h in enumerate(headers):
            ctk.CTkLabel(
                headers_frame, text=h, font=ctk.CTkFont(weight="bold"),
                width=180
            ).grid(row=0, column=i, padx=5, pady=5, sticky="w")

        self.traffic_scroll = ctk.CTkScrollableFrame(table_frame, height=400)
        self.traffic_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        return page

    def _create_blocking_page(self) -> ctk.CTkFrame:
        """Create content blocking page."""
        page = ctk.CTkFrame(self.content_frame)

        ctk.CTkLabel(
            page, text=f"🚫 {self._('blocking')}",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)

        # Category toggles
        categories_frame = ctk.CTkFrame(page)
        categories_frame.pack(fill="x", padx=20, pady=10)

        self.switches = {}
        for cat_key, cat_label, icon in [
            ("gaming", self._("block_gaming"), "🎮"),
            ("social_media", self._("block_social"), "📱"),
            ("streaming", self._("block_streaming"), "📺"),
        ]:
            row = ctk.CTkFrame(categories_frame)
            row.pack(fill="x", pady=5)

            ctk.CTkLabel(row, text=f"{icon} {cat_label}", width=200).pack(side="left", padx=10)

            enabled = self.config.get(f"categories.{cat_key}.enabled", False)
            switch = ctk.CTkSwitch(
                row, text="",
                command=lambda k=cat_key: self._toggle_category(k)
            )
            switch.pack(side="right", padx=10)
            if enabled:
                switch.select()
            self.switches[cat_key] = switch

        # Custom rules
        rules_frame = ctk.CTkFrame(page)
        rules_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            rules_frame, text=self._("custom_rules"),
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=5)

        rule_input_frame = ctk.CTkFrame(rules_frame)
        rule_input_frame.pack(fill="x", pady=5)

        self.rule_type_var = ctk.StringVar(value="host")
        ctk.CTkOptionMenu(
            rule_input_frame, variable=self.rule_type_var,
            values=[self._("rule_host"), self._("rule_domain"), self._("rule_port")]
        ).pack(side="left", padx=5)

        self.rule_target_entry = ctk.CTkEntry(rule_input_frame, width=200,
                                               placeholder_text=self._("target"))
        self.rule_target_entry.pack(side="left", padx=5)

        ctk.CTkButton(
            rule_input_frame, text=f"➕ {self._('add_rule')}",
            command=self._add_rule
        ).pack(side="left", padx=5)

        # Rules list
        self.rules_scroll = ctk.CTkScrollableFrame(page, height=200)
        self.rules_scroll.pack(fill="both", expand=True, padx=20, pady=10)
        self._refresh_rules()

        return page

    def _create_time_rules_page(self) -> ctk.CTkFrame:
        """Create time-based blocking rules page."""
        page = ctk.CTkFrame(self.content_frame)

        ctk.CTkLabel(
            page, text=f"🕐 {self._('time_rules')}",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)

        # Enable toggle
        enable_frame = ctk.CTkFrame(page)
        enable_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            enable_frame, text=self._("enable_time_blocking"),
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=10)

        tb_enabled = self.config.get("time_blocking.enabled", False)
        self.time_block_switch = ctk.CTkSwitch(
            enable_frame, text="",
            command=self._toggle_time_blocking
        )
        self.time_block_switch.pack(side="right", padx=10)
        if tb_enabled:
            self.time_block_switch.select()

        # Time inputs
        time_frame = ctk.CTkFrame(page)
        time_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(time_frame, text=self._("block_start")).pack(side="left", padx=5)
        self.block_start_entry = ctk.CTkEntry(
            time_frame, width=100,
            placeholder_text="23:00"
        )
        self.block_start_entry.pack(side="left", padx=5)
        self.block_start_entry.insert(0, self.config.get("time_blocking.block_start", "23:00"))

        ctk.CTkLabel(time_frame, text=self._("block_end")).pack(side="left", padx=5)
        self.block_end_entry = ctk.CTkEntry(
            time_frame, width=100,
            placeholder_text="00:00"
        )
        self.block_end_entry.pack(side="left", padx=5)
        self.block_end_entry.insert(0, self.config.get("time_blocking.block_end", "00:00"))

        ctk.CTkButton(
            time_frame, text=self._("save_changes"),
            command=self._save_time_rules
        ).pack(side="left", padx=10)

        # Days selection
        days_frame = ctk.CTkFrame(page)
        days_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            days_frame, text=self._("block_days"),
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=5)

        self.day_checkboxes = {}
        days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        day_names = [
            self._("monday"), self._("tuesday"), self._("wednesday"),
            self._("thursday"), self._("friday"), self._("saturday"), self._("sunday")
        ]

        days_row = ctk.CTkFrame(days_frame)
        days_row.pack(fill="x")

        for i, (day, name) in enumerate(zip(days, day_names)):
            cb = ctk.CTkCheckBox(days_row, text=name)
            cb.grid(row=0, column=i, padx=5, pady=5)
            if day in self.config.get("time_blocking.block_days", []):
                cb.select()
            self.day_checkboxes[day] = cb

        # Whitelist
        wl_frame = ctk.CTkFrame(page)
        wl_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            wl_frame, text=self._("whitelisted_hosts"),
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=5)

        wl_input_frame = ctk.CTkFrame(wl_frame)
        wl_input_frame.pack(fill="x", pady=5)

        self.wl_entry = ctk.CTkEntry(wl_input_frame, width=200,
                                      placeholder_text="192.168.1.x")
        self.wl_entry.pack(side="left", padx=5)

        ctk.CTkButton(
            wl_input_frame, text=f"➕ {self._('add_whitelist')}",
            command=self._add_whitelist
        ).pack(side="left", padx=5)

        return page

    def _create_speed_test_page(self) -> ctk.CTkFrame:
        """Create speed test page."""
        page = ctk.CTkFrame(self.content_frame)

        ctk.CTkLabel(
            page, text=f" {self._('speed_test')}",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)

        # Run button
        self.btn_speed_test = ctk.CTkButton(
            page, text=f"🚀 {self._('run_speed_test')}",
            command=self._run_speed_test_gui,
            width=200, height=50,
            font=ctk.CTkFont(size=16)
        )
        self.btn_speed_test.pack(pady=20)

        # Results display
        results_frame = ctk.CTkFrame(page)
        results_frame.pack(fill="x", padx=40, pady=10)

        self.speed_results = {
            "download": ctk.CTkLabel(results_frame, text=f"⬇ {self._('download_speed')}: ---",
                                      font=ctk.CTkFont(size=18)),
            "upload": ctk.CTkLabel(results_frame, text=f"⬆ {self._('upload_speed')}: ---",
                                    font=ctk.CTkFont(size=18)),
            "ping": ctk.CTkLabel(results_frame, text=f"📶 {self._('ping')}: ---",
                                  font=ctk.CTkFont(size=18)),
            "server": ctk.CTkLabel(results_frame, text=f"🖥️ {self._('server')}: ---",
                                    font=ctk.CTkFont(size=14), text_color="gray"),
        }

        for lbl in self.speed_results.values():
            lbl.pack(pady=5)

        # History
        ctk.CTkLabel(
            page, text=self._("test_history"),
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(20, 10))

        self.speed_history_scroll = ctk.CTkScrollableFrame(page, height=200)
        self.speed_history_scroll.pack(fill="both", expand=True, padx=20, pady=10)
        self._refresh_speed_history()

        return page

    def _create_alerts_page(self) -> ctk.CTkFrame:
        """Create alerts page."""
        page = ctk.CTkFrame(self.content_frame)

        header = ctk.CTkFrame(page)
        header.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            header, text=f"🔔 {self._('alerts')}",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            header, text=self._("mark_all_read"),
            command=self._mark_alerts_read
        ).pack(side="right", padx=10)

        ctk.CTkButton(
            header, text=f"🔄 {self._('refresh')}",
            command=self._refresh_alerts
        ).pack(side="right", padx=5)

        self.alerts_scroll = ctk.CTkScrollableFrame(page, height=500)
        self.alerts_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        self._refresh_alerts()

        return page

    def _create_settings_page(self) -> ctk.CTkFrame:
        """Create settings page."""
        page = ctk.CTkFrame(self.content_frame)

        ctk.CTkLabel(
            page, text=f"⚙️ {self._('settings')}",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)

        # Language
        lang_frame = ctk.CTkFrame(page)
        lang_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(lang_frame, text=self._("language"), width=150).pack(side="left", padx=10)
        lang_var = ctk.StringVar(value="arabic" if self.translations.is_rtl() else "english")
        lang_menu = ctk.CTkOptionMenu(
            lang_frame, variable=lang_var,
            values=[self._("english"), self._("arabic")],
            command=self._change_language
        )
        lang_menu.pack(side="left", padx=10)

        # Network interface
        iface_frame = ctk.CTkFrame(page)
        iface_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(iface_frame, text=self._("network_interface"), width=150).pack(side="left", padx=10)
        self.iface_entry = ctk.CTkEntry(iface_frame, width=200)
        self.iface_entry.pack(side="left", padx=10)
        self.iface_entry.insert(0, self.config.get("general.interface", "eth0"))

        ctk.CTkButton(
            iface_frame, text=self._("save_changes"),
            command=self._save_interface
        ).pack(side="left", padx=10)

        return page

    def _create_system_page(self) -> ctk.CTkFrame:
        """Create system information page."""
        page = ctk.CTkFrame(self.content_frame)

        ctk.CTkLabel(
            page, text=f"💻 {self._('system')}",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)

        # Admin settings
        admin_frame = ctk.CTkFrame(page)
        admin_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            admin_frame, text=self._("admin_settings"),
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=5)

        # Username
        user_frame = ctk.CTkFrame(admin_frame)
        user_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(user_frame, text=self._("current_username"), width=150).pack(side="left", padx=5)
        self.current_user_lbl = ctk.CTkLabel(user_frame, text="admin")
        self.current_user_lbl.pack(side="left", padx=5)

        ctk.CTkLabel(user_frame, text=self._("new_username"), width=120).pack(side="left", padx=5)
        self.new_user_entry = ctk.CTkEntry(user_frame, width=150)
        self.new_user_entry.pack(side="left", padx=5)

        ctk.CTkButton(
            user_frame, text=self._("change_username"),
            command=self._change_username
        ).pack(side="left", padx=5)

        # Password
        pass_frame = ctk.CTkFrame(admin_frame)
        pass_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(pass_frame, text=self._("change_password"), width=150).pack(side="left", padx=5)

        ctk.CTkLabel(pass_frame, text=self._("current_password"), width=120).pack(side="left", padx=5)
        self.curr_pass_entry = ctk.CTkEntry(pass_frame, width=120, show="*")
        self.curr_pass_entry.pack(side="left", padx=5)

        ctk.CTkLabel(pass_frame, text=self._("new_password"), width=100).pack(side="left", padx=5)
        self.new_pass_entry = ctk.CTkEntry(pass_frame, width=120, show="*")
        self.new_pass_entry.pack(side="left", padx=5)

        ctk.CTkButton(
            pass_frame, text=self._("change_password"),
            command=self._change_password
        ).pack(side="left", padx=5)

        # Email
        email_frame = ctk.CTkFrame(admin_frame)
        email_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(email_frame, text=self._("recovery_email"), width=150).pack(side="left", padx=5)
        self.email_entry = ctk.CTkEntry(email_frame, width=250)
        self.email_entry.pack(side="left", padx=5)
        self.email_entry.insert(0, self.config.get("general.recovery_email", ""))

        ctk.CTkButton(
            email_frame, text=self._("set_email"),
            command=self._set_email
        ).pack(side="left", padx=5)

        # System info
        sys_frame = ctk.CTkFrame(page)
        sys_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            sys_frame, text=self._("system_info"),
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=5)

        self.sys_info_label = ctk.CTkLabel(sys_frame, text="", justify="left")
        self.sys_info_label.pack(anchor="w", pady=5)
        self._refresh_system_info()

        return page

    # ─── Login Screen ────────────────────────────────────────────────────

    def _show_login(self):
        """Show login screen."""
        login_frame = ctk.CTkFrame(self, width=400, height=300)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            login_frame, text="🌐 HomeNet",
            font=ctk.CTkFont(size=32, weight="bold")
        ).pack(pady=(30, 10))

        ctk.CTkLabel(
            login_frame, text=self._("app_subtitle"),
            font=ctk.CTkFont(size=12), text_color="gray"
        ).pack(pady=(0, 30))

        ctk.CTkLabel(login_frame, text=self._("username")).pack(pady=(0, 5))
        self.login_user_entry = ctk.CTkEntry(login_frame, width=250)
        self.login_user_entry.pack(pady=(0, 15))
        self.login_user_entry.insert(0, "admin")

        ctk.CTkLabel(login_frame, text=self._("password")).pack(pady=(0, 5))
        self.login_pass_entry = ctk.CTkEntry(login_frame, width=250, show="*")
        self.login_pass_entry.pack(pady=(0, 15))
        self.login_pass_entry.insert(0, "123456")

        self.login_error_lbl = ctk.CTkLabel(
            login_frame, text="", text_color="red", font=ctk.CTkFont(size=11)
        )
        self.login_error_lbl.pack(pady=(0, 10))

        ctk.CTkButton(
            login_frame, text=self._("login_btn"),
            command=self._do_login, width=200, height=40
        ).pack(pady=10)

        # Forgot password
        forgot_frame = ctk.CTkFrame(login_frame, fg_color="transparent")
        forgot_frame.pack(pady=(10, 20))

        ctk.CTkLabel(
            forgot_frame, text=self._("forgot_password"),
            text_color="gray", cursor="hand2"
        ).pack(side="left")

        self.login_frame = login_frame

    def _do_login(self):
        """Process login."""
        username = self.login_user_entry.get()
        password = self.login_pass_entry.get()

        token = self.auth.login(username, password)
        if token:
            self.authenticated = True
            self.login_frame.destroy()
            self._refresh_dashboard()
        else:
            self.login_error_lbl.configure(text=self._("login_failed"))

    # ─── Navigation ──────────────────────────────────────────────────────

    def _show_page(self, page_name):
        """Show a specific page."""
        for name, page in self.pages.items():
            if name == page_name:
                page.pack(fill="both", expand=True)
            else:
                page.pack_forget()

    def _show_dashboard(self):
        self._show_page("dashboard")
        self._refresh_dashboard()

    def _show_hosts(self):
        self._show_page("hosts")
        self._refresh_hosts()

    def _show_traffic(self):
        self._show_page("traffic")
        self._refresh_traffic()

    def _show_blocking(self):
        self._show_page("blocking")
        self._refresh_rules()

    def _show_time_rules(self):
        self._show_page("time_rules")

    def _show_speed_test(self):
        self._show_page("speed_test")
        self._refresh_speed_history()

    def _show_alerts(self):
        self._show_page("alerts")
        self._refresh_alerts()

    def _show_settings(self):
        self._show_page("settings")

    def _show_system(self):
        self._show_page("system")
        self._refresh_system_info()

    # ─── Action Handlers ─────────────────────────────────────────────────

    def _refresh_dashboard(self):
        """Refresh dashboard data."""
        hosts = self.db.get_all_hosts()
        active = [h for h in hosts if not h["is_blocked"]]
        blocked = [h for h in hosts if h["is_blocked"]]

        self.card_total["label"].configure(text=str(len(hosts)))
        self.card_active["label"].configure(text=str(len(active)))
        self.card_blocked["label"].configure(text=str(len(blocked)))

        # Traffic
        summary = self.db.get_traffic_summary(hours=24)
        total = sum(s["total_bytes"] for s in summary) if summary else 0
        self.card_traffic["label"].configure(text=format_bytes(total))

        # Connection status
        connected = check_internet_connection()
        self.lbl_connection.configure(
            text=f" {self._('network_status')}: "
                 f"{'✅ ' + self._('connection_ok') if connected else '❌ ' + self._('connection_error')}"
        )

        # Blocking status
        blocking_active = self.config.is_time_to_block()
        self.lbl_blocking.configure(
            text=f"🕐 {self._('time_blocking')}: "
                 f"{'🔴 ' + self._('blocking_active') if blocking_active else '🟢 ' + self._('blocking_inactive')}"
        )

        # Time
        import datetime
        self.lbl_time.configure(
            text=f" {self._('current_time')}: {datetime.datetime.now().strftime('%H:%M:%S')}"
        )

    def _quick_scan(self):
        """Quick network scan from dashboard."""
        self._show_hosts()
        self._scan_network()

    def _quick_speed_test(self):
        """Quick speed test from dashboard."""
        self._show_speed_test()
        self._run_speed_test_gui()

    def _scan_network(self):
        """Scan network and update hosts list."""
        def scan_thread():
            hosts = self.scanner.quick_scan()
            for host in hosts:
                self.db.add_or_update_host(
                    ip=host["ip"], mac=host["mac"],
                    hostname=host["hostname"],
                    os_type=host["os_type"],
                    hardware_info=host["hardware"],
                )
            self.after(0, self._refresh_hosts)

        threading.Thread(target=scan_thread, daemon=True).start()

    def _refresh_hosts(self):
        """Refresh hosts list display."""
        # Clear existing
        for widget in self.hosts_scroll.winfo_children():
            widget.destroy()

        hosts = self.db.get_all_hosts()
        if not hosts:
            ctk.CTkLabel(
                self.hosts_scroll, text=self._("no_hosts"),
                text_color="gray"
            ).pack(pady=50)
            return

        for host in hosts:
            row = ctk.CTkFrame(self.hosts_scroll)
            row.pack(fill="x", pady=2)

            status = "🚫 " + self._("blocked") if host["is_blocked"] else "✅ " + self._("online")

            ctk.CTkLabel(row, text=host["ip_address"], width=140).grid(row=0, column=0, padx=5)
            ctk.CTkLabel(row, text=host["mac_address"] or "N/A", width=140).grid(row=0, column=1, padx=5)
            ctk.CTkLabel(row, text=host["hostname"] or "N/A", width=160).grid(row=0, column=2, padx=5)
            ctk.CTkLabel(row, text=host["os_type"] or "Unknown", width=120).grid(row=0, column=3, padx=5)
            ctk.CTkLabel(row, text=host["hardware_info"] or "N/A", width=140).grid(row=0, column=4, padx=5)
            ctk.CTkLabel(row, text=status, width=80).grid(row=0, column=5, padx=5)

            # Action buttons
            btn_frame = ctk.CTkFrame(row)
            btn_frame.grid(row=0, column=6, padx=5)

            if host["is_blocked"]:
                ctk.CTkButton(
                    btn_frame, text=self._("unblock"), width=60, height=25,
                    command=lambda ip=host["ip_address"]: self._unblock_host(ip)
                ).pack(side="left", padx=2)
            else:
                ctk.CTkButton(
                    btn_frame, text=self._("block"), width=60, height=25,
                    command=lambda ip=host["ip_address"]: self._block_host(ip)
                ).pack(side="left", padx=2)

            ctk.CTkButton(
                btn_frame, text=self._("remove"), width=60, height=25,
                fg_color="red", hover_color="darkred",
                command=lambda ip=host["ip_address"]: self._delete_host(ip)
            ).pack(side="left", padx=2)

    def _block_host(self, ip: str):
        """Block a host."""
        self.db.block_host(ip, True)
        self.firewall.block_host(ip)
        self._refresh_hosts()
        self._refresh_dashboard()

    def _unblock_host(self, ip: str):
        """Unblock a host."""
        self.db.block_host(ip, False)
        self.firewall.unblock_host(ip)
        self._refresh_hosts()
        self._refresh_dashboard()

    def _delete_host(self, ip: str):
        """Delete a host."""
        self.db.delete_host(ip)
        self._refresh_hosts()

    def _refresh_traffic(self):
        """Refresh traffic display."""
        for widget in self.traffic_scroll.winfo_children():
            widget.destroy()

        summary = self.db.get_traffic_summary(hours=24)
        if not summary:
            ctk.CTkLabel(
                self.traffic_scroll, text="No traffic data yet.",
                text_color="gray"
            ).pack(pady=50)
            return

        for s in summary[:20]:
            row = ctk.CTkFrame(self.traffic_scroll)
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(row, text=s["ip_address"], width=160).grid(row=0, column=0, padx=5)
            ctk.CTkLabel(row, text=s["hostname"] or "N/A", width=160).grid(row=0, column=1, padx=5)
            ctk.CTkLabel(row, text=format_bytes(s["total_sent"]), width=160).grid(row=0, column=2, padx=5)
            ctk.CTkLabel(row, text=format_bytes(s["total_recv"]), width=160).grid(row=0, column=3, padx=5)
            ctk.CTkLabel(
                row, text=format_bytes(s["total_bytes"]),
                width=160, font=ctk.CTkFont(weight="bold")
            ).grid(row=0, column=4, padx=5)

    def _toggle_monitoring(self):
        """Toggle traffic monitoring."""
        if self.monitor.running:
            self.monitor.stop()
            self.btn_monitor.configure(text=f"▶ {self._('start_monitoring')}")
        else:
            self.monitor.start(callback=self._traffic_callback, interval=5)
            self.btn_monitor.configure(text=f"⏹ {self._('stop_monitoring')}")

    def _traffic_callback(self, data):
        """Handle traffic monitoring callback."""
        for ip, stats in data.items():
            self.db.log_traffic(
                ip,
                bytes_sent=stats.get("bytes_sent", 0),
                bytes_recv=stats.get("bytes_recv", 0),
                packets_sent=stats.get("packets_sent", 0),
                packets_recv=stats.get("packets_recv", 0),
            )
        self.after(0, self._refresh_traffic)

    def _toggle_category(self, category: str):
        """Toggle a content category."""
        enabled = self.switches[category].get()
        self.config.set(f"categories.{category}.enabled", enabled)
        self.firewall.apply_all_rules()

    def _add_rule(self):
        """Add a custom blocking rule."""
        rule_type = self.rule_type_var.get()
        target = self.rule_target_entry.get().strip()

        if not target:
            return

        # Map display names to internal names
        type_map = {
            self._("rule_host"): "host",
            self._("rule_domain"): "domain",
            self._("rule_port"): "port",
        }
        internal_type = type_map.get(rule_type, rule_type)

        self.db.add_block_rule(internal_type, target, enabled=True)
        self.firewall.apply_all_rules()
        self.rule_target_entry.delete(0, "end")
        self._refresh_rules()

    def _refresh_rules(self):
        """Refresh rules list."""
        for widget in self.rules_scroll.winfo_children():
            widget.destroy()

        rules = self.db.get_block_rules()
        if not rules:
            ctk.CTkLabel(
                self.rules_scroll, text="No custom rules.",
                text_color="gray"
            ).pack(pady=20)
            return

        for rule in rules:
            row = ctk.CTkFrame(self.rules_scroll)
            row.pack(fill="x", pady=2)

            status = "✅" if rule["enabled"] else "❌"
            ctk.CTkLabel(row, text=f"{status} {rule['rule_type']}: {rule['target']}",
                          width=300).pack(side="left", padx=5)

            ctk.CTkButton(
                row, text="️", width=30, height=25,
                command=lambda rid=rule["id"]: self._delete_rule(rid)
            ).pack(side="right", padx=5)

    def _delete_rule(self, rule_id: int):
        """Delete a blocking rule."""
        self.db.delete_rule(rule_id)
        self.firewall.apply_all_rules()
        self._refresh_rules()

    def _toggle_time_blocking(self):
        """Toggle time-based blocking."""
        enabled = self.time_block_switch.get()
        self.config.set("time_blocking.enabled", enabled)

    def _save_time_rules(self):
        """Save time blocking rules."""
        start = self.block_start_entry.get()
        end = self.block_end_entry.get()

        self.config.set("time_blocking.block_start", start)
        self.config.set("time_blocking.block_end", end)

        # Save selected days
        selected_days = [day for day, cb in self.day_checkboxes.items() if cb.get()]
        self.config.set("time_blocking.block_days", selected_days)

    def _add_whitelist(self):
        """Add IP to time-blocking whitelist."""
        ip = self.wl_entry.get().strip()
        if ip:
            whitelist = self.config.get("time_blocking.whitelisted_hosts", [])
            if ip not in whitelist:
                whitelist.append(ip)
                self.config.set("time_blocking.whitelisted_hosts", whitelist)
            self.wl_entry.delete(0, "end")

    def _run_speed_test_gui(self):
        """Run speed test from GUI."""
        self.btn_speed_test.configure(text=self._("testing"), state="disabled")

        def test_thread():
            def progress(step, pct):
                self.after(0, lambda: self.btn_speed_test.configure(
                    text=f"{self._('testing')} {pct}%"
                ))

            result = self.speed_tester.run_test(callback=progress)

            def update_ui():
                if result["success"]:
                    self.speed_results["download"].configure(
                        text=f"⬇ {self._('download_speed')}: {result['download_mbps']:.2f} {self._('mbps')}"
                    )
                    self.speed_results["upload"].configure(
                        text=f"⬆ {self._('upload_speed')}: {result['upload_mbps']:.2f} {self._('mbps')}"
                    )
                    self.speed_results["ping"].configure(
                        text=f"📶 {self._('ping')}: {result['ping_ms']:.2f} {self._('ms')}"
                    )
                    self.speed_results["server"].configure(
                        text=f"️ {self._('server')}: {result['server']}"
                    )
                else:
                    self.speed_results["download"].configure(
                        text=f"❌ {result.get('error', 'Test failed')}"
                    )

                self.btn_speed_test.configure(
                    text=f"🚀 {self._('run_speed_test')}", state="normal"
                )
                self._refresh_speed_history()

            self.after(0, update_ui)

        threading.Thread(target=test_thread, daemon=True).start()

    def _refresh_speed_history(self):
        """Refresh speed test history."""
        for widget in self.speed_history_scroll.winfo_children():
            widget.destroy()

        history = self.speed_tester.get_history()
        if not history:
            ctk.CTkLabel(
                self.speed_history_scroll, text="No test history.",
                text_color="gray"
            ).pack(pady=20)
            return

        for test in history[:10]:
            row = ctk.CTkFrame(self.speed_history_scroll)
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(
                row,
                text=f" {test['download_mbps']:.2f} Mbps  "
                     f"⬆ {test['upload_mbps']:.2f} Mbps  "
                     f"📶 {test['ping_ms']:.0f} ms  "
                     f"📅 {test['timestamp']}"
            ).pack(anchor="w", padx=10, pady=5)

    def _refresh_alerts(self):
        """Refresh alerts list."""
        for widget in self.alerts_scroll.winfo_children():
            widget.destroy()

        alerts = self.db.get_alerts(limit=50)
        if not alerts:
            ctk.CTkLabel(
                self.alerts_scroll, text=self._("no_alerts"),
                text_color="gray"
            ).pack(pady=50)
            return

        severity_colors = {
            "info": "blue",
            "warning": "orange",
            "critical": "red",
        }

        for alert in alerts:
            color = severity_colors.get(alert["severity"], "gray")
            severity_labels = {
                "info": self._("severity_info"),
                "warning": self._("severity_warning"),
                "critical": self._("severity_critical"),
            }

            row = ctk.CTkFrame(self.alerts_scroll, fg_color=(f"{color}20", f"{color}15"))
            row.pack(fill="x", pady=2)

            icon = {"info": "️", "warning": "⚠️", "critical": "🚨"}.get(alert["severity"], "📢")
            read_status = "📖" if alert["is_read"] else "📕"

            ctk.CTkLabel(
                row,
                text=f"{read_status} {icon} [{severity_labels.get(alert['severity'], alert['severity'])}] "
                     f"{alert['message']}",
                justify="left"
            ).pack(anchor="w", padx=10, pady=5)

    def _mark_alerts_read(self):
        """Mark all alerts as read."""
        self.db.mark_alerts_read()
        self._refresh_alerts()

    def _toggle_language(self):
        """Toggle between English and Arabic."""
        new_lang = "ar" if self.translations.language == "en" else "en"
        self.translations.set_language(new_lang)
        self.config.set("general.language", new_lang)
        self._ = self.translations.get

        # Update RTL
        if self.translations.is_rtl():
            self.configure(direction="rtl")
        else:
            self.configure(direction="ltr")

        # Reload UI text
        self._refresh_dashboard()

    def _change_language(self, selection):
        """Change language from settings."""
        lang = "ar" if selection == self._("arabic") else "en"
        self._toggle_language()

    def _save_interface(self):
        """Save network interface setting."""
        iface = self.iface_entry.get().strip()
        if iface:
            self.config.set("general.interface", iface)

    def _change_username(self):
        """Change admin username."""
        new_user = self.new_user_entry.get().strip()
        if not new_user:
            return

        current_user = self.config.get("general.admin_username", "admin")
        if self.auth.update_profile(current_user, new_username=new_user):
            self.config.set("general.admin_username", new_user)
            self.current_user_lbl.configure(text=new_user)
            self.new_user_entry.delete(0, "end")

    def _change_password(self):
        """Change admin password."""
        current = self.curr_pass_entry.get()
        new_pass = self.new_pass_entry.get()

        if not current or not new_pass:
            return

        current_user = self.config.get("general.admin_username", "admin")
        if self.auth.change_password(current_user, current, new_pass):
            self.curr_pass_entry.delete(0, "end")
            self.new_pass_entry.delete(0, "end")
        else:
            pass  # Show error

    def _set_email(self):
        """Set recovery email."""
        email = self.email_entry.get().strip()
        self.config.set("general.recovery_email", email)

    def _refresh_system_info(self):
        """Refresh system information display."""
        info = get_system_info()
        import psutil
        text = (
            f"🖥️ Platform: {info['platform']} {info['platform_release']}\n"
            f"🏗️ Architecture: {info['architecture']}\n"
            f"⚡ Processor: {info['processor']}\n"
            f"🔢 CPU Cores: {info['cpu_count']}\n"
            f" CPU Usage: {psutil.cpu_percent(interval=0.5)}%\n"
            f"💾 RAM: {format_bytes(info['ram_available'])} / {format_bytes(info['ram_total'])}\n"
            f"💿 Disk: {info['disk_usage']}% used\n"
            f"🏠 Hostname: {info['hostname']}"
        )
        self.sys_info_label.configure(text=text)

    def on_closing(self):
        """Handle window close."""
        self.monitor.stop()
        self.db.close()
        self.destroy()


def main():
    """Entry point for HomeNet GUI."""
    app = HomeNetGUI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()