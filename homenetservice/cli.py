"""
HomeNet — Command Line Interface
Full-featured CLI for network management.
"""

import sys
import json
import cmd
import platform
import time
import threading
from typing import Optional

from .config import ConfigManager
from .database import DatabaseManager, init_db
from .network_scanner import NetworkScanner
from .traffic_monitor import TrafficMonitor
from .firewall_rules import FirewallManager
from .speed_test import SpeedTester
from .alerts import AlertManager
from .auth import AuthManager
from .utils import format_bytes, check_internet_connection, get_system_info
from .translations import TranslationManager


class HomeNetCLI(cmd.Cmd):
    """HomeNet Command Line Interface."""

    intro = "🌐 HomeNet CLI — Parental Network Controller (UAE 🇦🇪)"
    prompt = "homenet> "

    def __init__(self):
        super().__init__()
        self.db = init_db()
        self.config = ConfigManager()
        self.scanner = NetworkScanner()
        self.monitor = TrafficMonitor()
        self.firewall = FirewallManager(self.config, self.db)
        self.speed_tester = SpeedTester(self.db)
        self.alerts = AlertManager(self.db, self.config)
        self.auth = AuthManager(self.db)
        self.translations = TranslationManager(self.config.get("general.language", "en"))
        self.authenticated = False
        self._ = self.translations.get

        print(f"\n{'='*60}")
        print(f"  🌐 HomeNet v1.0.0 — Proudly developed in UAE 🇦🇪")
        print(f"{'='*60}\n")
        print("Commands: help, scan, hosts, traffic, block, unblock,")
        print("          categories, timerules, speedtest, alerts,")
        print("          settings, system, status, quit\n")

    # ─── Authentication ──────────────────────────────────────────────────

    def do_login(self, arg):
        """Login to HomeNet: login [username] [password]"""
        parts = arg.strip().split()
        if len(parts) < 2:
            username = input("Username: ")
            password = input("Password: ")
        else:
            username, password = parts[0], parts[1]

        token = self.auth.login(username, password)
        if token:
            self.authenticated = True
            print(f"✅ Logged in as {username}")
        else:
            print(" Invalid username or password")

    # ── Network Scanning ────────────────────────────────────────────────

    def do_scan(self, arg):
        """Scan the network for connected devices."""
        print("🔍 Scanning network...")
        hosts = self.scanner.quick_scan()

        for host in hosts:
            self.db.add_or_update_host(
                ip=host["ip"],
                mac=host["mac"],
                hostname=host["hostname"],
                os_type=host["os_type"],
                hardware_info=host["hardware"],
            )
            self.alerts.notify_new_host(host["ip"], host["hostname"], host["mac"])

        print(f"✅ Scan complete! Found {len(hosts)} devices.\n")
        self.do_hosts("")

    def do_hosts(self, arg):
        """List all discovered hosts."""
        hosts = self.db.get_all_hosts()
        if not hosts:
            print("No hosts discovered. Run 'scan' first.")
            return

        print(f"\n{'IP Address':<18} {'MAC Address':<18} {'Hostname':<20} {'OS':<15} {'Status':<10}")
        print("-" * 80)
        for h in hosts:
            status = "🚫 Blocked" if h["is_blocked"] else "✅ Active"
            print(f"{h['ip_address']:<18} {h['mac_address'] or 'N/A':<18} "
                  f"{h['hostname'] or 'N/A':<20} {h['os_type'] or 'Unknown':<15} {status}")
        print()

    # ─── Traffic Monitoring ──────────────────────────────────────────────

    def do_traffic(self, arg):
        """Show traffic statistics."""
        summary = self.db.get_traffic_summary(hours=24)
        if not summary:
            print("No traffic data yet. Start monitoring with 'monitor start'.")
            return

        print(f"\n{'IP Address':<18} {'Hostname':<20} {'Sent':<12} {'Recv':<12} {'Total':<12}")
        print("-" * 75)
        for s in summary[:10]:
            print(f"{s['ip_address']:<18} {s['hostname'] or 'N/A':<20} "
                  f"{format_bytes(s['total_sent']):<12} "
                  f"{format_bytes(s['total_recv']):<12} "
                  f"{format_bytes(s['total_bytes']):<12}")
        print()

    def do_monitor(self, arg):
        """Start/stop traffic monitoring: monitor [start|stop|status]"""
        parts = arg.strip().split()
        if not parts:
            print("Usage: monitor [start|stop|status]")
            return

        action = parts[0].lower()
        if action == "start":
            self.monitor.start(callback=self._traffic_callback, interval=5)
            print("✅ Traffic monitoring started.")
        elif action == "stop":
            self.monitor.stop()
            print("⏹️ Traffic monitoring stopped.")
        elif action == "status":
            print(f"Monitoring: {'Running' if self.monitor.running else 'Stopped'}")
        else:
            print("Usage: monitor [start|stop|status]")

    def _traffic_callback(self, data):
        """Callback for traffic data."""
        for ip, stats in data.items():
            self.db.log_traffic(
                ip,
                bytes_sent=stats.get("bytes_sent", 0),
                bytes_recv=stats.get("bytes_recv", 0),
                packets_sent=stats.get("packets_sent", 0),
                packets_recv=stats.get("packets_recv", 0),
            )

    # ─── Blocking ───────────────────────────────────────────────────────

    def do_block(self, arg):
        """Block a host or category: block <ip|gaming|social|streaming>"""
        target = arg.strip().lower()

        if target in ["gaming", "social", "streaming"]:
            self.config.set(f"categories.{target}.enabled", True)
            self.firewall.block_category(target)
            print(f"✅ {target.capitalize()} blocking enabled.")

        elif target in ["all"]:
            for cat in ["gaming", "social_media", "streaming"]:
                self.config.set(f"categories.{cat}.enabled", True)
            self.firewall.apply_all_rules()
            print("✅ All categories blocked.")

        else:
            # Block specific host
            self.db.block_host(target, True)
            self.firewall.block_host(target)
            print(f"✅ Host {target} blocked.")

    def do_unblock(self, arg):
        """Unblock a host or category: unblock <ip|gaming|social|streaming|all>"""
        target = arg.strip().lower()

        if target in ["gaming", "social", "streaming"]:
            self.config.set(f"categories.{target}.enabled", False)
            print(f"✅ {target.capitalize()} blocking disabled.")

        elif target in ["all"]:
            for cat in ["gaming", "social_media", "streaming"]:
                self.config.set(f"categories.{cat}.enabled", False)
            print("✅ All categories unblocked.")

        else:
            self.db.block_host(target, False)
            self.firewall.unblock_host(target)
            print(f"✅ Host {target} unblocked.")

    def do_categories(self, arg):
        """Show blocking category status."""
        print(f"\n{'Category':<20} {'Status':<10} {'Domains':<10} {'Ports':<10}")
        print("-" * 50)
        for cat in ["gaming", "social_media", "streaming"]:
            cfg = self.config.get(f"categories.{cat}", {})
            status = "✅ ON" if cfg.get("enabled", False) else "❌ OFF"
            domains = len(cfg.get("domains", []))
            ports = len(cfg.get("ports", []))
            print(f"{cat:<20} {status:<10} {domains:<10} {ports:<10}")
        print()

    # ─── Time Rules ──────────────────────────────────────────────────────

    def do_timerules(self, arg):
        """Manage time-based blocking: timerules [show|enable|disable|set <start> <end>]"""
        parts = arg.strip().split()

        if not parts or parts[0] == "show":
            tb = self.config.get("time_blocking", {})
            print(f"\nTime-Based Blocking:")
            print(f"  Enabled: {'Yes' if tb.get('enabled') else 'No'}")
            print(f"  Block Start: {tb.get('block_start', 'N/A')}")
            print(f"  Block End: {tb.get('block_end', 'N/A')}")
            print(f"  Days: {', '.join(tb.get('block_days', []))}")
            print(f"  Currently Active: {'Yes' if self.config.is_time_to_block() else 'No'}")
            print()

        elif parts[0] == "enable":
            self.config.set("time_blocking.enabled", True)
            print("✅ Time blocking enabled.")

        elif parts[0] == "disable":
            self.config.set("time_blocking.enabled", False)
            print("⏹️ Time blocking disabled.")

        elif parts[0] == "set" and len(parts) >= 3:
            self.config.set("time_blocking.block_start", parts[1])
            self.config.set("time_blocking.block_end", parts[2])
            print(f"✅ Block time set: {parts[1]} to {parts[2]}")

        else:
            print("Usage: timerules [show|enable|disable|set <start> <end>]")

    # ─── Speed Test ─────────────────────────────────────────────────────

    def do_speedtest(self, arg):
        """Run internet speed test."""
        print("📡 Running speed test...")

        def progress(step, pct):
            print(f"  {step}: {pct}%")

        result = self.speed_tester.run_test(callback=progress)

        if result["success"]:
            print(f"\n✅ Speed Test Results:")
            print(f"  Download: {result['download_mbps']:.2f} Mbps")
            print(f"  Upload:   {result['upload_mbps']:.2f} Mbps")
            print(f"  Ping:     {result['ping_ms']:.2f} ms")
            print(f"  Server:   {result['server']}")
        else:
            print(f" Speed test failed: {result.get('error', 'Unknown error')}")
        print()

    def do_connection(self, arg):
        """Check internet connection status."""
        connected = check_internet_connection()
        if connected:
            print("✅ Internet connection: ACTIVE")
        else:
            print("❌ Internet connection: INACTIVE")

    # ─── Alerts ──────────────────────────────────────────────────────────

    def do_alerts(self, arg):
        """Show recent alerts."""
        parts = arg.strip().split()
        unread_only = parts and parts[0] == "unread"

        alerts = self.db.get_alerts(unread_only=unread_only)
        if not alerts:
            print("No alerts." if not unread_only else "No unread alerts.")
            return

        print(f"\n{'Time':<20} {'Type':<15} {'Severity':<10} {'Message'}")
        print("-" * 80)
        for a in alerts[:20]:
            print(f"{a['created_at']:<20} {a['alert_type']:<15} "
                  f"{a['severity']:<10} {a['message']}")
        print()

    def do_markread(self, arg):
        """Mark all alerts as read."""
        self.db.mark_alerts_read()
        print("✅ All alerts marked as read.")

    # ─── Settings ────────────────────────────────────────────────────────

    def do_settings(self, arg):
        """Show or modify settings."""
        parts = arg.strip().split()

        if not parts or parts[0] == "show":
            print("\n📋 General Settings:")
            for key, val in self.config.get("general", {}).items():
                if key != "admin_password_hash":
                    print(f"  {key}: {val}")

            print(f"\n🌐 Language: {self.config.get('general.language', 'en')}")
            print(f" Interface: {self.config.get('general.interface', 'eth0')}")
            print()

        elif parts[0] == "language" and len(parts) >= 2:
            lang = parts[1]
            if lang in ["en", "ar"]:
                self.config.set("general.language", lang)
                self.translations.set_language(lang)
                print(f"✅ Language set to {'English' if lang == 'en' else 'العربية'}")
            else:
                print("Usage: settings language [en|ar]")

        elif parts[0] == "interface" and len(parts) >= 2:
            self.config.set("general.interface", parts[1])
            print(f"✅ Interface set to {parts[1]}")

        elif parts[0] == "email" and len(parts) >= 2:
            self.config.set("general.recovery_email", parts[1])
            print(f"✅ Recovery email set to {parts[1]}")

        else:
            print("Usage: settings [show|language <en|ar>|interface <name>|email <address>]")

    # ─── System ──────────────────────────────────────────────────────────

    def do_system(self, arg):
        """Show system information."""
        parts = arg.strip().split()

        if not parts or parts[0] == "info":
            info = get_system_info()
            print(f"\n System Information:")
            print(f"  Platform:       {info['platform']} {info['platform_release']}")
            print(f"  Architecture:   {info['architecture']}")
            print(f"  Processor:      {info['processor']}")
            print(f"  CPU Cores:      {info['cpu_count']}")
            print(f"  RAM Total:      {format_bytes(info['ram_total'])}")
            print(f"  RAM Available:  {format_bytes(info['ram_available'])}")
            print(f"  Disk Usage:     {info['disk_usage']}%")
            print(f"  Hostname:       {info['hostname']}")
            print()

        elif parts[0] == "user":
            user = self.db.get_admin_user()
            print(f"\n👤 Admin User:")
            print(f"  Username: {user.get('username', 'N/A')}")
            print(f"  Email:    {user.get('email', 'Not set')}")
            print()

        elif parts[0] == "change" and len(parts) >= 2:
            if parts[1] == "password":
                current = input("Current password: ")
                new_pass = input("New password: ")
                confirm = input("Confirm new password: ")
                if new_pass != confirm:
                    print("❌ Passwords do not match!")
                    return
                if self.auth.change_password(
                    self.config.get("general.admin_username", "admin"),
                    current, new_pass
                ):
                    print("✅ Password changed successfully!")
                else:
                    print("❌ Failed to change password. Check current password.")
            elif parts[1] == "username":
                new_user = input("New username: ")
                if self.auth.update_profile(
                    self.config.get("general.admin_username", "admin"),
                    new_username=new_user
                ):
                    self.config.set("general.admin_username", new_user)
                    print(f"✅ Username changed to {new_user}")
                else:
                    print("❌ Failed to change username.")

        else:
            print("Usage: system [info|user|change password|change username]")

    # ─── Status ─────────────────────────────────────────────────────────

    def do_status(self, arg):
        """Show overall HomeNet status."""
        hosts = self.db.get_all_hosts()
        active = [h for h in hosts if not h["is_blocked"]]
        blocked = [h for h in hosts if h["is_blocked"]]

        print(f"\n🌐 HomeNet Status Dashboard")
        print(f"{'='*40}")
        print(f"  Total Hosts:    {len(hosts)}")
        print(f"  Active Hosts:   {len(active)}")
        print(f"  Blocked Hosts:  {len(blocked)}")
        print(f"  Time Blocking:  {'Active' if self.config.is_time_to_block() else 'Inactive'}")
        print(f"  Internet:       {'Connected' if check_internet_connection() else 'Disconnected'}")
        print(f"  Unread Alerts:  {self.db.get_unread_count()}")
        print(f"{'='*40}\n")

    # ── Firewall ────────────────────────────────────────────────────────

    def do_firewall(self, arg):
        """Manage firewall rules."""
        parts = arg.strip().split()

        if not parts or parts[0] == "status":
            rules = self.firewall.get_rules_status()
            for rule in rules:
                print(f"\n[{rule.get('type', 'rules')}]:")
                print(rule.get('output', 'No rules'))
            print()

        elif parts[0] == "apply":
            self.firewall.apply_all_rules()
            print("✅ All firewall rules applied.")

        elif parts[0] == "flush":
            self.firewall.flush_rules()
            print("✅ All firewall rules removed.")

        elif parts[0] == "addrule":
            # Add custom rule
            print("Custom rule types: host, port, domain")
            rule_type = input("Rule type: ")
            target = input("Target: ")
            self.db.add_block_rule(rule_type, target, enabled=True)
            self.firewall.apply_all_rules()
            print("✅ Rule added and applied.")

        else:
            print("Usage: firewall [status|apply|flush|addrule]")

    # ── Help & Quit ─────────────────────────────────────────────────────

    def do_help(self, arg):
        """Show available commands."""
        if arg:
            super().do_help(arg)
        else:
            print("""
🌐 HomeNet CLI Commands:
═══════════════════════════════════════════════════════════
  scan              Scan network for devices
  hosts             List all discovered hosts
  traffic           Show traffic statistics
  monitor start     Start traffic monitoring
  monitor stop      Stop traffic monitoring
  block <target>    Block host or category (gaming/social/streaming/all)
  unblock <target>  Unblock host or category
  categories        Show category blocking status
  timerules         Manage time-based blocking rules
  speedtest         Run internet speed test
  connection        Check internet connection
  alerts            Show recent alerts
  markread          Mark all alerts as read
  settings          Show/modify settings
  system            System information
  firewall          Manage firewall rules
  status            Show overall status
  login             Login to admin panel
  quit / exit       Exit HomeNet CLI
═══════════════════════════════════════════════════════════
  🇦🇪 Proudly developed in UAE
""")

    def do_quit(self, arg):
        """Exit HomeNet CLI."""
        print("\n👋 Goodbye! HomeNet shutting down.")
        self.monitor.stop()
        self.db.close()
        return True

    def do_exit(self, arg):
        """Exit HomeNet CLI."""
        return self.do_quit(arg)

    def emptyline(self):
        """Handle empty lines."""
        pass


def main():
    """Entry point for HomeNet CLI."""
    try:
        cli = HomeNetCLI()
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()