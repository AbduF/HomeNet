"""
HomeNet - Login Window
Authentication screen
"""

import customtkinter as ctk
from PIL import Image
import logging


class LoginWindow(ctk.CTkFrame):
    """Login window frame."""

    def __init__(self, parent, db, config):
        super().__init__(parent, fg_color="#1A1A2E")
        self.parent = parent
        self.db = db
        self.config = config
        self.logger = logging.getLogger("HomeNet.Login")

        # Language
        self.lang = config.get('language', 'en')
        self.translations = self.get_translations()

        self.setup_ui()

    def get_translations(self):
        """Get translations based on language."""
        translations = {
            'en': {
                'title': 'HomeNet',
                'subtitle': 'Parental Network Controller',
                'username': 'Username',
                'password': 'Password',
                'login': 'Login',
                'forgot': 'Forgot Password?',
                'error': 'Invalid username or password',
                'welcome': 'Welcome to HomeNet',
                'developed': 'Proudly developed in UAE, Al Ain',
                'contact': 'Contact: abdalfaqeeh@gmail.com'
            },
            'ar': {
                'title': 'هوم نت',
                'subtitle': 'متحكم شبكة ولي الأمر',
                'username': 'اسم المستخدم',
                'password': 'كلمة المرور',
                'login': 'تسجيل الدخول',
                'forgot': 'نسيت كلمة المرور؟',
                'error': 'اسم المستخدم أو كلمة المرور غير صحيحة',
                'welcome': 'مرحباً بك في هوم نت',
                'developed': 'تم تطويره بفخر في الإمارات، العين',
                'contact': 'للتواصل: abdalfaqeeh@gmail.com'
            }
        }
        return translations.get(self.lang, translations['en'])

    def setup_ui(self):
        """Setup login UI."""
        # Center frame
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.pack(expand=True, fill="both", padx=50, pady=50)

        # Logo/Title section
        title_label = ctk.CTkLabel(
            center_frame,
            text=self.translations['title'],
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color="#1E88E5"
        )
        title_label.pack(pady=(0, 5))

        subtitle_label = ctk.CTkLabel(
            center_frame,
            text=self.translations['subtitle'],
            font=ctk.CFont(size=16),
            text_color="#B0B0B0"
        )
        subtitle_label.pack(pady=(0, 40))

        # Login form
        form_frame = ctk.CTkFrame(center_frame, fg_color="#16213E", corner_radius=16)
        form_frame.pack(pady=20, padx=40)

        # Username
        username_label = ctk.CTkLabel(
            form_frame,
            text=self.translations['username'],
            font=ctk.CTkFont(size=14),
            text_color="#FFFFFF"
        )
        username_label.pack(anchor="w", padx=24, pady=(24, 4))

        self.username_entry = ctk.CTkEntry(
            form_frame,
            width=300,
            height=44,
            placeholder_text=self.translations['username'],
            font=ctk.CTkFont(size=14),
            corner_radius=8,
            border_color="#1E88E5"
        )
        self.username_entry.pack(padx=24, pady=(0, 16))

        # Password
        password_label = ctk.CTkLabel(
            form_frame,
            text=self.translations['password'],
            font=ctk.CTkFont(size=14),
            text_color="#FFFFFF"
        )
        password_label.pack(anchor="w", padx=24, pady=(8, 4))

        self.password_entry = ctk.CTkEntry(
            form_frame,
            width=300,
            height=44,
            placeholder_text=self.translations['password'],
            font=ctk.CTkFont(size=14),
            corner_radius=8,
            border_color="#1E88E5",
            show="*"
        )
        self.password_entry.pack(padx=24, pady=(0, 8))

        # Bind Enter key
        self.password_entry.bind("<Return>", lambda e: self.do_login())
        self.username_entry.bind("<Return>", lambda e: self.do_login())

        # Error label
        self.error_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#E53935"
        )
        self.error_label.pack(pady=4)

        # Login button
        self.login_button = ctk.CTkButton(
            form_frame,
            text=self.translations['login'],
            width=300,
            height=44,
            corner_radius=8,
            fg_color="#1E88E5",
            hover_color="#1565C0",
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.do_login
        )
        self.login_button.pack(pady=16, padx=24)

        # Footer
        footer_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        footer_frame.pack(pady=20)

        welcome_label = ctk.CTkLabel(
            footer_frame,
            text=self.translations['welcome'],
            font=ctk.CTkFont(size=12),
            text_color="#B0B0B0"
        )
        welcome_label.pack()

        developed_label = ctk.CTkLabel(
            footer_frame,
            text=self.translations['developed'],
            font=ctk.CTkFont(size=11),
            text_color="#808080"
        )
        developed_label.pack()

        contact_label = ctk.CTkLabel(
            footer_frame,
            text=self.translations['contact'],
            font=ctk.CTkFont(size=10),
            text_color="#606060"
        )
        contact_label.pack()

        # Set RTL if Arabic
        if self.lang == 'ar':
            self.set_rtl()

    def set_rtl(self):
        """Set RTL layout for Arabic."""
        # Configure text direction
        pass

    def do_login(self):
        """Handle login attempt."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.error_label.configure(text=self.translations['error'])
            return

        # Verify credentials
        user = self.db.verify_user(username, password)

        if user:
            self.logger.info(f"User logged in: {username}")
            self.parent.current_user = user
            self.event_generate("<LoginSuccess>")
        else:
            self.logger.warning(f"Failed login attempt: {username}")
            self.error_label.configure(text=self.translations['error'])
            self.password_entry.delete(0, "end")
