"""
HomeNet - AI Help View
Smart AI assistant for parental guidance
"""

import customtkinter as ctk
import logging


class AIHelpView(ctk.CTkFrame):
    """AI Assistant view with smart parental help."""

    def __init__(self, parent, db, config, ai_assistant, lang='en'):
        super().__init__(parent, fg_color="#1A1A2E")
        self.parent = parent
        self.db = db
        self.config = config
        self.ai = ai_assistant
        self.lang = lang

        self.translations = self.get_translations()
        self.setup_ui()

    def get_translations(self):
        """Get translations."""
        return {
            'en': {
                'title': '🤖 AI Assistant',
                'subtitle': 'Smart Parental Help',
                'ask_question': 'Ask a question...',
                'send': 'Send',
                'quick_help': 'Quick Help',
                'daily_report': 'Daily Report',
                'parental_advice': 'Parental Advice',
                'troubleshoot': 'Troubleshoot',
                'child_age': 'Child Age',
                'get_advice': 'Get Advice',
                'example_questions': 'Example Questions',
                'q1': 'How to block gaming apps?',
                'q2': 'Set up bedtime blocking (11 PM)?',
                'q3': 'Block TikTok and Instagram?',
                'q4': 'Why is my Pi slow?',
                'q5': 'How to add trusted device?',
                'q6': 'Configure email alerts?',
            },
            'ar': {
                'title': '🤖 مساعد الذكاء الاصطناعي',
                'subtitle': 'مساعدة ذكية للوالدين',
                'ask_question': 'اسأل سؤالاً...',
                'send': 'إرسال',
                'quick_help': 'مساعدة سريعة',
                'daily_report': 'التقرير اليومي',
                'parental_advice': 'نصائح تربوية',
                'troubleshoot': 'حل المشكلات',
                'child_age': 'عمر الطفل',
                'get_advice': 'احصل على نصيحة',
                'example_questions': 'أسئلة مقترحة',
                'q1': 'كيف أحظر تطبيقات الألعاب؟',
                'q2': 'ضبط حظر وقت النوم (11 مساءً)؟',
                'q3': 'حظر تيك توك وانستغرام؟',
                'q4': 'لماذا جهازي بطيء؟',
                'q5': 'كيف أضيف جهاز موثوق؟',
                'q6': 'ضبط تنبيهات البريد؟',
            }
        }.get(self.lang, {})

    def setup_ui(self):
        """Setup AI help UI."""
        # Title
        title = ctk.CTkLabel(
            self,
            text=self.translations.get('title', 'AI Assistant'),
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFFFFF"
        )
        title.pack(anchor="w", padx=24, pady=(20, 5))

        subtitle = ctk.CTkLabel(
            self,
            text=self.translations.get('subtitle', 'Smart Help'),
            font=ctk.CTkFont(size=14),
            text_color="#B0B0B0"
        )
        subtitle.pack(anchor="w", padx=24, pady=(0, 20))

        # Main content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        content.grid_columnconfigure(0, weight=2)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        # Chat area
        chat_frame = ctk.CTkFrame(content, fg_color="#16213E", corner_radius=12)
        chat_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Welcome message
        self.welcome_label = ctk.CTkLabel(
            chat_frame,
            text=self.translations.get('title', '🤖 AI Assistant') + "\n" +
                 "Ask me anything about HomeNet! / اسألني أي شيء!",
            font=ctk.CTkFont(size=14),
            text_color="#B0B0B0",
            justify="center"
        )
        self.welcome_label.pack(pady=20)

        # Response area
        self.response_text = ctk.CTkTextbox(
            chat_frame,
            fg_color="#0F3460",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=13),
            wrap="word",
            state="disabled",
            corner_radius=8
        )
        self.response_text.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # Input area
        input_frame = ctk.CTkFrame(chat_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=16, pady=(0, 16))

        self.question_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text=self.translations.get('ask_question', 'Ask a question...'),
            height=44,
            corner_radius=8,
            font=ctk.CTkFont(size=14)
        )
        self.question_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.question_entry.bind("<Return>", lambda e: self.ask_question())

        send_btn = ctk.CTkButton(
            input_frame,
            text=self.translations.get('send', 'Send'),
            width=80,
            height=44,
            corner_radius=8,
            fg_color="#1E88E5",
            command=self.ask_question
        )
        send_btn.pack(side="right")

        # Quick actions panel
        actions_frame = ctk.CTkFrame(content, fg_color="#16213E", corner_radius=12)
        actions_frame.grid(row=0, column=1, sticky="nsew")

        # Quick help
        quick_label = ctk.CTkLabel(
            actions_frame,
            text=self.translations.get('quick_help', 'Quick Help'),
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#FFFFFF"
        )
        quick_label.pack(anchor="w", padx=16, pady=(16, 12))

        # Daily report button
        report_btn = ctk.CTkButton(
            actions_frame,
            text=f"📊 {self.translations.get('daily_report', 'Daily Report')}",
            height=40,
            corner_radius=8,
            fg_color="#43A047",
            anchor="w",
            command=self.show_daily_report
        )
        report_btn.pack(fill="x", padx=12, pady=4)

        # Parental advice
        advice_btn = ctk.CTkButton(
            actions_frame,
            text=f"👨‍👩‍👧 {self.translations.get('parental_advice', 'Parental Advice')}",
            height=40,
            corner_radius=8,
            fg_color="#FF7043",
            anchor="w",
            command=self.show_parental_advice
        )
        advice_btn.pack(fill="x", padx=12, pady=4)

        # Troubleshoot
        trouble_btn = ctk.CTkButton(
            actions_frame,
            text=f"🔧 {self.translations.get('troubleshoot', 'Troubleshoot')}",
            height=40,
            corner_radius=8,
            fg_color="#E53935",
            anchor="w",
            command=self.show_troubleshoot
        )
        trouble_btn.pack(fill="x", padx=12, pady=4)

        # Example questions
        examples_label = ctk.CTkLabel(
            actions_frame,
            text=self.translations.get('example_questions', 'Example Questions'),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#FFFFFF"
        )
        examples_label.pack(anchor="w", padx=16, pady=(20, 8))

        examples = [
            ('q1', 'How to block gaming apps?'),
            ('q2', 'Set up bedtime blocking?'),
            ('q3', 'Block TikTok?'),
            ('q4', 'Why is my Pi slow?'),
            ('q5', 'Add trusted device?'),
            ('q6', 'Email alerts setup?'),
        ]

        for key, text in examples:
            example_btn = ctk.CTkButton(
                actions_frame,
                text=f"• {text}",
                height=32,
                corner_radius=6,
                fg_color="#0F3460",
                anchor="w",
                font=ctk.CTkFont(size=11),
                command=lambda t=text: self.ask_specific(t)
            )
            example_btn.pack(fill="x", padx=12, pady=2)

    def ask_question(self):
        """Ask AI a question."""
        question = self.question_entry.get().strip()
        if not question:
            return

        # Clear input
        self.question_entry.delete(0, "end")

        # Get response
        response = self.ai.ask(question)

        # Display response
        self.display_response(response)

    def ask_specific(self, question: str):
        """Ask a specific question."""
        self.question_entry.delete(0, "end")
        self.question_entry.insert(0, question)
        self.ask_question()

    def display_response(self, response: str):
        """Display AI response."""
        self.response_text.configure(state="normal")
        self.response_text.delete("1.0", "end")
        self.response_text.insert("1.0", response)
        self.response_text.configure(state="disabled")

    def show_daily_report(self):
        """Show daily activity report."""
        report = self.ai.generate_daily_report()
        self.display_response(report)

    def show_parental_advice(self):
        """Show parental advice dialog."""
        # Simple age-based advice
        advice = self.ai.get_parental_advice(10)
        self.display_response(f"👨‍👩‍👧 Parental Advice for 10-year-old:\n\n{advice}")

    def show_troubleshoot(self):
        """Show troubleshooting options."""
        help_text = """
🔧 Common Issues & Solutions:

1️⃣ Blocking Not Working?
   → Check if blocking is ON
   → Restart service: sudo systemctl restart homonet

2️⃣ Raspberry Pi Running Slow?
   → Increase scan interval to 5 min
   → Disable charts in settings
   → Check RAM: free -m

3️⃣ No Email Alerts?
   → Configure SMTP in Settings
   → Check email address is set
   → Enable notifications

4️⃣ Can't Login?
   → Default: admin / 123456
   → Reset: sqlite3 ~/HomeNet/homenet.db "UPDATE users SET password_hash='8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92' WHERE username='admin';"

5️⃣ Need Help?
   → Email: abdalfaqeeh@gmail.com
   → GitHub: github.com/AbduF/HomeNet
"""
        self.display_response(help_text)
