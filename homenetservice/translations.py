"""
HomeNet — Translation Manager
Full Arabic and English language support with RTL layout indicators.
"""

TRANSLATIONS = {
    "en": {
        # App
        "app_title": "HomeNet — Parental Network Controller",
        "app_subtitle": "Proudly developed in UAE 🇦🇪",
        "version": "Version 1.0.0",

        # Navigation
        "dashboard": "Dashboard",
        "hosts": "Hosts & Devices",
        "traffic": "Traffic Monitor",
        "blocking": "Content Blocking",
        "time_rules": "Time Rules",
        "speed_test": "Speed Test",
        "alerts": "Alerts",
        "settings": "Settings",
        "system": "System",

        # Dashboard
        "welcome": "Welcome to HomeNet",
        "total_hosts": "Total Hosts",
        "active_hosts": "Active Hosts",
        "blocked_hosts": "Blocked",
        "total_traffic": "Total Traffic",
        "network_status": "Network Status",
        "connection_ok": "Connected",
        "connection_error": "Disconnected",
        "current_time": "Current Time",
        "blocking_active": "Blocking Active",
        "blocking_inactive": "Blocking Inactive",

        # Hosts
        "ip_address": "IP Address",
        "mac_address": "MAC Address",
        "hostname": "Hostname",
        "os_type": "OS Type",
        "hardware": "Hardware Info",
        "first_seen": "First Seen",
        "last_seen": "Last Seen",
        "status": "Status",
        "online": "Online",
        "offline": "Offline",
        "blocked": "Blocked",
        "whitelisted": "Whitelisted",
        "actions": "Actions",
        "block": "Block",
        "unblock": "Unblock",
        "whitelist": "Whitelist",
        "remove": "Remove",
        "refresh": "Refresh",
        "scan_network": "Scan Network",
        "no_hosts": "No hosts discovered yet. Click 'Scan Network' to begin.",

        # Traffic
        "bytes_sent": "Bytes Sent",
        "bytes_recv": "Bytes Received",
        "total_bytes": "Total Traffic",
        "top_consumers": "Top Traffic Consumers",
        "traffic_chart": "Traffic Over Time",
        "live_monitoring": "Live Traffic Monitoring",
        "start_monitoring": "Start Monitoring",
        "stop_monitoring": "Stop Monitoring",

        # Blocking
        "block_gaming": "Block Gaming",
        "block_social": "Block Social Media",
        "block_streaming": "Block Streaming",
        "block_all": "Block All Categories",
        "category_enabled": "Enabled",
        "category_disabled": "Disabled",
        "blocked_domains": "Blocked Domains",
        "blocked_ports": "Blocked Ports",
        "custom_rules": "Custom Rules",
        "add_rule": "Add Rule",
        "rule_type": "Rule Type",
        "rule_host": "Block Host",
        "rule_app": "Block App/Service",
        "rule_domain": "Block Domain",
        "rule_port": "Block Port",
        "target": "Target",
        "enabled": "Enabled",

        # Time Rules
        "time_blocking": "Time-Based Blocking",
        "enable_time_blocking": "Enable Time Blocking",
        "block_start": "Block Start Time",
        "block_end": "Block End Time",
        "block_days": "Block Days",
        "monday": "Monday", "tuesday": "Tuesday", "wednesday": "Wednesday",
        "thursday": "Thursday", "friday": "Friday", "saturday": "Saturday",
        "sunday": "Sunday",
        "select_days": "Select Days",
        "whitelisted_hosts": "Whitelisted Hosts (exempt from blocking)",
        "add_whitelist": "Add to Whitelist",

        # Speed Test
        "run_speed_test": "Run Speed Test",
        "download_speed": "Download Speed",
        "upload_speed": "Upload Speed",
        "ping": "Ping",
        "server": "Server",
        "testing": "Testing...",
        "mbps": "Mbps",
        "ms": "ms",
        "test_history": "Test History",

        # Alerts
        "new_host_detected": "New Host Detected",
        "high_traffic_alert": "High Traffic Alert",
        "new_host_msg": "A new device has connected to your network.",
        "high_traffic_msg": "Traffic volume has exceeded the threshold.",
        "mark_all_read": "Mark All as Read",
        "no_alerts": "No alerts",
        "severity_info": "Info",
        "severity_warning": "Warning",
        "severity_critical": "Critical",

        # Settings
        "general_settings": "General Settings",
        "language": "Language",
        "english": "English",
        "arabic": "العربية",
        "network_interface": "Network Interface",
        "log_level": "Log Level",

        # System
        "admin_settings": "Admin Settings",
        "change_username": "Change Username",
        "change_password": "Change Password",
        "recovery_email": "Recovery Email",
        "set_email": "Set Email",
        "current_username": "Current Username",
        "new_username": "New Username",
        "current_password": "Current Password",
        "new_password": "New Password",
        "confirm_password": "Confirm Password",
        "save_changes": "Save Changes",
        "system_info": "System Information",
        "os_info": "OS Information",
        "cpu_usage": "CPU Usage",
        "memory_usage": "Memory Usage",
        "disk_usage": "Disk Usage",
        "uptime": "Uptime",
        "homeNet_status": "HomeNet Status",
        "running": "Running",
        "stopped": "Stopped",

        # Login
        "login": "Login",
        "username": "Username",
        "password": "Password",
        "login_btn": "Sign In",
        "forgot_password": "Forgot Password?",
        "reset_via_email": "Reset via Email",
        "enter_email": "Enter your recovery email",
        "new_pass": "New Password",
        "reset_btn": "Reset Password",
        "login_failed": "Invalid username or password",
        "password_changed": "Password changed successfully!",
        "password_mismatch": "Passwords do not match",

        # Messages
        "saved": "Settings saved successfully!",
        "error": "An error occurred",
        "confirm": "Are you sure?",
        "confirm_block": "Block this host?",
        "confirm_unblock": "Unblock this host?",
        "confirm_delete": "Delete this host?",
        "scanning": "Scanning network...",
        "scan_complete": "Scan complete!",
        "speed_test_complete": "Speed test complete!",
        "rule_added": "Rule added successfully!",
        "rule_deleted": "Rule deleted!",

        # Network
        "gateway": "Gateway",
        "dns_servers": "DNS Servers",
        "subnet": "Subnet",
        "broadcast": "Broadcast",
        "interface_info": "Interface Information",
        "connection_status": "Connection Status",

        # Footer
        "footer": "🌐 HomeNet v1.0.0 — Proudly developed in UAE 🇦🇪",
    },

    "ar": {
        # App
        "app_title": "هوم نت — وحدة التحكم في الشبكة المنزلية",
        "app_subtitle": "تم تطويره بكل فخر في الإمارات 🇦",
        "version": "الإصدار 1.0.0",

        # Navigation
        "dashboard": "لوحة التحكم",
        "hosts": "الأجهزة المضيفة",
        "traffic": "مراقبة حركة البيانات",
        "blocking": "حظر المحتوى",
        "time_rules": "قواعد الوقت",
        "speed_test": "اختبار السرعة",
        "alerts": "التنبيهات",
        "settings": "الإعدادات",
        "system": "النظام",

        # Dashboard
        "welcome": "مرحباً بك في هوم نت",
        "total_hosts": "إجمالي الأجهزة",
        "active_hosts": "الأجهزة النشطة",
        "blocked_hosts": "محظور",
        "total_traffic": "إجمالي الحركة",
        "network_status": "حالة الشبكة",
        "connection_ok": "متصل",
        "connection_error": "غير متصل",
        "current_time": "الوقت الحالي",
        "blocking_active": "الحظر نشط",
        "blocking_inactive": "الحظر غير نشط",

        # Hosts
        "ip_address": "عنوان IP",
        "mac_address": "عنوان MAC",
        "hostname": "اسم المضيف",
        "os_type": "نظام التشغيل",
        "hardware": "معلومات الجهاز",
        "first_seen": "أول ظهور",
        "last_seen": "آخر ظهور",
        "status": "الحالة",
        "online": "متصل",
        "offline": "غير متصل",
        "blocked": "محظور",
        "whitelisted": "مسموح",
        "actions": "الإجراءات",
        "block": "حظر",
        "unblock": "إلغاء الحظر",
        "whitelist": "قائمة السماح",
        "remove": "حذف",
        "refresh": "تحديث",
        "scan_network": "فحص الشبكة",
        "no_hosts": "لم يتم اكتشاف أجهزة بعد. اضغط 'فحص الشبكة' للبدء.",

        # Traffic
        "bytes_sent": "البايتات المرسلة",
        "bytes_recv": "البايتات المستلمة",
        "total_bytes": "إجمالي الحركة",
        "top_consumers": "أكثر الأجهزة استخداماً",
        "traffic_chart": "حركة البيانات عبر الوقت",
        "live_monitoring": "مراقبة مباشرة لحركة البيانات",
        "start_monitoring": "بدء المراقبة",
        "stop_monitoring": "إيقاف المراقبة",

        # Blocking
        "block_gaming": "حظر الألعاب",
        "block_social": "حظر وسائل التواصل",
        "block_streaming": "حظر البث",
        "block_all": "حظر جميع الفئات",
        "category_enabled": "مفعل",
        "category_disabled": "معطل",
        "blocked_domains": "النطاقات المحظورة",
        "blocked_ports": "المنافذ المحظورة",
        "custom_rules": "قواعد مخصصة",
        "add_rule": "إضافة قاعدة",
        "rule_type": "نوع القاعدة",
        "rule_host": "حظر مضيف",
        "rule_app": "حظر تطبيق/خدمة",
        "rule_domain": "حظر نطاق",
        "rule_port": "حظر منفذ",
        "target": "الهدف",
        "enabled": "مفعل",

        # Time Rules
        "time_blocking": "الحظر بناءً على الوقت",
        "enable_time_blocking": "تفعيل الحظر الزمني",
        "block_start": "وقت بدء الحظر",
        "block_end": "وقت انتهاء الحظر",
        "block_days": "أيام الحظر",
        "monday": "الاثنين", "tuesday": "الثلاثاء", "wednesday": "الأربعاء",
        "thursday": "الخميس", "friday": "الجمعة", "saturday": "السبت",
        "sunday": "الأحد",
        "select_days": "اختر الأيام",
        "whitelisted_hosts": "الأجهزة المستثناة من الحظر",
        "add_whitelist": "إضافة إلى قائمة السماح",

        # Speed Test
        "run_speed_test": "تشغيل اختبار السرعة",
        "download_speed": "سرعة التحميل",
        "upload_speed": "سرعة الرفع",
        "ping": "زمن الاستجابة",
        "server": "الخادم",
        "testing": "جارٍ الاختبار...",
        "mbps": "ميغابت/ث",
        "ms": "مللي ثانية",
        "test_history": "سجل الاختبارات",

        # Alerts
        "new_host_detected": "تم اكتشاف جهاز جديد",
        "high_traffic_alert": "تنبيه حركة بيانات عالية",
        "new_host_msg": "تم اتصال جهاز جديد بشبكتك.",
        "high_traffic_msg": "تجاوز حجم حركة البيانات الحد المحدد.",
        "mark_all_read": "تحديد الكل كمقروء",
        "no_alerts": "لا توجد تنبيهات",
        "severity_info": "معلومات",
        "severity_warning": "تحذير",
        "severity_critical": "حرج",

        # Settings
        "general_settings": "الإعدادات العامة",
        "language": "اللغة",
        "english": "English",
        "arabic": "العربية",
        "network_interface": "واجهة الشبكة",
        "log_level": "مستوى السجل",

        # System
        "admin_settings": "إعدادات المسؤول",
        "change_username": "تغيير اسم المستخدم",
        "change_password": "تغيير كلمة المرور",
        "recovery_email": "البريد الإلكتروني للاسترداد",
        "set_email": "تعيين البريد",
        "current_username": "اسم المستخدم الحالي",
        "new_username": "اسم المستخدم الجديد",
        "current_password": "كلمة المرور الحالية",
        "new_password": "كلمة المرور الجديدة",
        "confirm_password": "تأكيد كلمة المرور",
        "save_changes": "حفظ التغييرات",
        "system_info": "معلومات النظام",
        "os_info": "معلومات نظام التشغيل",
        "cpu_usage": "استخدام المعالج",
        "memory_usage": "استخدام الذاكرة",
        "disk_usage": "استخدام القرص",
        "uptime": "وقت التشغيل",
        "homeNet_status": "حالة هوم نت",
        "running": "يعمل",
        "stopped": "متوقف",

        # Login
        "login": "تسجيل الدخول",
        "username": "اسم المستخدم",
        "password": "كلمة المرور",
        "login_btn": "دخول",
        "forgot_password": "نسيت كلمة المرور؟",
        "reset_via_email": "إعادة التعيين عبر البريد",
        "enter_email": "أدخل بريد الاسترداد",
        "new_pass": "كلمة مرور جديدة",
        "reset_btn": "إعادة تعيين",
        "login_failed": "اسم المستخدم أو كلمة المرور غير صحيحة",
        "password_changed": "تم تغيير كلمة المرور بنجاح!",
        "password_mismatch": "كلمتا المرور غير متطابقتين",

        # Messages
        "saved": "تم حفظ الإعدادات بنجاح!",
        "error": "حدث خطأ",
        "confirm": "هل أنت متأكد؟",
        "confirm_block": "حظر هذا الجهاز؟",
        "confirm_unblock": "إلغاء حظر هذا الجهاز؟",
        "confirm_delete": "حذف هذا الجهاز؟",
        "scanning": "جارٍ فحص الشبكة...",
        "scan_complete": "اكتمل الفحص!",
        "speed_test_complete": "اكتمل اختبار السرعة!",
        "rule_added": "تمت إضافة القاعدة بنجاح!",
        "rule_deleted": "تم حذف القاعدة!",

        # Network
        "gateway": "البوابة",
        "dns_servers": "خوادم DNS",
        "subnet": "الشبكة الفرعية",
        "broadcast": "البث",
        "interface_info": "معلومات الواجهة",
        "connection_status": "حالة الاتصال",

        # Footer
        "footer": "🌐 هوم نت v1.0.0 — تم تطويره بكل فخر في الإمارات 🇦🇪",
    },
}


class TranslationManager:
    """Manages translations between Arabic and English."""

    def __init__(self, language: str = "en"):
        self.language = language if language in TRANSLATIONS else "en"
        self.rtl = self.language == "ar"

    def set_language(self, language: str) -> None:
        """Switch language."""
        if language in TRANSLATIONS:
            self.language = language
            self.rtl = language == "ar"

    def get(self, key: str, default: str = "") -> str:
        """Get translation for a key."""
        return TRANSLATIONS.get(self.language, {}).get(key, default)

    def get_all(self) -> dict:
        """Get all translations for current language."""
        return TRANSLATIONS.get(self.language, {})

    def is_rtl(self) -> bool:
        """Check if current language is right-to-left."""
        return self.rtl