"""
HomeNet - AI Assistant Module
GLM5 Integration for Smart Parental Guidance
Free AI-powered help and diagnostics
"""

import logging
import requests
import json
from datetime import datetime

# GLM5 API Configuration
GLM_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
GLM_API_KEY = ""  # User can add their own key

class AIAssistant:
    """AI Assistant using GLM5 for parental guidance."""

    # Context about HomeNet
    CONTEXT = """
    You are HomeNet AI Assistant, a parental network controller.
    You help parents:
    - Set up internet blocking schedules (11 PM - 12 AM default)
    - Block gaming apps (Steam, Roblox, Minecraft, etc.)
    - Block social media (TikTok, Instagram, Snapchat, etc.)
    - Block streaming (Netflix, YouTube, Disney+, etc.)
    - Monitor children's device usage
    - Configure Raspberry Pi 3 for home network control

    Keep responses short, helpful, and family-friendly.
    Respond in the same language as the user's question.
    """

    # Pre-defined responses for offline mode
    LOCAL_RESPONSES = {
        "en": {
            "block": "To block a device, go to Hosts → find device → click Block.",
            "schedule": "Default schedule blocks internet 11 PM - 12 AM. Edit in Rules → Schedules.",
            "wifi": "Connect Raspberry Pi to router via Ethernet for best performance.",
            "performance": "For better Pi 3 performance: disable charts, increase scan interval to 5 min.",
            "gaming": "Block gaming apps in Rules → Apps → Gaming category toggle.",
            "social": "Block social media in Rules → Apps → Social Media toggle.",
            "kids_age": "Recommended: 10+ can have gaming, 13+ social media, 16+ streaming.",
            "password": "Change password in Settings → Account → Update Password.",
            "email": "Configure email in Settings → Email for alert notifications.",
            "raspberry": "Raspberry Pi 3 recommended. Use Ethernet for stability.",
            "language": "Switch language in sidebar: EN for English, AR for Arabic.",
            "new_device": "When new device connects, you'll get an alert. Then choose block/allow.",
            "trusted": "Mark trusted devices to never block. Edit in Hosts → trusted toggle.",
            "speedtest": "Run speed test in Traffic → Speed Test button.",
            "troubleshooting": "Check logs: tail -f ~/HomeNet/logs/homenet.log"
        },
        "ar": {
            "block": "لحظر جهاز: الأقران ← ابحث عن الجهاز ← انقر حظر",
            "schedule": "الجدول الافتراضي يحظر الإنترنت من 11 مساءً - 12 صباحاً",
            "wifi": "وصّل راسبيري بي بـ Ethernet للاستقرار",
            "performance": "لأداء أفضل: أوقف الرسوم البيانية، زد فترة الفحص لـ 5 دقائق",
            "gaming": "احظر الألعاب في القواعد ← التطبيقات ← تبديل الألعاب",
            "social": "احظر وسائل التواصل في القواعد ← التطبيقات ← تبديل التواصل الاجتماعي",
            "kids_age": "موصى به: 10+ للألعاب، 13+ للتواصل، 16+ للبث",
            "password": "غيّر كلمة المرور في الإعدادات ← الحساب",
            "email": "اضبط البريد في الإعدادات ← البريد للتنبيهات",
            "raspberry": "راسبيري بي 3 موصى به. استخدم Ethernet",
            "language": "بدّل اللغة: EN للإنجليزية، AR للعربية",
            "new_device": "عند اتصال جهاز جديد ستتلقى تنبيهاً",
            "trusted": "علّم الأجهزة الموثوقة بعدم الحظر",
            "speedtest": "اختبر السرعة في البيانات ← زر اختبار السرعة",
            "troubleshooting": "تحقق من السجلات: tail -f ~/HomeNet/logs/homenet.log"
        }
    }

    def __init__(self, db=None, config=None):
        self.db = db
        self.config = config
        self.logger = logging.getLogger("HomeNet.AI")
        self.lang = config.get('language', 'en') if config else 'en'
        self.api_key = config.get('glm_api_key', '') if config else ''
        self.enabled = bool(self.api_key)

    def ask(self, question: str) -> str:
        """Ask AI assistant a question."""
        self.logger.info(f"AI question: {question}")

        # Check for local responses first (offline mode)
        question_lower = question.lower()

        # Match keywords
        for keyword, response in self.LOCAL_RESPONSES.get(self.lang, self.LOCAL_RESPONSES['en']).items():
            if keyword in question_lower:
                return response

        # Try GLM5 if enabled
        if self.enabled and self.api_key:
            try:
                return self._call_glm5(question)
            except Exception as e:
                self.logger.warning(f"GLM5 error: {e}, falling back to local")

        # Default response
        return self._get_default_response(question)

    def _call_glm5(self, question: str) -> str:
        """Call GLM5 API for response."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "glm-4-flash",
            "messages": [
                {"role": "system", "content": self.CONTEXT},
                {"role": "user", "content": question}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }

        try:
            response = requests.post(
                GLM_API_URL,
                headers=headers,
                json=data,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                self.logger.warning(f"GLM5 API error: {response.status_code}")
                return None

        except requests.exceptions.Timeout:
            self.logger.warning("GLM5 API timeout")
            return None
        except Exception as e:
            self.logger.error(f"GLM5 error: {e}")
            return None

    def _get_default_response(self, question: str) -> str:
        """Get default response based on keywords."""
        responses = self.LOCAL_RESPONSES.get(self.lang, self.LOCAL_RESPONSES['en'])

        question_lower = question.lower()

        # Keyword mapping
        keywords = {
            'block': ['block', 'حظر', 'حجب'],
            'schedule': ['schedule', 'time', 'وقت', 'الجدول', '11', '12'],
            'wifi': ['wifi', 'wireless', 'واي فاي', 'شبكة'],
            'performance': ['slow', 'performance', 'بطيء', 'أداء', 'memory', 'رام'],
            'gaming': ['gaming', 'game', 'ألعاب', 'لعبة', 'steam', 'roblox'],
            'social': ['social', 'facebook', 'tiktok', 'instagram', 'تواصل'],
            'raspberry': ['raspberry', 'pi', 'راسبيري', 'باي'],
            'password': ['password', 'كلمة المرور', 'تسجيل'],
            'email': ['email', 'mail', 'بريد', 'إشعار'],
            'language': ['language', 'arabic', 'english', 'اللغة', 'عربي'],
            'trusted': ['trusted', 'trusted', 'موثوق', 'استثناء'],
            'speedtest': ['speed', 'test', 'سرعة', 'اختبار'],
        }

        for key, words in keywords.items():
            if any(word in question_lower for word in words):
                return responses.get(key, responses.get('block'))

        # Default help
        if self.lang == 'ar':
            return "اكتب سؤالك بوضوح. مثل: 'كيف أحظر جهاز؟' أو 'كيف أغير كلمة المرور؟'"
        return "Try asking: 'How to block a device?', 'Set up schedule', or 'Block gaming apps'"

    def generate_daily_report(self) -> str:
        """Generate AI-powered daily activity report."""
        if not self.db:
            return self._get_default_report()

        try:
            # Get data
            hosts = self.db.get_hosts()
            alerts = self.db.get_alerts(limit=10)
            stats = self.db.get_traffic_stats(hours=24)
            blocked_hosts = [h for h in hosts if h.get('blocked')]

            # Calculate stats
            total_alerts = len(alerts)
            new_devices = len([a for a in alerts if a.get('type') == 'new_host'])
            active_hosts = len([h for h in hosts if h.get('last_seen')])

            # Build report
            if self.lang == 'ar':
                report = f"""
