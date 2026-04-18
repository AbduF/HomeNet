import customtkinter as ctk
from . import i18n
from .auth_manager import AuthManager
from .network_monitor import NetworkMonitor
from .speed_test import SpeedTest

class HomeNetGUI(ctk.CTk):
    def __init__(self, lang="en"):
        super().__init__()
        i18n.init(lang)
        self.geometry("900x650")
        self.title(i18n.I18N["app_title"])
        self.auth = AuthManager()
        self.monitor = NetworkMonitor()
        self.speed = SpeedTest()

        # RTL for Arabic
        if lang == "ar":
            self.tk.call("tk", "scaling", 1.0)
            self.option_add("*Font", "Arial 14")
        
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        for tab_name in [i18n.I18N["dashboard"], i18n.I18N["hosts"], 
                         i18n.I18N["block_rules"], i18n.I18N["system"]]:
            self.tabview.add(tab_name)

        # Dashboard
        dash = self.tabview.tab(i18n.I18N["dashboard"])
        ctk.CTkLabel(dash, text=i18n.I18N["kids_block_active"], font=("Arial", 18, "bold")).pack(pady=20)
        ctk.CTkButton(dash, text=i18n.I18N["speed_test"], command=self._run_speed).pack(pady=10)
        self.speed_lbl = ctk.CTkLabel(dash, text="")
        self.speed_lbl.pack()

        # Hosts
        hosts = self.tabview.tab(i18n.I18N["hosts"])
        ctk.CTkButton(hosts, text="Scan Network", command=self._scan_hosts).pack(pady=10)
        self.hosts_lbl = ctk.CTkTextbox(hosts, height=300)
        self.hosts_lbl.pack(pady=5, padx=10)

        # System
        sys_tab = self.tabview.tab(i18n.I18N["system"])
        ctk.CTkEntry(sys_tab, placeholder_text="New Password").pack(pady=5)
        ctk.CTkEntry(sys_tab, placeholder_text="Reset Email").pack(pady=5)
        ctk.CTkButton(sys_tab, text="Save", command=self._save_sys).pack(pady=10)
        ctk.CTkButton(sys_tab, text=i18n.I18N["lang_switch"], command=self._toggle_lang).pack(pady=10)

    def _run_speed(self):
        self.speed_lbl.configure(text="Testing...")
        self.update()
        res = self.speed.run_test() if self.speed.check_connection() else "No Internet"
        self.speed_lbl.configure(text=res)

    def _scan_hosts(self):
        ips = self.monitor.scan_hosts()
        self.hosts_lbl.delete("0.0", "end")
        for ip in ips:
            info = self.monitor.get_host_os_hw(ip)
            traf = self.monitor.get_traffic_stats()
            self.hosts_lbl.insert("end", f"{ip} | {info['os']} | {traf['recv_mb']:.1f} MB Rx\n")

    def _save_sys(self):
        pass  # Bind to auth_manager & config

    def _toggle_lang(self):
        pass  # Reload GUI with "ar" or "en"