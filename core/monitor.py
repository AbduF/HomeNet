"""
HomeNet - Traffic Monitor Module
Real-time traffic monitoring and statistics
"""

import logging
import psutil
import time
from datetime import datetime, timedelta
from collections import defaultdict
import threading


class TrafficMonitor:
    """Monitor network traffic in real-time."""

    def __init__(self, db=None):
        self.db = db
        self.logger = logging.getLogger("HomeNet.TrafficMonitor")
        self.monitoring = False
        self.monitor_thread = None
        self.traffic_data = defaultdict(lambda: {'sent': 0, 'received': 0, 'packets_sent': 0, 'packets_received': 0})
        self.last_update = {}
        self.callbacks = []

    def add_callback(self, callback):
        """Add callback for traffic updates."""
        self.callbacks.append(callback)

    def remove_callback(self, callback):
        """Remove callback."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def get_interface_stats(self, interface=None):
        """Get network interface statistics."""
        try:
            stats = psutil.net_io_counters(pernic=True)

            if interface:
                if interface in stats:
                    return stats[interface]
                return None

            # Return all interfaces
            return stats
        except Exception as e:
            self.logger.error(f"Error getting interface stats: {e}")
            return None

    def get_total_traffic(self):
        """Get total traffic across all interfaces."""
        try:
            stats = psutil.net_io_counters()
            return {
                'bytes_sent': stats.bytes_sent,
                'bytes_received': stats.bytes_recv,
                'packets_sent': stats.packets_sent,
                'packets_received': stats.packets_recv,
                'errin': stats.errin,
                'errout': stats.errout,
                'dropin': stats.dropin,
                'dropout': stats.dropout
            }
        except Exception as e:
            self.logger.error(f"Error getting total traffic: {e}")
            return None

    def get_speed(self, interval=1):
        """Get current network speed."""
        try:
            stats1 = psutil.net_io_counters()
            time.sleep(interval)
            stats2 = psutil.net_io_counters()

            sent_speed = (stats2.bytes_sent - stats1.bytes_sent) / interval
            recv_speed = (stats2.bytes_recv - stats1.bytes_recv) / interval

            return {
                'download_speed': recv_speed,
                'upload_speed': sent_speed,
                'download_speed_mbps': recv_speed * 8 / 1000000,
                'upload_speed_mbps': sent_speed * 8 / 1000000
            }
        except Exception as e:
            self.logger.error(f"Error getting speed: {e}")
            return None

    def get_per_interface_speed(self, interval=1):
        """Get speed per interface."""
        try:
            stats1 = psutil.net_io_counters(pernic=True)
            time.sleep(interval)
            stats2 = psutil.net_io_counters(pernic=True)

            speeds = {}
            for iface in stats2:
                if iface == 'lo':
                    continue

                sent = stats2[iface].bytes_sent - stats1[iface].bytes_sent
                recv = stats2[iface].bytes_recv - stats1[iface].bytes_recv

                speeds[iface] = {
                    'upload_speed': sent / interval,
                    'download_speed': recv / interval,
                    'upload_mbps': sent * 8 / interval / 1000000,
                    'download_mbps': recv * 8 / interval / 1000000
                }

            return speeds
        except Exception as e:
            self.logger.error(f"Error getting per-interface speed: {e}")
            return None

    def start_monitoring(self, interval=5):
        """Start background traffic monitoring."""
        if self.monitoring:
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        self.logger.info("Traffic monitoring started")

    def stop_monitoring(self):
        """Stop background traffic monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        self.logger.info("Traffic monitoring stopped")

    def _monitor_loop(self, interval):
        """Background monitoring loop."""
        last_stats = psutil.net_io_counters()

        while self.monitoring:
            try:
                time.sleep(interval)
                current_stats = psutil.net_io_counters()

                # Calculate delta
                delta_sent = current_stats.bytes_sent - last_stats.bytes_sent
                delta_recv = current_stats.bytes_recv - last_stats.bytes_recv
                delta_packets_sent = current_stats.packets_sent - last_stats.packets_sent
                delta_packets_recv = current_stats.packets_recv - last_stats.packets_recv

                # Update data
                timestamp = datetime.now()
                self.traffic_data['total'] = {
                    'timestamp': timestamp,
                    'bytes_sent': delta_sent,
                    'bytes_received': delta_recv,
                    'packets_sent': delta_packets_sent,
                    'packets_received': delta_packets_recv,
                    'download_mbps': delta_recv * 8 / interval / 1000000,
                    'upload_mbps': delta_sent * 8 / interval / 1000000
                }

                last_stats = current_stats

                # Log to database
                if self.db:
                    self.db.log_traffic(
                        host_id=None,
                        bytes_sent=delta_sent,
                        bytes_received=delta_recv,
                        packets_sent=delta_packets_sent,
                        packets_received=delta_packets_recv
                    )

                # Notify callbacks
                for callback in self.callbacks:
                    try:
                        callback(self.traffic_data['total'])
                    except Exception as e:
                        self.logger.error(f"Callback error: {e}")

            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")

    def get_current_stats(self):
        """Get current monitoring statistics."""
        return self.traffic_data.get('total')

    def format_bytes(self, bytes_value):
        """Format bytes to human readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"

    def format_speed(self, bytes_per_second):
        """Format speed to human readable string."""
        mbps = bytes_per_second * 8 / 1000000
        if mbps < 1:
            kbps = bytes_per_second * 8 / 1000
            return f"{kbps:.2f} Kbps"
        return f"{mbps:.2f} Mbps"
