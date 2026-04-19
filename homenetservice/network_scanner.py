"""
HomeNet — Network Scanner
Discovers hosts on the local network using ARP and Nmap.
"""

import socket
import struct
import subprocess
import platform
import threading
import time
from typing import List, Dict, Optional, Callable
from scapy.all import ARP, Ether, srp, conf
from .utils import get_mac_manufacturer, get_os_fingerprint, get_mac_from_arp


class NetworkScanner:
    """Scans the local network for connected devices."""

    def __init__(self, interface: str = "eth0"):
        self.interface = interface
        self.subnet = self._get_subnet()
        self.hosts: List[Dict] = []
        self.scan_callback: Optional[Callable] = None

    def _get_subnet(self) -> str:
        """Determine the local subnet."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            # Convert to /24 subnet
            parts = local_ip.split(".")
            return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
        except Exception:
            return "192.168.1.0/24"

    def scan_arp(self, progress_callback: Callable = None) -> List[Dict]:
        """Scan network using ARP requests (fast, reliable for local hosts)."""
        self.hosts = []
        conf.verb = 0  # Suppress scapy output

        try:
            if progress_callback:
                progress_callback("Scanning network via ARP...", 0)

            # Create ARP request
            arp = ARP(pdst=self.subnet)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether / arp

            if progress_callback:
                progress_callback("Sending ARP requests...", 30)

            # Send and receive
            result = srp(packet, timeout=3, verbose=False)[0]

            if progress_callback:
                progress_callback("Processing results...", 70)

            # Parse results
            for sent, received in result:
                host_info = {
                    "ip": received.psrc,
                    "mac": received.hwsrc,
                    "hostname": self._resolve_hostname(received.psrc),
                    "os_type": "Unknown",
                    "hardware": get_mac_manufacturer(received.hwsrc),
                }
                self.hosts.append(host_info)

            if progress_callback:
                progress_callback(f"Found {len(self.hosts)} hosts", 100)

        except Exception as e:
            if progress_callback:
                progress_callback(f"Scan error: {str(e)}", 100)

        return self.hosts

    def scan_nmap(self, progress_callback: Callable = None) -> List[Dict]:
        """Scan using Nmap for more detailed host information."""
        try:
            result = subprocess.run(
                ["nmap", "-sn", "-n", self.subnet],
                capture_output=True, text=True, timeout=120
            )

            hosts = []
            current_ip = None
            current_mac = None

            for line in result.stdout.split("\n"):
                if "Nmap scan report for" in line:
                    current_ip = line.split()[-1].strip("()")
                elif "MAC Address:" in line:
                    current_mac = line.split()[2]
                    hostname = ""
                    if "(" in line and ")" in line:
                        hostname = line.split("(")[1].split(")")[0]
                    hosts.append({
                        "ip": current_ip,
                        "mac": current_mac,
                        "hostname": hostname,
                        "os_type": "Unknown",
                        "hardware": get_mac_manufacturer(current_mac),
                    })
                    current_ip = None
                    current_mac = None

            self.hosts = hosts
            return hosts

        except Exception as e:
            return self.scan_arp(progress_callback)  # Fallback to ARP

    def _resolve_hostname(self, ip: str) -> str:
        """Try to resolve hostname from IP."""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname.split(".")[0]
        except (socket.herror, socket.gaierror):
            return ""

    def quick_scan(self) -> List[Dict]:
        """Perform a quick scan (ARP only, no callbacks)."""
        return self.scan_arp()

    def get_my_ip(self) -> str:
        """Get the IP address of this machine."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def get_gateway(self) -> str:
        """Get the default gateway IP."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            parts = local_ip.split(".")
            return f"{parts[0]}.{parts[1]}.{parts[2]}.1"
        except Exception:
            return "192.168.1.1"