import customtkinter as ctk
import json
import sys
import os

# Set theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

def load_i18n(lang):
    path = f"i18n/{lang}.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def load_config():
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            return json.load(f)
    return {
        "admin": {"username": "admin", "password": "123456", "email": ""},
        "settings": {"language": "en", "block_schedule": {"start": "23:00", "end": "00:00"}, "traffic_alert_threshold_mb": 500, "alerts_enabled": True},
        "rules": []
    }

class LoginWindow(ctk.CTk):
    def __init__(self, config, i18n):
        super().__init__()
        self.config = config
        self.i18n = i18n
        self.title(self.i18n.get("login", "Login"))
        self.geometry("400x300")
        self.resizable(False, False)
        
        ctk.CTkLabel(self, text=self.i18n.get("app_title", "HomeNet"), font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        ctk.CTkLabel(self, text="🇦 UAE / Al Ain", font=ctk.CTkFont(size=12)).pack(pady=0)
        
        self.user_entry = ctk.CTkEntry(self, placeholder_text=self.i18n.get("username", "Username"), width=250)
        self.user_entry.pack(pady=10)
        
        self.pass_entry = ctk.CTkEntry(self, placeholder_text=self.i18n.get("password", "Password"), show="*", width=250)
        self.pass_entry.pack(pady=10)
        
        ctk.CTkButton(self, text=self.i18n.get("login", "Login"), command=self.authenticate, width=250).pack(pady=20)
        
        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.pack()
        
    def authenticate(self):
        user = self.user_entry.get()
        pwd = self.pass_entry.get()
        
        if user == self.config["admin"]["username"] and pwd == self.config["admin"]["password"]:
            self.destroy()
            from ui.dashboard import HomeNetDashboard
            app = HomeNetDashboard(self.config, self.i18n)
            app.mainloop()
        else:
            self.error_label.configure(text="Invalid credentials")

if __name__ == "__main__":
    config = load_config()
    lang = config["settings"]["language"]
    i18n = load_i18n(lang)
    
    login = LoginWindow(config, i18n)
    login.mainloop()