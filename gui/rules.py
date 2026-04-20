"""
HomeNet - Rules View
Blocking rules configuration
"""

import customtkinter as ctk
import json
import logging
from datetime import time


class RulesView(ctk.CTkFrame):
    """Rules configuration view."""

    def __init__(self, parent, db, config, scanner, monitor, blocker, lang='en'):
        super().__init__(parent, fg_color="#1A1A2E")
        self.parent = parent
        self.db = db
        self.config = config
        self.scanner = scanner
        self.monitor = monitor
        self.blocker = blocker
        self.lang = lang
        self.logger = logging.getLogger("HomeNet.Rules")

        self.translations = self.get_translations()
        self.setup_ui()
        self.load_rules()
        self.load_schedules()

    def get_translations(self):
        """Get translations."""
        translations = {
            'en': {
                'title': 'Blocking Rules',
                'schedules': 'Time Schedules',
                'apps': 'App Categories',
                'domains': 'Custom Domains',
                'add_rule': 'Add Rule',
                'add_schedule': 'Add Schedule',
                'name': 'Name',
                'category': 'Category',
                'pattern': 'Pattern',
                'enabled': 'Enabled',
                'action': 'Action',
                'time': 'Time',
                'days': 'Days',
                'gaming': 'Gaming',
                'social': 'Social Media',
                'streaming': 'Streaming',
                'custom': 'Custom',
                'block': 'Block',
                'allow': 'Allow',
                'delete': 'Delete',
                'save': 'Save',
                'cancel': 'Cancel',
                'start_time': 'Start Time',
                'end_time': 'End Time',
                'all_days': 'All Days',
                'weekdays': 'Weekdays',
                'weekends': 'Weekends',
                'no_rules': 'No rules configured',
                'no_schedules': 'No schedules configured',
                'default_blocking': 'Default: 11 PM - 12 AM',
                'kids_sleep_time': 'Kids Sleep Time'
            },
            'ar': {
                'title': 'قواعد الحظر',
                'schedules': 'جداول الوقت',
                'apps': 'فئات التطبيقات',
                'domains': 'النطاقات المخصصة',
                'add_rule': 'إضافة قاعدة',
                'add_schedule': 'إضافة جدول',
                'name': 'الاسم',
                'category': 'الفئة',
                'pattern': 'النمط',
                'enabled': 'مفعّل',
                'action': 'الإجراء',
                'time': 'الوقت',
                'days': 'الأيام',
                'gaming': 'الألعاب',
                'social': 'وسائل التواصل',
                'streaming': 'البث',
                'custom': 'مخصص',
                'block': 'حظر',
                'allow': 'سماح',
                'delete': 'حذف',
                'save': 'حفظ',
                'cancel': 'إلغاء',
                'start_time': 'وقت البدء',
                'end_time': 'وقت الانتهاء',
                'all_days': 'جميع الأيام',
                'weekdays': 'أيام العمل',
                'weekends': 'نهاية الأسبوع',
                'no_rules': 'لا توجد قواعد',
                'no_schedules': 'لا توجد جداول',
                'default_blocking': 'افتراضي: 11 مساءً - 12 صباحاً',
                'kids_sleep_time': 'وقت نوم الأطفال'
            }
        }
        return translations.get(self.lang, translations['en'])

    def setup_ui(self):
        """Setup rules view UI."""
        # Title
        title = ctk.CTkLabel(
            self,
            text=self.translations['title'],
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFFFFF"
        )
        title.pack(anchor="w", padx=24, pady=(20, 10))

        # Notebooks for tabs
        notebook = ctk.CTkTabview(self, fg_color="#16213E", segmented_button_fg_color="#0F3460")
        notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Schedules tab
        schedules_tab = notebook.add(self.translations['schedules'])
        self.setup_schedules_tab(schedules_tab)

        # Apps tab
        apps_tab = notebook.add(self.translations['apps'])
        self.setup_apps_tab(apps_tab)

        # Custom tab
        custom_tab = notebook.add(self.translations['domains'])
        self.setup_custom_tab(custom_tab)

    def setup_schedules_tab(self, parent):
        """Setup schedules tab."""
        # Header
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(16, 8))

        header_label = ctk.CTkLabel(
            header,
            text=f"⏰ {self.translations['schedules']} ({self.translations['default_blocking']})",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#FFFFFF"
        )
        header_label.pack(side="left")

        add_btn = ctk.CTkButton(
            header,
            text=f"+ {self.translations['add_schedule']}",
            width=140,
            height=36,
            corner_radius=8,
            fg_color="#1E88E5",
            command=self.show_add_schedule_dialog
        )
        add_btn.pack(side="right")

        # Schedules list
        self.schedules_list = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.schedules_list.pack(fill="both", expand=True, padx=16, pady=8)

    def setup_apps_tab(self, parent):
        """Setup apps tab with categories."""
        # Header
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(16, 8))

        header_label = ctk.CTkLabel(
            header,
            text=f"🎮 {self.translations['apps']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#FFFFFF"
        )
        header_label.pack(side="left")

        # Categories
        categories = ['gaming', 'social', 'streaming']
        self.category_toggles = {}

        for cat in categories:
            toggle = ctk.CTkSwitch(
                header,
                text=self.translations.get(cat, cat).title(),
                onvalue=1,
                offvalue=0,
                command=lambda c=cat: self.toggle_category(c)
            )
            toggle.select()
            toggle.pack(side="right", padx=12)
            self.category_toggles[cat] = toggle

        # Rules list
        self.rules_list = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.rules_list.pack(fill="both", expand=True, padx=16, pady=8)

    def setup_custom_tab(self, parent):
        """Setup custom domains tab."""
        # Header
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(16, 8))

        header_label = ctk.CTkLabel(
            header,
            text=f"🌐 {self.translations['domains']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#FFFFFF"
        )
        header_label.pack(side="left")

        add_btn = ctk.CTkButton(
            header,
            text=f"+ {self.translations['add_rule']}",
            width=140,
            height=36,
            corner_radius=8,
            fg_color="#1E88E5",
            command=self.show_add_custom_rule_dialog
        )
        add_btn.pack(side="right")

        # Custom rules list
        self.custom_rules_list = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.custom_rules_list.pack(fill="both", expand=True, padx=16, pady=8)

    def load_rules(self):
        """Load blocking rules."""
        try:
            # Load app rules
            self.load_app_rules()

            # Load custom rules
            self.load_custom_rules()

        except Exception as e:
            self.logger.error(f"Error loading rules: {e}")

    def load_app_rules(self):
        """Load app blocking rules."""
        # Clear existing
        for widget in self.rules_list.winfo_children():
            widget.destroy()

        rules = self.db.get_rules(type='app')

        for rule in rules:
            self.add_rule_item(self.rules_list, rule)

    def load_custom_rules(self):
        """Load custom blocking rules."""
        # Clear existing
        for widget in self.custom_rules_list.winfo_children():
            widget.destroy()

        rules = self.db.get_rules(type='custom')

        for rule in rules:
            self.add_rule_item(self.custom_rules_list, rule, custom=True)

    def add_rule_item(self, parent, rule, custom=False):
        """Add rule item to list."""
        item = ctk.CTkFrame(parent, fg_color="#0F3460", corner_radius=8)
        item.pack(fill="x", pady=4)

        # Toggle
        toggle = ctk.CTkSwitch(
            item,
            text="",
            onvalue=1,
            offvalue=0,
            width=40
        )
        if rule.get('enabled'):
            toggle.select()
        toggle.configure(command=lambda t, r=rule: self.toggle_rule(r))
        toggle.pack(side="left", padx=12)

        # Name and pattern
        info_frame = ctk.CTkFrame(item, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=8, pady=8)

        name_label = ctk.CTkLabel(
            info_frame,
            text=rule.get('name', ''),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#FFFFFF",
            anchor="w"
        )
        name_label.pack(fill="x")

        pattern_label = ctk.CTkLabel(
            info_frame,
            text=rule.get('pattern', ''),
            font=ctk.CTkFont(size=11),
            text_color="#B0B0B0",
            anchor="w"
        )
        pattern_label.pack(fill="x")

        # Category badge
        category = rule.get('category', 'custom')
        colors = {'gaming': '#FF7043', 'social': '#1E88E5', 'streaming': '#E53935', 'custom': '#43A047'}
        badge = ctk.CTkLabel(
            item,
            text=self.translations.get(category, category).title(),
            font=ctk.CTkFont(size=10),
            text_color="#FFFFFF",
            fg_color=colors.get(category, '#43A047'),
            corner_radius=4,
            width=80,
            height=20
        )
        badge.pack(side="left", padx=8)

        # Delete button
        delete_btn = ctk.CTkButton(
            item,
            text="🗑️",
            width=36,
            height=36,
            corner_radius=6,
            fg_color="#E53935",
            hover_color="#C62828",
            command=lambda r=rule: self.delete_rule(r)
        )
        delete_btn.pack(side="right", padx=8, pady=8)

    def load_schedules(self):
        """Load blocking schedules."""
        try:
            # Clear existing
            for widget in self.schedules_list.winfo_children():
                widget.destroy()

            schedules = self.db.get_schedules()

            if not schedules:
                # Add default schedule
                self.db.add_schedule(
                    name=self.translations.get('kids_sleep_time', 'Kids Sleep Time'),
                    start_time="23:00",
                    end_time="00:00",
                    days=[0, 1, 2, 3, 4, 5, 6]
                )
                schedules = self.db.get_schedules()

            for schedule in schedules:
                self.add_schedule_item(schedule)

        except Exception as e:
            self.logger.error(f"Error loading schedules: {e}")

    def add_schedule_item(self, schedule):
        """Add schedule item to list."""
        item = ctk.CTkFrame(self.schedules_list, fg_color="#0F3460", corner_radius=8)
        item.pack(fill="x", pady=4)

        # Toggle
        toggle = ctk.CTkSwitch(
            item,
            text="",
            onvalue=1,
            offvalue=0,
            width=40
        )
        if schedule.get('enabled'):
            toggle.select()
        toggle.configure(command=lambda t, s=schedule: self.toggle_schedule(s))
        toggle.pack(side="left", padx=12)

        # Info
        info_frame = ctk.CTkFrame(item, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=8, pady=8)

        name_label = ctk.CTkLabel(
            info_frame,
            text=schedule.get('name', ''),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#FFFFFF",
            anchor="w"
        )
        name_label.pack(fill="x")

        # Parse days
        days_str = schedule.get('days', '[]')
        if isinstance(days_str, str):
            try:
                days = json.loads(days_str)
            except:
                days = [0, 1, 2, 3, 4, 5, 6]
        else:
            days = days_str

        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        active_days = [day_names[d] for d in days if 0 <= d <= 6]

        time_label = ctk.CTkLabel(
            info_frame,
            text=f"{schedule.get('start_time', '')} - {schedule.get('end_time', '')} | {', '.join(active_days)}",
            font=ctk.CTkFont(size=11),
            text_color="#B0B0B0",
            anchor="w"
        )
        time_label.pack(fill="x")

        # Delete button
        delete_btn = ctk.CTkButton(
            item,
            text="🗑️",
            width=36,
            height=36,
            corner_radius=6,
            fg_color="#E53935",
            hover_color="#C62828",
            command=lambda s=schedule: self.delete_schedule(s)
        )
        delete_btn.pack(side="right", padx=8, pady=8)

    def toggle_rule(self, rule):
        """Toggle rule enabled status."""
        self.db.toggle_rule(rule['id'], not rule.get('enabled'))
        self.load_rules()

    def toggle_schedule(self, schedule):
        """Toggle schedule enabled status."""
        self.db.toggle_schedule(schedule['id'], not schedule.get('enabled'))

    def toggle_category(self, category):
        """Toggle all rules in category."""
        rules = self.db.get_rules(category=category)
        enabled = self.category_toggles[category].get()

        for rule in rules:
            self.db.toggle_rule(rule['id'], enabled)

        self.load_rules()

    def delete_rule(self, rule):
        """Delete blocking rule."""
        self.db.delete_rule(rule['id'])
        self.load_rules()

    def delete_schedule(self, schedule):
        """Delete schedule."""
        self.db.delete_schedule(schedule['id'])
        self.load_schedules()

    def show_add_schedule_dialog(self):
        """Show dialog to add new schedule."""
        dialog = ctk.CTkToplevel(self)
        dialog.title(self.translations['add_schedule'])
        dialog.geometry("400x400")
        dialog.transient(self)
        dialog.grab_set()

        # Make it modal
        dialog.frame = ctk.CTkFrame(dialog, fg_color="#16213E")
        dialog.frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Name
        name_label = ctk.CTkLabel(dialog.frame, text=self.translations['name'], text_color="#FFFFFF")
        name_label.pack(anchor="w", pady=(0, 4))
        name_entry = ctk.CTkEntry(dialog.frame, width=300, placeholder_text="Schedule name")
        name_entry.pack(pady=(0, 12))

        # Time inputs
        time_frame = ctk.CTkFrame(dialog.frame, fg_color="transparent")
        time_frame.pack(fill="x", pady=8)

        start_label = ctk.CTkLabel(time_frame, text=self.translations['start_time'], text_color="#FFFFFF")
        start_label.pack(side="left", padx=(0, 8))
        start_entry = ctk.CTkEntry(time_frame, width=100, placeholder_text="23:00")
        start_entry.pack(side="left", padx=(0, 20))

        end_label = ctk.CTkLabel(time_frame, text=self.translations['end_time'], text_color="#FFFFFF")
        end_label.pack(side="left", padx=(0, 8))
        end_entry = ctk.CTkEntry(time_frame, width=100, placeholder_text="00:00")
        end_entry.pack(side="left")

        # Buttons
        btn_frame = ctk.CTkFrame(dialog.frame, fg_color="transparent")
        btn_frame.pack(side="bottom", pady=16)

        def save():
            name = name_entry.get().strip()
            start = start_entry.get().strip()
            end = end_entry.get().strip()

            if name and start and end:
                self.db.add_schedule(name, start, end)
                self.load_schedules()
                dialog.destroy()

        cancel_btn = ctk.CTkButton(btn_frame, text=self.translations['cancel'], width=100,
                                   command=dialog.destroy, fg_color="#666666")
        cancel_btn.pack(side="left", padx=8)

        save_btn = ctk.CTkButton(btn_frame, text=self.translations['save'], width=100,
                                 command=save, fg_color="#1E88E5")
        save_btn.pack(side="left", padx=8)

    def show_add_custom_rule_dialog(self):
        """Show dialog to add custom rule."""
        dialog = ctk.CTkToplevel(self)
        dialog.title(self.translations['add_rule'])
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()

        dialog.frame = ctk.CTkFrame(dialog, fg_color="#16213E")
        dialog.frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Name
        name_label = ctk.CTkLabel(dialog.frame, text=self.translations['name'], text_color="#FFFFFF")
        name_label.pack(anchor="w", pady=(0, 4))
        name_entry = ctk.CTkEntry(dialog.frame, width=300, placeholder_text="Rule name")
        name_entry.pack(pady=(0, 12))

        # Pattern (domain)
        pattern_label = ctk.CTkLabel(dialog.frame, text=self.translations['pattern'], text_color="#FFFFFF")
        pattern_label.pack(anchor="w", pady=(0, 4))
        pattern_entry = ctk.CTkEntry(dialog.frame, width=300, placeholder_text="example.com")
        pattern_entry.pack(pady=(0, 12))

        # Buttons
        btn_frame = ctk.CTkFrame(dialog.frame, fg_color="transparent")
        btn_frame.pack(side="bottom", pady=16)

        def save():
            name = name_entry.get().strip()
            pattern = pattern_entry.get().strip()

            if name and pattern:
                self.db.add_rule(name, pattern, rule_type='custom', category='custom')
                self.load_custom_rules()
                dialog.destroy()

        cancel_btn = ctk.CTkButton(btn_frame, text=self.translations['cancel'], width=100,
                                    command=dialog.destroy, fg_color="#666666")
        cancel_btn.pack(side="left", padx=8)

        save_btn = ctk.CTkButton(btn_frame, text=self.translations['save'], width=100,
                                 command=save, fg_color="#1E88E5")
        save_btn.pack(side="left", padx=8)
