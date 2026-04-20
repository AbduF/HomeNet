"""
HomeNet - Settings View
Application settings and user management
"""

import customtkinter as ctk
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class SettingsView(ctk.CTkFrame):
    """Settings view for application configuration."""

    def __init__(self, parent, db, config, scanner, monitor, blocker, lang='en'):
        super().__init__(parent, fg_color="#1A1A2E")
        self.parent = parent
        self.db = db
        self.config = config
        self.scanner = scanner
        self.monitor = monitor
        self.blocker = blocker
        self.lang = lang
        self.logger = logging.getLogger("HomeNet.Settings")

        self.translations = self.get_translations()
        self.setup_ui()
        self.load_settings()

    def get_translations(self):
        """Get translations."""
        translations = {
            'en': {
                'title': 'Settings',
                'account': 'Account',
                'username': 'Username',
                'password': 'Password',
                'email': 'Email',
                'save': 'Save Changes',
                'language': 'Language',
                'english': 'English',
                'arabic': 'العربية',
                'network': 'Network',
                'interface': 'Network Interface',
                'scan_interval': 'Scan Interval (seconds)',
                'notifications': 'Notifications',
                'alert_new_host': 'Alert on new host',
                'alert_high_traffic': 'Alert on high traffic',
                'traffic_threshold': 'Traffic threshold (MB)',
                'email_settings': 'Email Settings',
                'smtp_host': 'SMTP Host',
                'smtp_port': 'SMTP Port',
                'smtp_user': 'SMTP User',
                'smtp_password': 'SMTP Password',
                'test_email': 'Test Email',
                'about': 'About',
                'version': 'Version',
                'developed': 'Developed in UAE, Al Ain',
                'contact': 'Contact: abdalfaqeeh@gmail.com',
                'reset_password': 'Reset Password',
                'password_updated': 'Password updated successfully',
                'email_updated': 'Email updated successfully',
                'settings_saved': 'Settings saved successfully',
                'current_password': 'Current Password',
                'new_password': 'New Password',
                'confirm_password': 'Confirm Password',
                'password_mismatch': 'Passwords do not match',
                'incorrect_password': 'Current password is incorrect'
            },
            'ar': {
                'title': 'الإعدادات',
                'account': 'الحساب',
                'username': 'اسم المستخدم',
                'password': 'كلمة المرور',
                'email': 'البريد الإلكتروني',
                'save': 'حفظ التغييرات',
                'language': 'اللغة',
                'english': 'English',
                'arabic': 'العربية',
                'network': 'الشبكة',
                'interface': 'واجهة الشبكة',
                'scan_interval': 'فترة الفحص (ثانية)',
                'notifications': 'الإشعارات',
                'alert_new_host': 'تنبيه عند جهاز جديد',
                'alert_high_traffic': 'تنبيه عند بيانات عالية',
                'traffic_threshold': 'حد البيانات (ميجابابت)',
                'email_settings': 'إعدادات البريد',
                'smtp_host': 'خادم SMTP',
                'smtp_port': 'منفذ SMTP',
                'smtp_user': 'مستخدم SMTP',
                'smtp_password': 'كلمة مرور SMTP',
                'test_email': 'اختبار البريد',
                'about': 'حول',
                'version': 'الإصدار',
                'developed': 'تم التطوير في الإمارات، العين',
                'contact': 'للتواصل: abdalfaqeeh@gmail.com',
                'reset_password': 'إعادة تعيين كلمة المرور',
                'password_updated': 'تم تحديث كلمة المرور بنجاح',
                'email_updated': 'تم تحديث البريد بنجاح',
                'settings_saved': 'تم حفظ الإعدادات بنجاح',
                'current_password': 'كلمة المرور الحالية',
                'new_password': 'كلمة المرور الجديدة',
                'confirm_password': 'تأكيد كلمة المرور',
                'password_mismatch': 'كلمات المرور غير متطابقة',
                'incorrect_password': 'كلمة المرور الحالية غير صحيحة'
            }
        }
        return translations.get(self.lang, translations['en'])

    def setup_ui(self):
        """Setup settings view UI."""
        # Title
        title = ctk.CTkLabel(
            self,
            text=self.translations['title'],
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFFFFF"
        )
        title.pack(anchor="w", padx=24, pady=(20, 10))

        # Scrollable content
        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Account section
        self.create_section(
            content,
            f"👤 {self.translations['account']}",
            self.create_account_section
        )

        # Language section
        self.create_section(
            content,
            f"🌍 {self.translations['language']}",
            self.create_language_section
        )

        # Notifications section
        self.create_section(
            content,
            f"🔔 {self.translations['notifications']}",
            self.create_notifications_section
        )

        # Email settings section
        self.create_section(
            content,
            f"📧 {self.translations['email_settings']}",
            self.create_email_section
        )

        # About section
        self.create_section(
            content,
            f"ℹ️ {self.translations['about']}",
            self.create_about_section
        )

    def create_section(self, parent, title, create_content):
        """Create a settings section."""
        section = ctk.CTkFrame(parent, fg_color="#16213E", corner_radius=12)
        section.pack(fill="x", pady=8)

        # Section title
        title_label = ctk.CTkLabel(
            section,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#FFFFFF"
        )
        title_label.pack(anchor="w", padx=16, pady=(16, 8))

        # Content
        content_frame = ctk.CTkFrame(section, fg_color="transparent")
        content_frame.pack(fill="x", padx=16, pady=(0, 16))

        create_content(content_frame)

    def create_account_section(self, parent):
        """Create account settings."""
        # Get current user info
        current_user = self.parent.parent.current_user if hasattr(self.parent.parent, 'current_user') else None
        username = current_user.get('username', 'admin') if current_user else 'admin'
        email = current_user.get('email', '') if current_user else ''

        # Username (read-only)
        user_label = ctk.CTkLabel(parent, text=self.translations['username'], text_color="#B0B0B0", anchor="w")
        user_label.pack(fill="x", pady=(0, 4))
        user_entry = ctk.CTkEntry(parent, width=300)
        user_entry.insert(0, username)
        user_entry.configure(state="disabled")
        user_entry.pack(pady=(0, 12))

        # Email
        email_label = ctk.CTkLabel(parent, text=self.translations['email'], text_color="#B0B0B0", anchor="w")
        email_label.pack(fill="x", pady=(0, 4))
        self.email_entry = ctk.CTkEntry(parent, width=300, placeholder_text="your@email.com")
        self.email_entry.insert(0, email)
        self.email_entry.pack(pady=(0, 12))

        # Current password
        curr_pass_label = ctk.CTkLabel(parent, text=self.translations['current_password'], text_color="#B0B0B0", anchor="w")
        curr_pass_label.pack(fill="x", pady=(0, 4))
        self.curr_pass_entry = ctk.CTkEntry(parent, width=300, show="*")
        self.curr_pass_entry.pack(pady=(0, 12))

        # New password
        new_pass_label = ctk.CTkLabel(parent, text=self.translations['new_password'], text_color="#B0B0B0", anchor="w")
        new_pass_label.pack(fill="x", pady=(0, 4))
        self.new_pass_entry = ctk.CTkEntry(parent, width=300, show="*")
        self.new_pass_entry.pack(pady=(0, 12))

        # Confirm password
        confirm_label = ctk.CTkLabel(parent, text=self.translations['confirm_password'], text_color="#B0B0B0", anchor="w")
        confirm_label.pack(fill="x", pady=(0, 4))
        self.confirm_pass_entry = ctk.CTkEntry(parent, width=300, show="*")
        self.confirm_pass_entry.pack(pady=(0, 12))

        # Status label
        self.account_status = ctk.CTkLabel(parent, text="", text_color="#43A047")
        self.account_status.pack(pady=(0, 8))

        # Save button
        save_btn = ctk.CTkButton(
            parent,
            text=f"💾 {self.translations['save']}",
            width=140,
            height=36,
            corner_radius=8,
            fg_color="#1E88E5",
            command=self.save_account
        )
        save_btn.pack(pady=(0, 8))

    def create_language_section(self, parent):
        """Create language settings."""
        self.lang_var = ctk.StringVar(value=self.lang)

        english_btn = ctk.CTkRadioButton(
            parent,
            text=self.translations['english'],
            variable=self.lang_var,
            value="en",
            command=self.change_language
        )
        english_btn.pack(anchor="w", pady=4)

        arabic_btn = ctk.CTkRadioButton(
            parent,
            text=self.translations['arabic'],
            variable=self.lang_var,
            value="ar",
            command=self.change_language
        )
        arabic_btn.pack(anchor="w", pady=4)

    def create_notifications_section(self, parent):
        """Create notification settings."""
        self.alert_new_host = ctk.CTkSwitch(
            parent,
            text=self.translations['alert_new_host'],
            onvalue=1,
            offvalue=0
        )
        if self.config.get('alert_new_host', True):
            self.alert_new_host.select()
        self.alert_new_host.pack(anchor="w", pady=4)

        self.alert_high_traffic = ctk.CTkSwitch(
            parent,
            text=self.translations['alert_high_traffic'],
            onvalue=1,
            offvalue=0
        )
        if self.config.get('alert_high_traffic', True):
            self.alert_high_traffic.select()
        self.alert_high_traffic.pack(anchor="w", pady=4)

        # Save button
        save_btn = ctk.CTkButton(
            parent,
            text=f"💾 {self.translations['save']}",
            width=140,
            height=36,
            corner_radius=8,
            fg_color="#1E88E5",
            command=self.save_notifications
        )
        save_btn.pack(anchor="w", pady=(12, 0))

    def create_email_section(self, parent):
        """Create email settings."""
        # SMTP Host
        host_label = ctk.CTkLabel(parent, text=self.translations['smtp_host'], text_color="#B0B0B0", anchor="w")
        host_label.pack(fill="x", pady=(0, 4))
        self.smtp_host = ctk.CTkEntry(parent, width=300, placeholder_text="smtp.gmail.com")
        self.smtp_host.insert(0, self.config.get('smtp_host', ''))
        self.smtp_host.pack(pady=(0, 8))

        # SMTP Port
        port_label = ctk.CTkLabel(parent, text=self.translations['smtp_port'], text_color="#B0B0B0", anchor="w")
        port_label.pack(fill="x", pady=(0, 4))
        self.smtp_port = ctk.CTkEntry(parent, width=300, placeholder_text="587")
        self.smtp_port.insert(0, str(self.config.get('smtp_port', 587)))
        self.smtp_port.pack(pady=(0, 8))

        # SMTP User
        user_label = ctk.CTkLabel(parent, text=self.translations['smtp_user'], text_color="#B0B0B0", anchor="w")
        user_label.pack(fill="x", pady=(0, 4))
        self.smtp_user = ctk.CTkEntry(parent, width=300)
        self.smtp_user.insert(0, self.config.get('smtp_user', ''))
        self.smtp_user.pack(pady=(0, 8))

        # SMTP Password
        pass_label = ctk.CTkLabel(parent, text=self.translations['smtp_password'], text_color="#B0B0B0", anchor="w")
        pass_label.pack(fill="x", pady=(0, 4))
        self.smtp_password = ctk.CTkEntry(parent, width=300, show="*")
        self.smtp_password.insert(0, self.config.get('smtp_password', ''))
        self.smtp_password.pack(pady=(0, 8))

        # Status label
        self.email_status = ctk.CTkLabel(parent, text="", text_color="#43A047")
        self.email_status.pack(pady=(0, 8))

        # Buttons
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(anchor="w")

        save_btn = ctk.CTkButton(
            btn_frame,
            text=f"💾 {self.translations['save']}",
            width=120,
            height=36,
            corner_radius=8,
            fg_color="#1E88E5",
            command=self.save_email_settings
        )
        save_btn.pack(side="left", padx=(0, 8))

        test_btn = ctk.CTkButton(
            btn_frame,
            text=f"📧 {self.translations['test_email']}",
            width=120,
            height=36,
            corner_radius=8,
            fg_color="#43A047",
            command=self.test_email
        )
        test_btn.pack(side="left")

    def create_about_section(self, parent):
        """Create about section."""
        about_text = f"""
🌐 HomeNet - Parental Network Controller

📌 {self.translations['version']}: 1.0.0

🏠 {self.translations['developed']}

📧 {self.translations['contact']}

━━━━━━━━━━━━━━━━━━━━━━━━

Features:
• Time-based internet blocking (11 PM - 12 AM)
• Network host monitoring
• Traffic analytics
• App and domain blocking
• Real-time alerts
• Bilingual support (English/Arabic)
        """

        about_label = ctk.CTkLabel(
            parent,
            text=about_text,
            font=ctk.CTkFont(size=12),
            text_color="#B0B0B0",
            justify="left",
            anchor="w"
        )
        about_label.pack(anchor="w")

    def load_settings(self):
        """Load current settings."""
        self.lang_var.set(self.lang)
        self.alert_new_host.select() if self.config.get('alert_new_host', True) else None
        self.alert_high_traffic.select() if self.config.get('alert_high_traffic', True) else None

    def save_account(self):
        """Save account settings."""
        try:
            # Verify current password
            current_user = self.parent.parent.current_user if hasattr(self.parent.parent, 'current_user') else None
            username = current_user.get('username', 'admin') if current_user else 'admin'

            curr_pass = self.curr_pass_entry.get()
            new_pass = self.new_pass_entry.get()
            confirm_pass = self.confirm_pass_entry.get()
            email = self.email_entry.get().strip()

            # Update email if provided
            if email:
                self.db.update_user_email(username, email)
                self.email_status.configure(text=self.translations['email_updated'], text_color="#43A047")

            # Update password if provided
            if new_pass:
                if new_pass != confirm_pass:
                    self.account_status.configure(text=self.translations['password_mismatch'], text_color="#E53935")
                    return

                # Verify current password
                user = self.db.verify_user(username, curr_pass)
                if not user:
                    self.account_status.configure(text=self.translations['incorrect_password'], text_color="#E53935")
                    return

                # Update password
                self.db.update_user_password(username, new_pass)
                self.account_status.configure(text=self.translations['password_updated'], text_color="#43A047")

                # Clear fields
                self.curr_pass_entry.delete(0, "end")
                self.new_pass_entry.delete(0, "end")
                self.confirm_pass_entry.delete(0, "end")

        except Exception as e:
            self.logger.error(f"Error saving account: {e}")
            self.account_status.configure(text=str(e), text_color="#E53935")

    def change_language(self):
        """Change application language."""
        new_lang = self.lang_var.get()
        self.config.set('language', new_lang)
        self.parent.parent.change_language("EN" if new_lang == 'en' else "AR")

    def save_notifications(self):
        """Save notification settings."""
        self.config.set('alert_new_host', bool(self.alert_new_host.get()))
        self.config.set('alert_high_traffic', bool(self.alert_high_traffic.get()))

    def save_email_settings(self):
        """Save email settings."""
        self.config.set('smtp_host', self.smtp_host.get())
        self.config.set('smtp_port', int(self.smtp_port.get()))
        self.config.set('smtp_user', self.smtp_user.get())
        self.config.set('smtp_password', self.smtp_password.get())

        self.email_status.configure(text=self.translations['settings_saved'], text_color="#43A047")

    def test_email(self):
        """Send test email."""
        try:
            host = self.smtp_host.get()
            port = int(self.smtp_port.get())
            user = self.smtp_user.get()
            password = self.smtp_password.get()
            admin_email = self.db.get_user('admin').get('email') if self.db.get_user('admin') else 'abdalfaqeeh@gmail.com'

            if not all([host, user, password]):
                self.email_status.configure(text="Please fill all SMTP fields", text_color="#E53935")
                return

            msg = MIMEMultipart()
            msg['From'] = user
            msg['To'] = admin_email
            msg['Subject'] = 'HomeNet - Test Email'

            body = 'This is a test email from HomeNet Parental Network Controller.'
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(host, port)
            server.starttls()
            server.login(user, password)
            server.send_message(msg)
            server.quit()

            self.email_status.configure(text="Test email sent successfully!", text_color="#43A047")

        except Exception as e:
            self.logger.error(f"Email test error: {e}")
            self.email_status.configure(text=f"Error: {str(e)}", text_color="#E53935")