📊 تقرير HomeNet اليومي

👥 الأجهزة: {active_hosts} جهاز نشط
🚫 المحظورة: {len(blocked_hosts)} جهاز
🔔 التنبيهات: {total_alerts} تنبيه
🆕 أجهزة جديدة: {new_devices} جهاز

💡 نصيحة: راجع الأجهزة الجديدة للتأكد من أنها أجهزة عائلية
"""
            else:
                report = f"""
📊 HomeNet Daily Report

👥 Devices: {active_hosts} active
🚫 Blocked: {len(blocked_hosts)} devices
🔔 Alerts: {total_alerts} alerts
🆕 New Devices: {new_devices} devices

💡 Tip: Review new devices to ensure family safety
"""
            return report

        except Exception as e:
            self.logger.error(f"Report generation error: {e}")
            return self._get_default_report()

    def _get_default_report(self) -> str:
        """Get default report."""
        if self.lang == 'ar':
            return "📊 تقرير HomeNet اليومي\n\nتحقق من التطبيق لمزيد من التفاصيل"
        return "📊 HomeNet Daily Report\n\nCheck the app for details"

    def get_parental_advice(self, child_age: int = 10) -> str:
        """Get age-appropriate parental advice."""
        advice = {
            'en': {
                'under_8': "Age 6-7: No gaming, limited streaming (1hr/day), no social media.",
                '8_12': "Age 8-12: Light gaming (1hr), supervised streaming, no social media.",
                '13_15': "Age 13-15: Moderate gaming (2hr), streaming (2hr), limited social media.",
                '16_plus': "Age 16+: Guided access, focus on education, open communication."
            },
            'ar': {
                'under_8': "العمر 6-7: لا ألعاب، بث محدود (ساعة يومياً)، لا تواصل",
                '8_12': "العمر 8-12: ألعاب خفيفة (ساعة)، بث بإشراف، لا تواصل",
                '13_15': "العمر 13-15: ألعاب معتدلة (ساعتين)، بث (ساعتين)، تواصل محدود",
                '16_plus': "العمر 16+: إرشاد، التركيز على التعليم، تواصل مفتوح"
            }
        }

        lang_advice = advice.get(self.lang, advice['en'])

        if child_age < 8:
            return lang_advice['under_8']
        elif child_age <= 12:
            return lang_advice['8_12']
        elif child_age <= 15:
            return lang_advice['13_15']
        else:
            return lang_advice['16_plus']

    def diagnose_issue(self, issue: str) -> dict:
        """Diagnose common issues and provide solutions."""
        issues = {
            'en': {
                'blocking_not_working': {
                    'cause': 'iptables permissions or blocking not enabled',
                    'solution': '1. Check if blocking is ON in sidebar\n2. Ensure iptables permissions: sudo visudo\n3. Restart service: sudo systemctl restart homonet',
                    'severity': 'high'
                },
                'slow_pi': {
                    'cause': 'Too many background processes or memory full',
                    'solution': '1. Increase scan interval to 5 min\n2. Disable charts in settings\n3. Run: free -m to check RAM',
                    'severity': 'medium'
                },
                'no_alerts': {
                    'cause': 'Email not configured or alerts disabled',
                    'solution': '1. Go to Settings → Email\n2. Configure SMTP settings\n3. Enable alerts in Settings → Notifications',
                    'severity': 'low'
                }
            },
            'ar': {
                'blocking_not_working': {
                    'cause': 'صلاحيات iptables أو عدم تفعيل الحظر',
                    'solution': '١. تأكد من تفعيل الحظر\n٢. تحقق من الصلاحيات\n٣. أعد تشغيل الخدمة',
                    'severity': 'high'
                },
                'slow_pi': {
                    'cause': 'عمليات كثيرة أو امتلاء الذاكرة',
                    'solution': '١. زد فترة الفحص لـ 5 دقائق\n٢. أوقف الرسوم البيانية\n٣. تحقق من الذاكرة: free -m',
                    'severity': 'medium'
                },
                'no_alerts': {
                    'cause': 'البريد غير مضبوط أو التنبيهات معطلة',
                    'solution': '١. الإعدادات ← البريد\n٢. اضبط إعدادات SMTP\n٣. فعّل التنبيهات',
                    'severity': 'low'
                }
            }
        }

        issue_lower = issue.lower()

        for key, solution in issues.get(self.lang, issues['en']).items():
            if key in issue_lower or any(w in issue_lower for w in key.split('_')):
                return solution

        # Default
        return {
            'cause': 'Unknown issue',
            'solution': 'Check logs or contact support: abdalfaqeeh@gmail.com',
            'severity': 'info'
        }
