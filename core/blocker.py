"""
HomeNet - Traffic Blocker Module
iptables-based traffic blocking
"""

import logging
import subprocess
import os
from datetime import datetime, time


class TrafficBlocker:
    """Traffic blocker using iptables on Linux."""

    def __init__(self, db=None):
        self.db = db
        self.logger = logging.getLogger("HomeNet.Blocker")
        self.blocking_active = False
        self.blocked_ips = set()
        self.is_linux = os.name == 'posix'

    def _run_command(self, cmd, sudo=False):
        """Run shell command."""
        try:
            if sudo and os.geteuid() != 0:
                cmd = ['sudo'] + cmd

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                self.logger.warning(f"Command failed: {result.stderr}")

            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            self.logger.error(f"Command error: {e}")
            return False, "", str(e)

    def is_admin(self):
        """Check if running with admin privileges."""
        return os.geteuid() == 0

    def create_chain(self, chain_name="HOMENET"):
        """Create custom iptables chain."""
        if not self.is_linux:
            self.logger.warning("Only supported on Linux")
            return False

        success, _, _ = self._run_command(['iptables', '-L', chain_name, '-n'])

        if not success:
            # Create chain
            self._run_command(['iptables', '-N', chain_name], sudo=True)
            # Add to INPUT chain
            self._run_command(['iptables', '-A', 'INPUT', '-j', chain_name], sudo=True)
            # Add to OUTPUT chain
            self._run_command(['iptables', '-A', 'OUTPUT', '-j', chain_name], sudo=True)
            self.logger.info(f"Created chain: {chain_name}")

        return True

    def block_ip(self, ip_address):
        """Block IP address."""
        if not self.is_linux:
            self.logger.warning("IP blocking only supported on Linux")
            return False

        # Add to HOMENET chain
        success, _, _ = self._run_command(
            ['iptables', '-A', 'HOMENET', '-d', ip_address, '-j', 'DROP'],
            sudo=True
        )

        if success:
            self.blocked_ips.add(ip_address)
            self.logger.info(f"Blocked IP: {ip_address}")

        return success

    def unblock_ip(self, ip_address):
        """Unblock IP address."""
        if not self.is_linux:
            return False

        success, _, _ = self._run_command(
            ['iptables', '-D', 'HOMENET', '-d', ip_address, '-j', 'DROP'],
            sudo=True
        )

        if success:
            self.blocked_ips.discard(ip_address)
            self.logger.info(f"Unblocked IP: {ip_address}")

        return success

    def block_mac(self, mac_address):
        """Block MAC address (drop at input)."""
        if not self.is_linux:
            return False

        success, _, _ = self._run_command(
            ['iptables', '-A', 'HOMENET', '-m', 'mac', '--mac-source', mac_address, '-j', 'DROP'],
            sudo=True
        )

        return success

    def block_domain(self, domain):
        """Block domain by creating iptables rule for resolved IPs."""
        if not self.is_linux:
            return False

        try:
            import socket
            ip = socket.gethostbyname(domain)

            success, _, _ = self._run_command(
                ['iptables', '-A', 'HOMENET', '-d', ip, '-j', 'DROP'],
                sudo=True
            )

            if success:
                self.blocked_ips.add(f"{domain} ({ip})")
                self.logger.info(f"Blocked domain: {domain} ({ip})")

            return success
        except Exception as e:
            self.logger.error(f"Error blocking domain {domain}: {e}")
            return False

    def block_port(self, port, protocol='tcp'):
        """Block port for all traffic."""
        if not self.is_linux:
            return False

        success, _, _ = self._run_command(
            ['iptables', '-A', 'HOMENET', '-p', protocol, '--dport', str(port), '-j', 'DROP'],
            sudo=True
        )

        if success:
            self.logger.info(f"Blocked port {port}/{protocol}")

        return success

    def enable_blocking(self):
        """Enable all blocking rules."""
        if not self.is_linux:
            self.logger.warning("Blocking only supported on Linux")
            return False

        if not self.is_admin():
            self.logger.error("Admin privileges required for blocking")
            return False

        self.create_chain()
        self.blocking_active = True
        self.logger.info("Blocking enabled")
        return True

    def disable_blocking(self):
        """Disable all blocking rules."""
        if not self.is_linux:
            return False

        # Flush HOMENET chain
        self._run_command(['iptables', '-F', 'HOMENET'], sudo=True)
        self.blocked_ips.clear()
        self.blocking_active = False
        self.logger.info("Blocking disabled")
        return True

    def get_blocked_list(self):
        """Get list of blocked IPs/domains."""
        return list(self.blocked_ips)

    def is_blocking_active(self):
        """Check if blocking is currently active."""
        return self.blocking_active

    def check_schedule(self, schedules):
        """Check if current time matches any blocking schedule."""
        now = datetime.now()
        current_time = now.time()
        current_day = now.weekday()

        for schedule in schedules:
            if not schedule.get('enabled', True):
                continue

            # Parse times
            try:
                start_time = datetime.strptime(schedule['start_time'], '%H:%M').time()
                end_time = datetime.strptime(schedule['end_time'], '%H:%M').time()

                # Check days
                days = schedule.get('days', [0, 1, 2, 3, 4, 5, 6])
                if isinstance(days, str):
                    import json
                    days = json.loads(days)

                if current_day not in days:
                    continue

                # Check if current time is in range
                if start_time <= current_time <= end_time:
                    return True, schedule

            except Exception as e:
                self.logger.error(f"Error checking schedule: {e}")

        return False, None

    def apply_scheduled_blocks(self, hosts, schedules):
        """Apply blocking based on schedules."""
        is_blocking, schedule = self.check_schedule(schedules)

        if is_blocking and not self.blocking_active:
            self.enable_blocking()

            # Block all non-trusted hosts
            for host in hosts:
                if not host.get('trusted') and not host.get('blocked'):
                    ip = host.get('ip_address')
                    if ip:
                        self.block_ip(ip)

            self.logger.info(f"Applied blocking schedule: {schedule['name']}")

        elif not is_blocking and self.blocking_active:
            self.disable_blocking()
            self.logger.info("Disabled scheduled blocking")

        return is_blocking

    def add_custom_rule(self, rule_string):
        """Add custom iptables rule."""
        if not self.is_linux:
            return False

        cmd = ['iptables', '-A', 'HOMENET'] + rule_string.split()
        success, _, _ = self._run_command(cmd, sudo=True)

        return success
