"""
HomeNet - Traffic View
Traffic monitoring and statistics
"""

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import logging
from datetime import datetime, timedelta


class TrafficView(ctk.CTkFrame):
    """Traffic monitoring view."""

    def __init__(self, parent, db, config, scanner, monitor, blocker, lang='en'):
        super().__init__(parent, fg_color="#1A1A2E")
        self.parent = parent
        self.db = db
        self.config = config
        self.scanner = scanner
        self.monitor = monitor
        self.blocker = blocker
        self.lang = lang
        self.logger = logging.getLogger("HomeNet.Traffic")

        self.translations = self.get_translations()
        self.setup_ui()
        self.refresh_data()

    def get_translations(self):
        """Get translations."""
        translations = {
            'en': {
                'title': 'Traffic Monitor',
                'realtime': 'Real-Time',
                'download': 'Download',
                'upload': 'Upload',
                'total': 'Total',
                'history': 'History',
                'top_consumers': 'Top Consumers',
                'speed_test': 'Speed Test',
                'download_speed': 'Download Speed',
                'upload_speed': 'Upload Speed',
                'latency': 'Latency',
                'run_test': 'Run Test',
                'today': 'Today',
                'this_week': 'This Week',
                'this_month': 'This Month',
                'mbps': 'Mbps',
                'ms': 'ms',
                'host': 'Host',
                'volume': 'Volume',
                'refresh': 'Refresh'
            },
            'ar': {
                'title': 'مراقبة البيانات',
                'realtime': 'الوقت الفعلي',
                'download': 'تحميل',
                'upload': 'رفع',
                'total': 'الإجمالي',
                'history': 'السجل',
                'top_consumers': 'أكبر مستهلكين',
                'speed_test': 'اختبار السرعة',
                'download_speed': 'سرعة التحميل',
                'upload_speed': 'سرعة الرفع',
                'latency': 'زمن الاستجابة',
                'run_test': 'تشغيل الاختبار',
                'today': 'اليوم',
                'this_week': 'هذا الأسبوع',
                'this_month': 'هذا الشهر',
                'mbps': 'ميجابابت/ث',
                'ms': 'مللي ثانية',
                'host': 'الجهاز',
                'volume': 'الحجم',
                'refresh': 'تحديث'
            }
        }
        return translations.get(self.lang, translations['en'])

    def setup_ui(self):
        """Setup traffic view UI."""
        # Title
        title = ctk.CTkLabel(
            self,
            text=self.translations['title'],
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFFFFF"
        )
        title.pack(anchor="w", padx=24, pady=(20, 10))

        # Main content grid
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=10)

        content.grid_columnconfigure(0, weight=2)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        # Left panel - Charts
        left_panel = ctk.CTkFrame(content, fg_color="#16213E", corner_radius=12)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Speed test card
        speed_card = ctk.CTkFrame(left_panel, fg_color="#0F3460", corner_radius=8)
        speed_card.pack(fill="x", padx=16, pady=16)

        speed_title = ctk.CTkLabel(
            speed_card,
            text=f"📡 {self.translations['speed_test']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#FFFFFF"
        )
        speed_title.pack(anchor="w", padx=16, pady=(12, 8))

        # Speed results
        speed_results = ctk.CTkFrame(speed_card, fg_color="transparent")
        speed_results.pack(fill="x", padx=16, pady=8)

        self.download_speed_label = ctk.CTkLabel(
            speed_results,
            text=f"↓ {self.translations['download']}: -- Mbps",
            font=ctk.CTkFont(size=14),
            text_color="#43A047"
        )
        self.download_speed_label.pack(anchor="w", pady=4)

        self.upload_speed_label = ctk.CTkLabel(
            speed_results,
            text=f"↑ {self.translations['upload']}: -- Mbps",
            font=ctk.CTkFont(size=14),
            text_color="#FF7043"
        )
        self.upload_speed_label.pack(anchor="w", pady=4)

        self.latency_label = ctk.CTkLabel(
            speed_results,
            text=f"⏱ {self.translations['latency']}: -- {self.translations['ms']}",
            font=ctk.CTkFont(size=14),
            text_color="#1E88E5"
        )
        self.latency_label.pack(anchor="w", pady=4)

        # Run test button
        test_btn = ctk.CTkButton(
            speed_card,
            text=f"▶ {self.translations['run_test']}",
            width=140,
            height=36,
            corner_radius=8,
            fg_color="#1E88E5",
            command=self.run_speedtest
        )
        test_btn.pack(pady=(8, 12))

        # Real-time chart
        chart_card = ctk.CTkFrame(left_panel, fg_color="#0F3460", corner_radius=8)
        chart_card.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        chart_title = ctk.CTkLabel(
            chart_card,
            text=f"📊 {self.translations['realtime']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#FFFFFF"
        )
        chart_title.pack(anchor="w", padx=16, pady=(12, 8))

        # Matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(8, 3), facecolor='#0F3460')
        self.ax.set_facecolor('#0F3460')
        self.fig.patch.set_facecolor('#0F3460')
        self.ax.tick_params(colors='white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.title.set_color('white')

        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_card)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

        # Initialize chart data
        self.time_data = []
        self.download_data = []
        self.upload_data = []

        # Right panel
        right_panel = ctk.CTkFrame(content, fg_color="#16213E", corner_radius=12)
        right_panel.grid(row=0, column=1, sticky="nsew")

        # Total stats
        total_card = ctk.CTkFrame(right_panel, fg_color="#0F3460", corner_radius=8)
        total_card.pack(fill="x", padx=16, pady=16)

        total_title = ctk.CTkLabel(
            total_card,
            text=f"📈 {self.translations['total']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#FFFFFF"
        )
        total_title.pack(anchor="w", padx=16, pady=(12, 8))

        self.total_download_label = ctk.CTkLabel(
            total_card,
            text=f"↓ {self.translations['download']}: 0 MB",
            font=ctk.CTkFont(size=14),
            text_color="#43A047"
        )
        self.total_download_label.pack(anchor="w", padx=16, pady=4)

        self.total_upload_label = ctk.CTkLabel(
            total_card,
            text=f"↑ {self.translations['upload']}: 0 MB",
            font=ctk.CTkFont(size=14),
            text_color="#FF7043"
        )
        self.total_upload_label.pack(anchor="w", padx=16, pady=4)

        # Top consumers
        consumers_card = ctk.CTkFrame(right_panel, fg_color="#0F3460", corner_radius=8)
        consumers_card.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        consumers_title = ctk.CTkLabel(
            consumers_card,
            text=f"🏆 {self.translations['top_consumers']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#FFFFFF"
        )
        consumers_title.pack(anchor="w", padx=16, pady=(12, 8))

        # Top consumers list
        self.consumers_list = ctk.CTkScrollableFrame(
            consumers_card,
            fg_color="transparent",
            height=200
        )
        self.consumers_list.pack(fill="both", expand=True, padx=8, pady=8)

    def refresh_data(self):
        """Refresh traffic data."""
        try:
            if self.monitor:
                speed = self.monitor.get_speed(interval=1)
                if speed:
                    # Update labels
                    down_mbps = speed['download_speed_mbps']
                    up_mbps = speed['upload_speed_mbps']

                    self.download_speed_label.configure(
                        text=f"↓ {self.translations['download']}: {down_mbps:.1f} {self.translations['mbps']}"
                    )
                    self.upload_speed_label.configure(
                        text=f"↑ {self.translations['upload']}: {up_mbps:.1f} {self.translations['mbps']}"
                    )

                    # Update chart
                    self.time_data.append(datetime.now().strftime('%H:%M:%S'))
                    self.download_data.append(down_mbps)
                    self.upload_data.append(up_mbps)

                    # Keep last 20 points
                    if len(self.time_data) > 20:
                        self.time_data = self.time_data[-20:]
                        self.download_data = self.download_data[-20:]
                        self.upload_data = self.upload_data[-20:]

                    self.update_chart()

            # Update total stats
            stats = self.monitor.get_total_traffic() if self.monitor else None
            if stats:
                total_down = self.monitor.format_bytes(stats.get('bytes_received', 0))
                total_up = self.monitor.format_bytes(stats.get('bytes_sent', 0))
                self.total_download_label.configure(text=f"↓ {self.translations['download']}: {total_down}")
                self.total_upload_label.configure(text=f"↑ {self.translations['upload']}: {total_up}")

            # Update top consumers
            self.update_top_consumers()

        except Exception as e:
            self.logger.error(f"Error refreshing traffic data: {e}")

        # Schedule next refresh
        self.after(2000, self.refresh_data)

    def update_chart(self):
        """Update traffic chart."""
        try:
            self.ax.clear()

            if self.time_data:
                x = range(len(self.time_data))

                self.ax.plot(x, self.download_data, 'g-', label=self.translations['download'], linewidth=2)
                self.ax.plot(x, self.upload_data, 'r-', label=self.translations['upload'], linewidth=2)

                self.ax.set_xticks(x[::5] if len(x) > 5 else x)
                self.ax.set_xticklabels([self.time_data[i] for i in range(0, len(self.time_data), 5)] if len(self.time_data) > 5 else self.time_data, rotation=45)

                self.ax.set_ylabel('Mbps')
                self.ax.legend(loc='upper left', facecolor='#0F3460', labelcolor='white')
                self.ax.grid(True, alpha=0.3, color='white')

            self.canvas.draw()
        except Exception as e:
            self.logger.error(f"Chart update error: {e}")

    def update_top_consumers(self):
        """Update top consumers list."""
        try:
            # Clear existing
            for widget in self.consumers_list.winfo_children():
                widget.destroy()

            # Get top consumers
            consumers = self.db.get_top_consumers(limit=5)

            for i, consumer in enumerate(consumers):
                item = ctk.CTkFrame(self.consumers_list, fg_color="#16213E", corner_radius=6)
                item.pack(fill="x", pady=4)

                rank = ctk.CTkLabel(
                    item,
                    text=f"#{i+1}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#FF7043",
                    width=30
                )
                rank.pack(side="left", padx=8)

                name = ctk.CTkLabel(
                    item,
                    text=consumer.get('hostname', 'Unknown')[:20],
                    font=ctk.CTkFont(size=12),
                    text_color="#FFFFFF"
                )
                name.pack(side="left", padx=4)

                volume = consumer.get('total_bytes', 0)
                volume_str = self.monitor.format_bytes(volume) if self.monitor else f"{volume} B"
                volume_label = ctk.CTkLabel(
                    item,
                    text=volume_str,
                    font=ctk.CTkFont(size=11),
                    text_color="#B0B0B0"
                )
                volume_label.pack(side="right", padx=8)

        except Exception as e:
            self.logger.error(f"Error updating consumers: {e}")

    def run_speedtest(self):
        """Run internet speed test."""
        try:
            from core.speedtest import SpeedTest

            result = SpeedTest().run_test()
            if result:
                self.download_speed_label.configure(
                    text=f"↓ {self.translations['download']}: {result['download_mbps']:.1f} {self.translations['mbps']}"
                )
                self.upload_speed_label.configure(
                    text=f"↑ {self.translations['upload']}: {result['upload_mbps']:.1f} {self.translations['mbps']}"
                )
                self.latency_label.configure(
                    text=f"⏱ {self.translations['latency']}: {result['ping_ms']:.0f} {self.translations['ms']}"
                )

        except Exception as e:
            self.logger.error(f"Speed test error: {e}")
