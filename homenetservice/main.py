"""
HomeNet — Main Entry Point
Proudly developed in UAE 🇦🇪
"""

import sys
import os
import signal
import threading
import time
import argparse

from .config import ConfigManager
from .database import DatabaseManager, init_db
from .network_scanner import NetworkScanner
from .traffic_monitor import TrafficMonitor
from .firewall_rules import FirewallManager
from .speed_test import SpeedTester
from .alerts import AlertManager
from .auth import AuthManager


class HomeNetService:
    """Main HomeNet background service."""

    def __init__(self):
        self.db = init_db()
        self.config = ConfigManager()
        self.scanner = NetworkScanner(self.config.get("general.interface", "eth0"))
        self.monitor = TrafficMonitor(self.config.get("general.interface", "eth0"))
        self.firewall = FirewallManager(self.config, self.db)
        self.speed_tester = SpeedTester(self.db)
        self.alerts = AlertManager(self.db, self.config)
        self.auth = AuthManager(self.db)

        self.running = False
        self.last_scan_time = 0
        self.last_traffic_check = 0

    def start(self):
        """Start the HomeNet service."""
        self.running = True
        print("🌐 HomeNet Service starting...")
        print("🇪 Proudly developed in UAE")

        # Initialize firewall
        self.firewall.init_chains()
        self.firewall.apply_all_rules()

        # Start traffic monitoring
        self.monitor.start(callback=self._on_traffic_data, interval=10)

        # Start background threads
        threading.Thread(target=self._periodic_scan, daemon=True).start()
        threading.Thread(target=self._time_block_checker, daemon=True).start()
        threading.Thread(target=self._traffic_threshold_checker, daemon=True).start()

        print("✅ HomeNet Service running!")
        print(f"   CLI: homenetservice-cli")
        print(f"   GUI: homenetservice-gui")

        # Keep alive
        while self.running:
            time.sleep(1)

    def stop(self):
        """Stop the HomeNet service."""
        self.running = False
        self.monitor.stop()
        self.db.close()
        print("⏹️ HomeNet Service stopped.")

    def _on_traffic_data(self, data):
        """Handle traffic monitoring data."""
        for ip, stats in data.items():
            self.db.log_traffic(
                ip,
                bytes_sent=stats.get("bytes_sent", 0),
                bytes_recv=stats.get("bytes_recv", 0),
                packets_sent=stats.get("packets_sent", 0),
                packets_recv=stats.get("packets_recv", 0),
            )

    def _periodic_scan(self):
        """Periodically scan for new hosts."""
        while self.running:
            try:
                hosts = self.scanner.quick_scan()
                for host in hosts:
                    existing = self.db.get_host_by_ip(host["ip"])
                    if not existing:
                        self.db.add_or_update_host(
                            ip=host["ip"],
                            mac=host["mac"],
                            hostname=host["hostname"],
                            os_type=host["os_type"],
                            hardware_info=host["hardware"],
                        )
                        self.alerts.notify_new_host(
                            host["ip"], host["hostname"], host["mac"]
                        )
                    else:
                        # Update last seen
                        self.db.add_or_update_host(
                            ip=host["ip"],
                            mac=host["mac"],
                            hostname=host["hostname"],
                            os_type=host["os_type"],
                            hardware_info=host["hardware"],
                        )
            except Exception as e:
                print(f"Scan error: {e}")

            time.sleep(60)  # Scan every 60 seconds

    def _time_block_checker(self):
        """Check and apply time-based blocking."""
        last_state = None
        while self.running:
            try:
                is_blocking = self.config.is_time_to_block()
                if is_blocking != last_state:
                    if is_blocking:
                        self.alerts.notify_blocking_activated()
                        # Apply blocks
                        hosts = self.db.get_all_hosts()
                        for host in hosts:
                            ip = host["ip_address"]
                            if not self.config.is_host_whitelisted(ip) and not host.get("is_whitelisted"):
                                self.firewall.block_host(ip)
                    else:
                        self.alerts.notify_blocking_deactivated()
                        # Remove blocks
                        hosts = self.db.get_all_hosts()
                        for host in hosts:
                            ip = host["ip_address"]
                            self.firewall.unblock_host(ip)
                    last_state = is_blocking
            except Exception as e:
                print(f"Time block error: {e}")

            time.sleep(30)  # Check every 30 seconds

    def _traffic_threshold_checker(self):
        """Check for high traffic alerts."""
        while self.running:
            try:
                summary = self.db.get_traffic_summary(hours=1)
                threshold = self.config.get("alerts.high_traffic_threshold_mb", 500) * 1_048_576

                for s in summary:
                    if s["total_bytes"] > threshold:
                        self.alerts.notify_high_traffic(s["ip_address"], s["total_bytes"])
            except Exception as e:
                print(f"Traffic threshold error: {e}")

            time.sleep(300)  # Check every 5 minutes


def signal_handler(signum, frame):
    """Handle termination signals."""
    print("\n👋 Shutting down HomeNet...")
    sys.exit(0)


def main():
    """Main entry point."""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    parser = argparse.ArgumentParser(description="HomeNet - Parental Network Controller")
    parser.add_argument("--mode", choices=["service", "cli", "gui"], default="service",
                        help="Run mode: service (default), cli, or gui")

    args = parser.parse_args()

    if args.mode == "cli":
        from .cli import main as cli_main
        cli_main()
    elif args.mode == "gui":
        from .gui import main as gui_main
        gui_main()
    else:
        service = HomeNetService()
        try:
            service.start()
        except KeyboardInterrupt:
            service.stop()


if __name__ == "__main__":
    main()