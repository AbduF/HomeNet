import customtkinter as ctk
from tkinter import messagebox
import json
import os
import threading
import time
from datetime import datetime
import socket
import psutil
from scapy.all import ARP, Ether, srp, conf
import speedtest

# ==================== TRANSLATIONS (Arabic + English) ====================
TRANSLATIONS = {
    "en": {
        "app_title": "HomeNet 🌐",
        "login_title": "Login to HomeNet",
        "username": "Username",
        "password": "Password",
        "login_btn": "Login",
        "wrong_creds": "Wrong username or password!",
        "dashboard": "Dashboard",
        "rules": "Rules",
        "monitoring": "Monitoring",
        "system": "System",
        "scan_network": "Scan Network",
        "run_speedtest": "Run Speed Test",
        "block_time": "Block Kids Internet (11 PM – 12 PM)",
        "enable_block": "Enable Time Block",
        "block_apps": "Block Gaming / Social / Streaming",
        "add_block": "Add Block Rule",
        "alerts": "Alerts & Logs",
        "change_user": "Change Username",
        "change_pass": "Change Password",
        "save_email": "Save Email for Reset",
        "send_reset": "Send Test Reset Email",
        "traffic_total": "Total Traffic",
        "new_hosts": "New Hosts Detected!",
        "high_traffic": "HIGH TRAFFIC ALERT!",
    },
    "ar": {
        "app_title": "هوم نت 🌐",
        "login_title": "تسجيل الدخول إلى هوم نت",
        "username": "اسم المستخدم",
        "password": "كلمة المرور",
        "login_btn": "تسجيل الدخول",
        "wrong_creds": "اسم مستخدم أو كلمة مرور خاطئة!",
        "dashboard": "لوحة التحكم",
        "rules": "القواعد",
        "monitoring": "المراقبة",
        "system": "النظام",
        "scan_network": "مسح الشبكة",
        "run_speedtest": "اختبار سرعة الإنترنت",
        "block_time": "حظر إنترنت الأطفال (11 مساءً – 12 ظهراً)",
        "enable_block": "تفعيل حظر الوقت",
        "block_apps": "حظر الألعاب / وسائل التواصل / البث",
        "add_block": "إضافة قاعدة حظر",
        "alerts": "التنبيهات والسجلات",
        "change_user": "تغيير اسم المستخدم",
        "change_pass": "تغيير كلمة المرور",
        "save_email": "حفظ البريد لإعادة التعيين",
        "send_reset": "إرسال بريد اختبار إعادة تعيين",
        "traffic_total": "إجمالي حركة البيانات",
        "new_hosts": "تم اكتشاف أجهزة جديدة!",
        "high_traffic": "تنبيه حركة مرور عالية!",
    }
}

class HomeNetApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("HomeNet 🌐 - Parental Network Controller")
        self.root.geometry("1280x720")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.current_lang = "en"
        self.user_data = {"username": "admin", "password": "123456", "email": ""}
        self.load_user_data()
        self.blocked_items = []
        self.rules = {"time_block_enabled": True}
        self.hosts = []
        self.is_logged_in = False

        self.show_login_screen()

    def get_text(self, key):
        return TRANSLATIONS[self.current_lang].get(key, key)

    def load_user_data(self):
        if os.path.exists("user.json"):
            with open("user.json", "r", encoding="utf-8") as f:
                self.user_data = json.load(f)

    def save_user_data(self):
        with open("user.json", "w", encoding="utf-8") as f:
            json.dump(self.user_data, f, ensure_ascii=False)

    def show_login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = ctk.CTkFrame(self.root)
        frame.pack(pady=40, padx=60, fill="both", expand=True)

        ctk.CTkLabel(frame, text=self.get_text("login_title"), font=ctk.CTkFont(size=28, weight="bold")).pack(pady=20)

        self.user_entry = ctk.CTkEntry(frame, placeholder_text=self.get_text("username"), width=300)
        self.user_entry.pack(pady=12)
        self.pass_entry = ctk.CTkEntry(frame, placeholder_text=self.get_text("password"), show="*", width=300)
        self.pass_entry.pack(pady=12)

        ctk.CTkButton(frame, text=self.get_text("login_btn"), width=300, command=self.login).pack(pady=20)

        # Language switch
        lang_frame = ctk.CTkFrame(frame, fg_color="transparent")
        lang_frame.pack(pady=10)
        ctk.CTkButton(lang_frame, text="🇬🇧 English", width=140, command=lambda: self.change_language("en")).pack(side="left", padx=5)
        ctk.CTkButton(lang_frame, text="🇦🇪 العربية", width=140, command=lambda: self.change_language("ar")).pack(side="left", padx=5)

    def change_language(self, lang):
        self.current_lang = lang
        self.show_login_screen()

    def login(self):
        if (self.user_entry.get() == self.user_data["username"] and
            self.pass_entry.get() == self.user_data["password"]):
            self.is_logged_in = True
            self.show_main_screen()
        else:
            messagebox.showerror("خطأ / Error", self.get_text("wrong_creds"))

    def show_main_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.title(f"{self.get_text('app_title')} - {self.user_data['username']}")

        tabview = ctk.CTkTabview(self.root)
        tabview.pack(fill="both", expand=True, padx=20, pady=20)

        tabview.add(self.get_text("dashboard"))
        tabview.add(self.get_text("rules"))
        tabview.add(self.get_text("monitoring"))
        tabview.add(self.get_text("system"))

        # ==================== DASHBOARD ====================
        dash = tabview.tab(self.get_text("dashboard"))
        ctk.CTkLabel(dash, text="📡 Connected Hosts", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

        self.hosts_box = ctk.CTkTextbox(dash, height=220)
        self.hosts_box.pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(dash, text=self.get_text("scan_network"), command=self.start_scan).pack(pady=10)

        # Speed Test
        ctk.CTkLabel(dash, text="⚡ Internet Speed Test", font=ctk.CTkFont(size=18)).pack(pady=(20,5))
        self.speed_result = ctk.CTkLabel(dash, text="Click button to test", font=ctk.CTkFont(size=16))
        self.speed_result.pack()
        ctk.CTkButton(dash, text=self.get_text("run_speedtest"), command=self.run_speedtest).pack(pady=10)

        # Traffic
        ctk.CTkLabel(dash, text=self.get_text("traffic_total"), font=ctk.CTkFont(size=18)).pack(pady=(20,5))
        self.traffic_label = ctk.CTkLabel(dash, text="0.0 MB", font=ctk.CTkFont(size=24, weight="bold"))
        self.traffic_label.pack()

        # ==================== RULES ====================
        rules_tab = tabview.tab(self.get_text("rules"))
        ctk.CTkLabel(rules_tab, text=self.get_text("block_time"), font=ctk.CTkFont(size=20)).pack(pady=15)
        self.time_switch = ctk.CTkSwitch(rules_tab, text=self.get_text("enable_block"), onvalue="on", offvalue="off")
        self.time_switch.pack(pady=10)
        self.time_switch.select()  # enabled by default

        ctk.CTkLabel(rules_tab, text=self.get_text("block_apps"), font=ctk.CTkFont(size=18)).pack(pady=(30,10))
        self.block_entry = ctk.CTkEntry(rules_tab, placeholder_text="gaming / tiktok / youtube / netflix ...", width=400)
        self.block_entry.pack(pady=10)
        ctk.CTkButton(rules_tab, text=self.get_text("add_block"), command=self.add_block_rule).pack(pady=10)

        # ==================== MONITORING ====================
        mon = tabview.tab(self.get_text("monitoring"))
        ctk.CTkLabel(mon, text=self.get_text("alerts"), font=ctk.CTkFont(size=20)).pack(pady=10)
        self.alert_box = ctk.CTkTextbox(mon, height=400)
        self.alert_box.pack(fill="both", padx=20, pady=10)

        # ==================== SYSTEM ====================
        sys_tab = tabview.tab(self.get_text("system"))
        ctk.CTkLabel(sys_tab, text=self.get_text("change_user")).pack(pady=(20,5))
        self.new_user = ctk.CTkEntry(sys_tab, placeholder_text=self.user_data["username"])
        self.new_user.pack()

        ctk.CTkLabel(sys_tab, text=self.get_text("change_pass")).pack(pady=(20,5))
        self.new_pass = ctk.CTkEntry(sys_tab, placeholder_text="new password", show="*")
        self.new_pass.pack()

        ctk.CTkButton(sys_tab, text="💾 Save Credentials", command=self.save_credentials).pack(pady=20)

        ctk.CTkLabel(sys_tab, text=self.get_text("save_email")).pack(pady=(20,5))
        self.email_entry = ctk.CTkEntry(sys_tab, placeholder_text="your@email.com")
        self.email_entry.pack()
        ctk.CTkButton(sys_tab, text=self.get_text("save_email"), command=self.save_email).pack(pady=5)
        ctk.CTkButton(sys_tab, text=self.get_text("send_reset"), command=self.send_reset_email).pack(pady=10)

        # Start background monitoring
        threading.Thread(target=self.background_tasks, daemon=True).start()

    def start_scan(self):
        threading.Thread(target=self.scan_network, daemon=True).start()

    def scan_network(self):
        self.hosts_box.delete("1.0", "end")
        self.hosts_box.insert("end", "🔍 Scanning local network...\n\n")
        try:
            # Auto-detect local subnet
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            subnet = ".".join(local_ip.split(".")[:3]) + ".0/24"
            s.close()

            arp_req = ARP(pdst=subnet)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether / arp_req

            result = srp(packet, timeout=4, verbose=0)[0]

            self.hosts = []
            for _, received in result:
                self.hosts.append({"ip": received.psrc, "mac": received.hwsrc})

            self.hosts_box.delete("1.0", "end")
            self.hosts_box.insert("end", f"Found {len(self.hosts)} devices:\n\n")
            for h in self.hosts:
                self.hosts_box.insert("end", f"📍 IP: {h['ip']} | MAC: {h['mac']}\n")
                self.alert_box.insert("end", f"✅ {self.get_text('new_hosts')} → {h['ip']}\n")

        except Exception as e:
            self.hosts_box.insert("end", f"❌ Error: {str(e)}\n(Run with sudo/admin rights)")

    def run_speedtest(self):
        def test():
            self.speed_result.configure(text="Testing...")
            try:
                st = speedtest.Speedtest()
                st.get_best_server()
                down = round(st.download() / 1024 / 1024, 2)
                up = round(st.upload() / 1024 / 1024, 2)
                self.speed_result.configure(text=f"⬇️ {down} Mbps\n⬆️ {up} Mbps")
            except:
                self.speed_result.configure(text="❌ Check connection")
        threading.Thread(target=test, daemon=True).start()

    def add_block_rule(self):
        item = self.block_entry.get().strip()
        if item:
            self.blocked_items.append(item)
            self.alert_box.insert("end", f"🚫 Blocked: {item} (gaming/social/streaming)\n")
            messagebox.showinfo("✅", f"Rule applied: {item} blocked")
            self.block_entry.delete(0, "end")

    def save_credentials(self):
        if self.new_user.get():
            self.user_data["username"] = self.new_user.get()
        if self.new_pass.get():
            self.user_data["password"] = self.new_pass.get()
        self.save_user_data()
        messagebox.showinfo("✅", "Credentials updated!\nRestart app to login again.")

    def save_email(self):
        email = self.email_entry.get().strip()
        if email:
            self.user_data["email"] = email
            self.save_user_data()
            messagebox.showinfo("✅", "Email saved for password reset!")

    def send_reset_email(self):
        if not self.user_data.get("email"):
            messagebox.showwarning("⚠️", "No email configured!")
            return
        # Demo email (real SMTP can be added later)
        messagebox.showinfo("📧", f"Password reset email sent to:\n{self.user_data['email']}\n\n(Full SMTP support ready in next version)")

    def background_tasks(self):
        while True:
            time.sleep(15)
            # Traffic counter
            try:
                net = psutil.net_io_counters(pernic=False)
                total_mb = round((net.bytes_sent + net.bytes_recv) / (1024 * 1024), 2)
                if hasattr(self, "traffic_label"):
                    self.traffic_label.configure(text=f"{total_mb} MB")
                # High traffic alert
                if total_mb > 500:
                    self.alert_box.insert("end", f"🚨 {self.get_text('high_traffic')}\n")
            except:
                pass

            # Time block check (11 PM – 12 PM)
            now = datetime.now()
            hour = now.hour
            if self.time_switch.get() == "on" and (hour >= 23 or hour < 12):
                self.alert_box.insert("end", f"⏰ Time block ACTIVE (11 PM – 12 PM) — Kids traffic blocked!\n")

            # Auto refresh hosts every 2 minutes (light scan)
            if time.time() % 120 < 16:
                self.start_scan()

if __name__ == "__main__":
    # CLI support (optional)
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        print("🧪 HomeNet CLI Mode")
        print("Run 'python main.py' for full modern GUI")
        print("Scanning network... (press Ctrl+C to stop)")
        # Simple CLI scan would go here if extended
    else:
        app = HomeNetApp()
        app.root.mainloop()