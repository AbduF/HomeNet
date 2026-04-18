import subprocess
import platform

class FirewallManager:
    def __init__(self):
        self.is_linux = platform.system() == "Linux"

    def block_ip(self, ip):
        if self.is_linux:
            subprocess.run(["sudo", "iptables", "-A", "FORWARD", "-s", ip, "-j", "DROP"], check=True)
            subprocess.run(["sudo", "iptables", "-A", "OUTPUT", "-d", ip, "-j", "DROP"], check=True)

    def unblock_ip(self, ip):
        if self.is_linux:
            subprocess.run(["sudo", "iptables", "-D", "FORWARD", "-s", ip, "-j", "DROP"], check=True)
            subprocess.run(["sudo", "iptables", "-D", "OUTPUT", "-d", ip, "-j", "DROP"], check=True)

    def apply_time_rule(self, start_h, end_h):
        # Simplified cron/iptables time match example
        cmd = f'sudo iptables -A FORWARD -m time --timestart {start_h} --timestop {end_h} --kiddst {self._kids_net()} -j DROP'
        # In production, use nftables or cron for persistence
        pass

    def _kids_net(self):
        return "192.168.1.0/24"  # Adjust to your LAN