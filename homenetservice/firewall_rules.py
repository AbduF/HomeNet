"""
HomeNet — Firewall Rules Manager
Manages iptables/nftables rules for blocking hosts, ports, and domains.
"""

import subprocess
import platform
import os
import time
import socket
from typing import List, Dict, Optional
from .config import ConfigManager
from .database import DatabaseManager


class FirewallManager:
    """Manages firewall rules for blocking and filtering."""

    CHAIN_NAME = "HOMENET_BLOCK"
    DNS_CHAIN = "HOMENET_DNS"

    def __init__(self, config: ConfigManager, db: DatabaseManager,
                 interface: str = "eth0"):
        self.config = config
        self.db = db
        self.interface = interface
        self.use_nftables = self._check_nftables()
        self.rules_applied: Dict[str, bool] = {}

    def _check_nftables(self) -> bool:
        """Check if nftables is available."""
        try:
            result = subprocess.run(
                ["which", "nft"], capture_output=True, text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def _run_cmd(self, cmd: List[str]) -> bool:
        """Run a shell command and return success status."""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception:
            return False

    def init_chains(self) -> bool:
        """Initialize firewall chains."""
        if self.use_nftables:
            return self._init_nftables()
        return self._init_iptables()

    def _init_iptables(self) -> bool:
        """Initialize iptables chains."""
        commands = [
            ["iptables", "-N", self.CHAIN_NAME],
            ["iptables", "-N", self.DNS_CHAIN],
            ["iptables", "-I", "FORWARD", "-j", self.CHAIN_NAME],
            ["iptables", "-I", "FORWARD", "-p", "udp", "--dport", "53",
             "-j", self.DNS_CHAIN],
            ["iptables", "-I", "FORWARD", "-p", "tcp", "--dport", "53",
             "-j", self.DNS_CHAIN],
        ]
        for cmd in commands:
            self._run_cmd(cmd)
        return True

    def _init_nftables(self) -> bool:
        """Initialize nftables chains."""
        table = "inet homenetservice"
        commands = [
            ["nft", "add", "table", table],
            ["nft", "add", "chain", table, "forward",
             "{ type filter hook forward priority 0; }"],
            ["nft", "add", "chain", table, self.CHAIN_NAME],
            ["nft", "add", "chain", table, self.DNS_CHAIN],
            ["nft", "add", "rule", table, "forward", "jump", self.CHAIN_NAME],
            ["nft", "add", "rule", table, "forward",
             "meta", "l4proto", "{ tcp, udp }", "th", "dport", "53",
             "jump", self.DNS_CHAIN],
        ]
        for cmd in commands:
            self._run_cmd(cmd)
        return True

    def block_host(self, ip: str) -> bool:
        """Block all traffic to/from a specific host."""
        if self.use_nftables:
            return self._run_cmd([
                "nft", "add", "rule", "inet homenetservice", self.CHAIN_NAME,
                "ip", "saddr", ip, "drop"
            ]) and self._run_cmd([
                "nft", "add", "rule", "inet homenetservice", self.CHAIN_NAME,
                "ip", "daddr", ip, "drop"
            ])
        else:
            return self._run_cmd([
                "iptables", "-A", self.CHAIN_NAME, "-s", ip, "-j", "DROP"
            ]) and self._run_cmd([
                "iptables", "-A", self.CHAIN_NAME, "-d", ip, "-j", "DROP"
            ])

    def unblock_host(self, ip: str) -> bool:
        """Remove block rules for a specific host."""
        if self.use_nftables:
            # Delete matching rules
            self._run_cmd([
                "nft", "delete", "rule", "inet homenetservice", self.CHAIN_NAME,
                "handle", "$(nft -a list chain inet homenetservice HOMENET_BLOCK | grep ip | grep saddr | grep {} | awk '{{print $NF}}')".format(ip)
            ])
        else:
            self._run_cmd([
                "iptables", "-D", self.CHAIN_NAME, "-s", ip, "-j", "DROP"
            ])
            self._run_cmd([
                "iptables", "-D", self.CHAIN_NAME, "-d", ip, "-j", "DROP"
            ])
        return True

    def block_port(self, port: int, protocol: str = "tcp") -> bool:
        """Block traffic on a specific port."""
        if self.use_nftables:
            return self._run_cmd([
                "nft", "add", "rule", "inet homenetservice", self.CHAIN_NAME,
                "meta", "l4proto", protocol, "th", "dport", str(port), "drop"
            ])
        else:
            return self._run_cmd([
                "iptables", "-A", self.CHAIN_NAME, "-p", protocol,
                "--dport", str(port), "-j", "DROP"
            ])

    def block_domain(self, domain: str) -> bool:
        """Block a domain by adding DNS redirect rule."""
        # Add to DNS chain to redirect/block DNS queries for this domain
        if self.use_nftables:
            return self._run_cmd([
                "nft", "add", "rule", "inet homenetservice", self.DNS_CHAIN,
                "meta", "l4proto", "{ tcp, udp }", "th", "dport", "53",
                "payload", "16-15", "string", domain, "drop"
            ])
        else:
            # Use string match for domain blocking
            return self._run_cmd([
                "iptables", "-A", self.DNS_CHAIN, "-p", "udp", "--dport", "53",
                "-m", "string", "--string", domain, "--algo", "bm", "-j", "DROP"
            ])

    def block_category(self, category: str) -> bool:
        """Block all domains/ports for a category."""
        cat_config = self.config.get(f"categories.{category}", {})
        if not cat_config.get("enabled", False):
            return True

        # Block ports
        for port in cat_config.get("ports", []):
            self.block_port(port)

        # Block domains
        for domain in cat_config.get("domains", []):
            clean_domain = domain.lstrip("*.").rstrip(".")
            self.block_domain(clean_domain)

        return True

    def apply_time_blocking(self):
        """Apply or remove time-based blocking rules."""
        if self.config.is_time_to_block():
            # Get all non-whitelisted hosts and block them
            hosts = self.db.get_all_hosts()
            for host in hosts:
                ip = host["ip_address"]
                if not self.config.is_host_whitelisted(ip) and not host.get("is_whitelisted"):
                    self.block_host(ip)
        else:
            # Remove time-based blocks
            hosts = self.db.get_all_hosts()
            for host in hosts:
                ip = host["ip_address"]
                self.unblock_host(ip)

    def apply_all_rules(self) -> bool:
        """Apply all configured blocking rules."""
        self.init_chains()

        # Apply category blocks
        for category in ["gaming", "social_media", "streaming"]:
            self.block_category(category)

        # Apply host blocks
        hosts = self.db.get_all_hosts()
        for host in hosts:
            if host.get("is_blocked"):
                self.block_host(host["ip_address"])

        # Apply custom rules
        rules = self.db.get_block_rules()
        for rule in rules:
            if rule["enabled"]:
                if rule["rule_type"] == "host":
                    self.block_host(rule["target"])
                elif rule["rule_type"] == "port":
                    self.block_port(int(rule["target"]))
                elif rule["rule_type"] == "domain":
                    self.block_domain(rule["target"])

        return True

    def flush_rules(self) -> bool:
        """Remove all HomeNet firewall rules."""
        if self.use_nftables:
            return self._run_cmd([
                "nft", "delete", "table", "inet homenetservice"
            ])
        else:
            self._run_cmd(["iptables", "-F", self.CHAIN_NAME])
            self._run_cmd(["iptables", "-F", self.DNS_CHAIN])
            self._run_cmd(["iptables", "-D", "FORWARD", "-j", self.CHAIN_NAME])
            self._run_cmd(["iptables", "-D", "FORWARD", "-j", self.DNS_CHAIN])
            self._run_cmd(["iptables", "-X", self.CHAIN_NAME])
            self._run_cmd(["iptables", "-X", self.DNS_CHAIN])
            return True

    def get_rules_status(self) -> List[Dict]:
        """Get current firewall rules status."""
        rules = []
        try:
            if self.use_nftables:
                result = subprocess.run(
                    ["nft", "list", "table", "inet homenetservice"],
                    capture_output=True, text=True, timeout=5
                )
                rules.append({"type": "nftables", "output": result.stdout})
            else:
                result = subprocess.run(
                    ["iptables", "-L", self.CHAIN_NAME, "-n", "-v"],
                    capture_output=True, text=True, timeout=5
                )
                rules.append({"type": "iptables", "chain": self.CHAIN_NAME,
                              "output": result.stdout})
                result = subprocess.run(
                    ["iptables", "-L", self.DNS_CHAIN, "-n", "-v"],
                    capture_output=True, text=True, timeout=5
                )
                rules.append({"type": "iptables", "chain": self.DNS_CHAIN,
                              "output": result.stdout})
        except Exception as e:
            rules.append({"type": "error", "output": str(e)})

        return rules