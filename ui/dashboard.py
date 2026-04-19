import customtkinter as ctk
import json
import time
import threading
from datetime import datetime
import psutil
import speedtest
import nmap
import requests

class HomeNetDashboard(ctk.CTk):
    def __init__(self, config, i18n):
        super().__init__()
        self.config = config
        self.i18n = i18n
        self.lang = config["settings"]["language"]
        self.is_arabic = self.lang == "ar"
        
        self.title(self.i18n["app_title"])
        self.geometry("1100x700")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        if self.is_arabic:
            self.configure(justify="right")
            
        self.setup_sidebar()
        self.setup_main_area()
        self.load_hosts()
        self.start_monitoring()
        
    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        ctk.CTkLabel(self.sidebar, text="🌐 HomeNet", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)
        ctk.CTkLabel(self.sidebar, text="UAE / Al Ain", font=ctk.CTkFont(size=12)).pack(pady=0)
        
        self.sidebar_buttons = {}
        tabs = ["dashboard", "hosts", "rules", "settings", "speed_test"]
        for tab in tabs:
            btn = ctk.CTkButton(self.sidebar, text=self.i18n[tab], command=lambda t=tab: self.show_tab(t))
            btn.pack(fill="x", padx=10, pady=5)
            self.sidebar_buttons[tab] = btn
            
        ctk.CTkButton(self.sidebar, text=self.i18n["logout"], fg_color="red", hover_color="darkred",
                      command=self.destroy).pack(fill="x", padx=10, pady=20, side="bottom")
        
    def setup_main_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.dashboard_tab = ctk.CTkFrame(self.main_frame)
        self.hosts_tab = ctk.CTkFrame(self.main_frame)
        self.rules_tab = ctk.CTkFrame(self.main_frame)
        self.settings_tab = ctk.CTkFrame(self.main_frame)
        self.speed_tab = ctk.CTkFrame(self.main_frame)
        
        self.build_dashboard()
        self.build_hosts()
        self.build_rules()
        self.build_settings()
        self.build_speed_test()
        
        self.show_tab("dashboard")
        
    def show_tab(self, tab_name):
        for frame in [self.dashboard_tab, self.hosts_tab, self.rules_tab, self.settings_tab, self.speed_tab]:
            frame.grid_forget()
        getattr(self, f"{tab_name}_tab").grid(sticky="nsew")
        
    def build_dashboard(self):
        self.traffic_frame = ctk.CTkFrame(self.dashboard_tab)
        self.traffic_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(self.traffic_frame, text=self.i18n["traffic_utilization"], font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        self.traffic_bar = ctk.CTkProgressBar(self.traffic_frame, mode="determinate")
        self.traffic_bar.pack(fill="x", pady=5)
        self.traffic_label = ctk.CTkLabel(self.traffic_frame, text="0 MB/s")
        self.traffic_label.pack(anchor="e")
        
        self.alert_frame = ctk.CTkFrame(self.dashboard_tab)
        self.alert_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(self.alert_frame, text="⚠️ System Alerts", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        self.alert_text = ctk.CTkTextbox(self.alert_frame, height=100)
        self.alert_text.pack(fill="x", pady=5)
        
        self.status_frame = ctk.CTkFrame(self.dashboard_tab)
        self.status_frame.pack(fill="x", padx=10, pady=10)
        self.status_label = ctk.CTkLabel(self.status_frame, text=f" {self.i18n['status_connected']}")
        self.status_label.pack(anchor="w")
        
    def build_hosts(self):
        self.hosts_frame = ctk.CTkFrame(self.hosts_tab)
        self.hosts_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(self.hosts_frame, text=self.i18n["hosts"], font=ctk.CTkFont(weight="bold", size=16)).pack(anchor="w", pady=5)
        
        self.hosts_text = ctk.CTkTextbox(self.hosts_frame, height=400)
        self.hosts_text.pack(fill="both", expand=True)
        
        refresh_btn = ctk.CTkButton(self.hosts_frame, text="🔄 Refresh", command=self.load_hosts)
        refresh_btn.pack(pady=5)
        
    def build_rules(self):
        self.rules_frame = ctk.CTkFrame(self.rules_tab)
        self.rules_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(self.rules_frame, text=self.i18n["rules"], font=ctk.CTkFont(weight="bold", size=16)).pack(anchor="w", pady=5)
        
        self.rules_text = ctk.CTkTextbox(self.rules_frame, height=300)
        self.rules_text.pack(fill="both", expand=True, pady=5)
        self.rules_text.insert("0.0", json.dumps(self.config["rules"], indent=2))
        
        ctk.CTkButton(self.rules_frame, text=self.i18n["save"], command=self.save_rules).pack(pady=5)
        
        ctk.CTkLabel(self.rules_frame, text=self.i18n["block_time"]).pack(anchor="w", pady=5)
        self.start_entry = ctk.CTkEntry(self.rules_frame)
        self.start_entry.insert(0, self.config["settings"]["block_schedule"]["start"])
        self.start_entry.pack(fill="x", pady=2)
        
        self.end_entry = ctk.CTkEntry(self.rules_frame)
        self.end_entry.insert(0, self.config["settings"]["block_schedule"]["end"])
        self.end_entry.pack(fill="x", pady=2)
        
        ctk.CTkButton(self.rules_frame, text=self.i18n["save"], command=self.save_schedule).pack(pady=5)
        
    def build_settings(self):
        self.settings_frame = ctk.CTkFrame(self.settings_tab)
        self.settings_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(self.settings_frame, text=self.i18n["settings"], font=ctk.CTkFont(weight="bold", size=16)).pack(anchor="w", pady=5)
        
        ctk.CTkLabel(self.settings_frame, text=self.i18n["username"]).pack(anchor="w")
        self.user_entry = ctk.CTkEntry(self.settings_frame)
        self.user_entry.insert(0, self.config["admin"]["username"])
        self.user_entry.pack(fill="x", pady=2)
        
        ctk.CTkLabel(self.settings_frame, text=self.i18n["password"]).pack(anchor="w")
        self.pass_entry = ctk.CTkEntry(self.settings_frame, show="*")
        self.pass_entry.pack(fill="x", pady=2)
        
        ctk.CTkLabel(self.settings_frame, text="Email (for password reset)").pack(anchor="w")
        self.email_entry = ctk.CTkEntry(self.settings_frame)
        self.email_entry.insert(0, self.config["admin"]["email"])
        self.email_entry.pack(fill="x", pady=2)
        
        ctk.CTkLabel(self.settings_frame, text="Language / اللغة").pack(anchor="w")
        self.lang_var = ctk.StringVar(value=self.lang)
        ctk.CTkSegmentedButton(self.settings_frame, values=["en", "ar"], variable=self.lang_var, command=self.change_language).pack(pady=5)
        
        ctk.CTkButton(self.settings_frame, text=self.i18n["save"], command=self.save_settings).pack(pady=10)
        
    def build_speed_test(self):
        self.speed_frame = ctk.CTkFrame(self.speed_tab)
        self.speed_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(self.speed_frame, text=self.i18n["speed_test"], font=ctk.CTkFont(weight="bold", size=16)).pack(anchor="w", pady=5)
        
        self.speed_result = ctk.CTkLabel(self.speed_frame, text="Ready")
        self.speed_result.pack(pady=20)
        
        self.progress = ctk.CTkProgressBar(self.speed_frame, mode="determinate")
        self.progress.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkButton(self.speed_frame, text=self.i18n["run_test"], command=self.run_speed_test).pack(pady=10)
        
    def load_hosts(self):
        nm = nmap.PortScanner()
        hosts_info = "IP Address       | MAC Address        | OS/HW Details\n" + "="*60 + "\n"
        
        try:
            nm.scan(hosts='192.168.1.0/24', arguments='-sn')
            for host in nm.all_hosts():
                mac = nm[host]['addresses'].get('mac', 'Unknown')
                vendor = nm[host].get('vendor', {}).get(mac, 'Unknown')
                hosts_info += f"{host:<17} | {mac:<19} | {vendor}\n"
        except Exception as e:
            hosts_info += f"Scan error: {e}\n"
            
        self.hosts_text.delete("0.0", "end")
        self.hosts_text.insert("0.0", hosts_info)
        
    def run_speed_test(self):
        def test():
            self.progress.set(0)
            self.speed_result.configure(text="Testing...")
            try:
                st = speedtest.Speedtest()
                self.progress.set(0.3)
                st.get_best_server()
                self.progress.set(0.5)
                st.download()
                self.progress.set(0.7)
                st.upload()
                self.progress.set(1.0)
                
                results = st.results.dict()
                down = results['download'] / 1_000_000
                up = results['upload'] / 1_000_000
                ping = results['ping']
                
                self.speed_result.configure(
                    text=f"⬇️ Download: {down:.2f} Mbps\n️ Upload: {up:.2f} Mbps\n📡 Ping: {ping:.0f} ms"
                )
            except Exception as e:
                self.speed_result.configure(text=f"Error: {e}")
                
        threading.Thread(target=test, daemon=True).start()
        
    def start_monitoring(self):
        def monitor():
            while True:
                try:
                    net = psutil.net_io_counters()
                    upload = net.bytes_sent / 1_000_000
                    download = net.bytes_recv / 1_000_000
                    total = upload + download
                    
                    self.traffic_bar.set(min(total / 1000, 1.0))
                    self.traffic_label.configure(text=f"↑ {upload:.1f} MB | ↓ {download:.1f} MB")
                    
                    if self.config["settings"]["alerts_enabled"] and total > self.config["settings"]["traffic_alert_threshold_mb"]:
                        self.alert_text.insert("end", f"️ {self.i18n['high_traffic_alert']}: {total:.1f} MB\n")
                        
                except Exception:
                    pass
                time.sleep(5)
                
        threading.Thread(target=monitor, daemon=True).start()
        
    def save_rules(self):
        try:
            self.config["rules"] = json.loads(self.rules_text.get("0.0", "end"))
            with open("config.json", "w") as f:
                json.dump(self.config, f, indent=2)
            self.alert_text.insert("end", "✅ Rules saved\n")
        except Exception as e:
            self.alert_text.insert("end", f" Error: {e}\n")
            
    def save_schedule(self):
        self.config["settings"]["block_schedule"]["start"] = self.start_entry.get()
        self.config["settings"]["block_schedule"]["end"] = self.end_entry.get()
        with open("config.json", "w") as f:
            json.dump(self.config, f, indent=2)
        self.alert_text.insert("end", "✅ Schedule updated\n")
        
    def save_settings(self):
        self.config["admin"]["username"] = self.user_entry.get()
        if self.pass_entry.get():
            self.config["admin"]["password"] = self.pass_entry.get()
        self.config["admin"]["email"] = self.email_entry.get()
        with open("config.json", "w") as f:
            json.dump(self.config, f, indent=2)
        self.alert_text.insert("end", "✅ Settings saved\n")
        
    def change_language(self, lang):
        self.lang = lang
        self.is_arabic = lang == "ar"
        with open("config.json", "r") as f:
            self.config = json.load(f)
        self.config["settings"]["language"] = lang
        with open("config.json", "w") as f:
            json.dump(self.config, f, indent=2)
        self.destroy()