"""
HomeNet - Hosts View
Host management and device information
"""

import customtkinter as ctk
from tkinter import ttk
import logging


class HostsView(ctk.CTkFrame):
    """Hosts management view."""

    def __init__(self, parent, db, config, scanner, monitor, blocker, lang='en'):
        super().__init__(parent, fg_color="#1A1A2E")
        self.parent = parent
        self.db = db
        self.config = config
        self.scanner = scanner
        self.monitor = monitor
        self.blocker = blocker
        self.lang = lang
        self.logger = logging.getLogger("HomeNet.Hosts")

        self.translations = self.get_translations()
        self.hosts_data = []
        self.setup_ui()
        self.load_hosts()

    def get_translations(self):
        """Get translations."""
        translations = {
            'en': {
                'title': 'Network Hosts',
                'ip': 'IP Address',
                'mac': 'MAC Address',
                'hostname': 'Hostname',
                'type': 'Device Type',
                'os': 'OS',
                'vendor': 'Vendor',
                'status': 'Status',
                'actions': 'Actions',
                'blocked': 'Blocked',
                'trusted': 'Trusted',
                'active': 'Active',
                'scan': 'Scan Network',
                'refresh': 'Refresh',
                'block': 'Block',
                'unblock': 'Unblock',
                'details': 'Details',
                'no_hosts': 'No hosts found',
                'new_host': 'New Device',
                'os_unknown': 'Unknown',
                'total': 'Total Devices',
                'filter_all': 'All',
                'filter_blocked': 'Blocked',
                'filter_trusted': 'Trusted'
            },
            'ar': {
                'title': 'أجهزة الشبكة',
                'ip': 'عنوان IP',
                'mac': 'عنوان MAC',
                'hostname': 'اسم الجهاز',
                'type': 'نوع الجهاز',
                'os': 'نظام التشغيل',
                'vendor': 'الشركة المصنعة',
                'status': 'الحالة',
                'actions': 'الإجراءات',
                'blocked': 'محظور',
                'trusted': 'موثوق',
                'active': 'نشط',
                'scan': 'فحص الشبكة',
                'refresh': 'تحديث',
                'block': 'حظر',
                'unblock': 'إلغاء الحظر',
                'details': 'التفاصيل',
                'no_hosts': 'لم يتم العثور على أجهزة',
                'new_host': 'جهاز جديد',
                'os_unknown': 'غير معروف',
                'total': 'إجمالي الأجهزة',
                'filter_all': 'الكل',
                'filter_blocked': 'المحظورة',
                'filter_trusted': 'الموثوقة'
            }
        }
        return translations.get(self.lang, translations['en'])

    def setup_ui(self):
        """Setup hosts view UI."""
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 10))

        # Title
        title = ctk.CTkLabel(
            header,
            text=self.translations['title'],
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFFFFF"
        )
        title.pack(side="left")

        # Stats
        self.stats_label = ctk.CTkLabel(
            header,
            text=f"{self.translations['total']}: 0",
            font=ctk.CTkFont(size=14),
            text_color="#B0B0B0"
        )
        self.stats_label.pack(side="right")

        # Toolbar
        toolbar = ctk.CTkFrame(self, fg_color="#16213E", corner_radius=8)
        toolbar.pack(fill="x", padx=20, pady=(0, 10))

        # Filter
        filter_label = ctk.CTkLabel(toolbar, text="Filter:", text_color="#B0B0B0")
        filter_label.pack(side="left", padx=(16, 8), pady=12)

        self.filter_var = ctk.StringVar(value="all")
        filter_menu = ctk.CTkOptionMenu(
            toolbar,
            values=[self.translations['filter_all'], self.translations['filter_blocked'], self.translations['filter_trusted']],
            variable=self.filter_var,
            width=120,
            command=self.apply_filter
        )
        filter_menu.pack(side="left", padx=8, pady=12)

        # Buttons
        scan_btn = ctk.CTkButton(
            toolbar,
            text=f"🔍 {self.translations['scan']}",
            width=140,
            height=36,
            corner_radius=8,
            fg_color="#1E88E5",
            command=self.scan_network
        )
        scan_btn.pack(side="right", padx=16, pady=8)

        refresh_btn = ctk.CTkButton(
            toolbar,
            text=f"↻ {self.translations['refresh']}",
            width=100,
            height=36,
            corner_radius=8,
            fg_color="#0F3460",
            command=self.load_hosts
        )
        refresh_btn.pack(side="right", padx=8, pady=8)

        # Table frame
        table_frame = ctk.CTkFrame(self, fg_color="#16213E", corner_radius=12)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Treeview style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                       background="#16213E",
                       foreground="#FFFFFF",
                       fieldbackground="#16213E",
                       rowheight=40)
        style.configure("Treeview.Heading",
                       background="#0F3460",
                       foreground="#FFFFFF",
                       font=("Segoe UI", 12, "bold"))
        style.map("Treeview", background=[("selected", "#1E88E5")])

        # Columns
        columns = ('hostname', 'ip', 'mac', 'type', 'os', 'vendor', 'status', 'actions')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', style="Treeview")

        # Column headings
        self.tree.heading('hostname', text=self.translations['hostname'])
        self.tree.heading('ip', text=self.translations['ip'])
        self.tree.heading('mac', text=self.translations['mac'])
        self.tree.heading('type', text=self.translations['type'])
        self.tree.heading('os', text=self.translations['os'])
        self.tree.heading('vendor', text=self.translations['vendor'])
        self.tree.heading('status', text=self.translations['status'])
        self.tree.heading('actions', text=self.translations['actions'])

        # Column widths
        self.tree.column('hostname', width=150)
        self.tree.column('ip', width=120)
        self.tree.column('mac', width=140)
        self.tree.column('type', width=100)
        self.tree.column('os', width=100)
        self.tree.column('vendor', width=120)
        self.tree.column('status', width=80)
        self.tree.column('actions', width=150)

        # Scrollbar
        scrollbar = ctk.CTkScrollbar(table_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(12, 0), pady=12)
        scrollbar.pack(side="right", fill="y", padx=(0, 12), pady=12)

        # Bind selection
        self.tree.bind('<ButtonRelease-1>', self.on_select)

    def load_hosts(self):
        """Load hosts from database."""
        try:
            self.hosts_data = self.db.get_hosts()
            self.refresh_table()
        except Exception as e:
            self.logger.error(f"Error loading hosts: {e}")

    def refresh_hosts(self):
        """Refresh hosts (called from main window)."""
        self.load_hosts()

    def refresh_table(self):
        """Refresh table with current filter."""
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Apply filter
        filter_val = self.filter_var.get()
        filtered_hosts = self.hosts_data

        if filter_val == 'blocked':
            filtered_hosts = [h for h in filtered_hosts if h.get('blocked')]
        elif filter_val == 'trusted':
            filtered_hosts = [h for h in filtered_hosts if h.get('trusted')]

        # Update stats
        self.stats_label.configure(text=f"{self.translations['total']}: {len(filtered_hosts)}")

        # Add hosts
        for host in filtered_hosts:
            status = self.translations['blocked'] if host.get('blocked') else self.translations['active']
            status_color = "#E53935" if host.get('blocked') else "#43A047"

            item = self.tree.insert('', 'end', values=(
                host.get('hostname', '-'),
                host.get('ip_address', '-'),
                host.get('mac_address', '-'),
                host.get('device_type', self.translations['os_unknown']),
                host.get('os_type', self.translations['os_unknown']),
                host.get('mac_vendor', '-'),
                status,
                self.translations['block']
            ))

            # Set row tag for status color
            if host.get('blocked'):
                self.tree.tag_configure(item, background='#2D1F1F')

    def apply_filter(self, value):
        """Apply filter to hosts."""
        self.refresh_table()

    def scan_network(self):
        """Scan network for new hosts."""
        if not self.scanner:
            return

        try:
            hosts = self.scanner.full_scan()
            new_count = 0

            for host in hosts:
                mac = host.get('mac_address')
                existing = self.db.get_host(mac_address=mac)

                if not existing:
                    # New host
                    self.db.add_host(
                        mac_address=mac,
                        ip_address=host.get('ip_address'),
                        hostname=host.get('hostname')
                    )

                    # Add alert
                    self.db.add_alert(
                        'new_host',
                        self.translations['new_host'],
                        f"New device: {host.get('hostname', mac)}",
                        'warning'
                    )
                    new_count += 1

            self.load_hosts()
            self.logger.info(f"Network scan complete: {len(hosts)} hosts, {new_count} new")

        except Exception as e:
            self.logger.error(f"Scan error: {e}")

    def on_select(self, event):
        """Handle row selection."""
        pass

    def toggle_block(self, host_id, blocked):
        """Toggle host block status."""
        self.db.block_host(host_id, not blocked)

        if not blocked:
            # Block the host
            host = self.db.get_host(host_id=host_id)
            if host and host.get('ip_address') and self.blocker:
                self.blocker.block_ip(host['ip_address'])
        else:
            # Unblock the host
            host = self.db.get_host(host_id=host_id)
            if host and host.get('ip_address') and self.blocker:
                self.blocker.unblock_ip(host['ip_address'])

        self.load_hosts()
