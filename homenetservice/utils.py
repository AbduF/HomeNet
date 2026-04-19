"""
HomeNet — Utility Functions
Helper functions for formatting, validation, and common operations.
"""

import os
import socket
import struct
import platform
import subprocess
from typing import List, Dict, Optional


def format_bytes(num_bytes: int) -> str:
    """Format bytes into human-readable string."""
    if num_bytes < 0:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.2f} PB"


def get_mac_manufacturer(mac: str) -> str:
    """Get manufacturer from MAC address OUI."""
    if not mac:
        return "Unknown"
    oui = mac.replace(":", "").replace("-", "").upper()[:6]
    # Common OUIs
    manufacturers = {
        "001A79": "Apple",
        "001B63": "Apple",
        "001E58": "Apple",
        "002369": "Apple",
        "002500": "Apple",
        "002608": "Apple",
        "3C15C2": "Apple",
        "ACBC32": "Apple",
        "B8E856": "Apple",
        "F01898": "Apple",
        "B0BE76": "Apple",
        "0003F2": "Microsoft",
        "00125A": "Microsoft",
        "001DD8": "Microsoft",
        "005056": "VMware",
        "000C29": "VMware",
        "0050B6": "VMware",
        "00155D": "Microsoft Hyper-V",
        "080027": "Oracle VirtualBox",
        "000F3D": "Intel",
        "0016D3": "Intel",
        "001F3C": "Intel",
        "00216A": "Intel",
        "94659C": "Huawei",
        "E4F14C": "Huawei",
        "00E04C": "Realtek",
        "000B46": "ASUS",
        "1831BF": "ASUS",
        "00179A": "TP-Link",
        "50E549": "TP-Link",
        "001A2B": "Dell",
        "A4BADB": "Dell",
        "246E96": "Dell",
        "001EC9": "Sony",
        "00238A": "Sony",
        "182A7B": "Nintendo",
        "4C8B30": "Nintendo",
        "0009BF": "Sony PlayStation",
        "5C864A": "Sony PlayStation",
        "7C9EBD": "Sony PlayStation",
        "001BF3": "Nintendo Wii",
        "001D5E": "Nintendo DS",
        "B83AFD": "Amazon (Echo/Fire TV)",
        "18742E": "Amazon",
        "00FC8B": "Google",
        "3C5A37": "Google",
        "546009": "Google",
        "A47733": "Google",
        "D83BBF": "Google",
        "E8611F": "Google Nest",
        "00265E": "Samsung",
        "001632": "Samsung",
        "20D160": "Samsung",
        "5001BB": "Samsung",
        "782544": "Samsung",
        "A45046": "Samsung",
        "F47B5E": "Samsung",
    }
    return manufacturers.get(oui, "Unknown")


def get_os_fingerprint(ip: str, ttl: int = None) -> str:
    """Estimate OS from TTL value."""
    if ttl is None:
        return "Unknown"
    if ttl <= 64:
        return "Linux/Unix"
    elif ttl <= 128:
        return "Windows"
    elif ttl <= 255:
        return "Network Device / Router"
    return "Unknown"


def get_hardware_info(ip: str) -> str:
    """Try to get hardware info via SNMP or other means."""
    mac = get_mac_from_arp(ip)
    manufacturer = get_mac_manufacturer(mac) if mac else ""
    return manufacturer


def get_mac_from_arp(ip: str) -> Optional[str]:
    """Get MAC address from ARP table."""
    try:
        if platform.system() == "Linux":
            result = subprocess.run(
                ["arp", "-n", ip], capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.split("\n"):
                if ip in line:
                    parts = line.split()
                    for part in parts:
                        if ":" in part and len(part) == 17:
                            return part
        elif platform.system() == "Windows":
            result = subprocess.run(
                ["arp", "-a", ip], capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.split("\n"):
                if ip in line:
                    parts = line.split()
                    for part in parts:
                        if "-" in part and len(part) == 17:
                            return part.replace("-", ":")
    except Exception:
        pass
    return None


def get_local_interfaces() -> List[Dict]:
    """Get all network interfaces."""
    interfaces = []
    try:
        if platform.system() == "Linux":
            result = subprocess.run(
                ["ip", "-j", "addr"], capture_output=True, text=True, timeout=5
            )
            import json
            data = json.loads(result.stdout)
            for iface in data:
                info = {
                    "name": iface.get("ifname", ""),
                    "state": iface.get("operstate", "unknown"),
                    "mac": "",
                    "ipv4": [],
                    "ipv6": [],
                }
                for addr in iface.get("addr_info", []):
                    if addr.get("family") == "inet":
                        info["ipv4"].append(addr.get("local", ""))
                    elif addr.get("family") == "inet6":
                        info["ipv6"].append(addr.get("local", ""))
                if info["ipv4"] or info["ipv6"]:
                    interfaces.append(info)
        else:
            import netifaces
            for iface_name in netifaces.interfaces():
                addrs = netifaces.ifaddresses(iface_name)
                info = {
                    "name": iface_name,
                    "state": "up" if addrs else "down",
                    "mac": addrs.get(netifaces.AF_LINK, [{}])[0].get("addr", ""),
                    "ipv4": [a.get("addr", "") for a in addrs.get(netifaces.AF_INET, [])],
                    "ipv6": [a.get("addr", "") for a in addrs.get(netifaces.AF_INET6, [])],
                }
                interfaces.append(info)
    except Exception:
        pass
    return interfaces


def get_default_gateway() -> str:
    """Get the default gateway IP."""
    try:
        if platform.system() == "Linux":
            result = subprocess.run(
                ["ip", "route", "show", "default"],
                capture_output=True, text=True, timeout=5
            )
            for part in result.stdout.split():
                try:
                    socket.inet_aton(part)
                    return part
                except socket.error:
                    continue
        elif platform.system() == "Windows":
            result = subprocess.run(
                ["route", "print", "0.0.0.0"],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.split("\n"):
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        socket.inet_aton(parts[2])
                        return parts[2]
                    except socket.error:
                        continue
    except Exception:
        pass
    return "Unknown"


def get_dns_servers() -> List[str]:
    """Get DNS servers from system configuration."""
    dns_servers = []
    try:
        if platform.system() == "Linux":
            with open("/etc/resolv.conf", "r") as f:
                for line in f:
                    if line.startswith("nameserver"):
                        dns_servers.append(line.split()[1])
        elif platform.system() == "Windows":
            result = subprocess.run(
                ["ipconfig", "/all"], capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.split("\n"):
                if "DNS Server" in line or "DNS Servers" in line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        dns_servers.append(parts[1].strip())
    except Exception:
        pass

    if not dns_servers:
        dns_servers = ["8.8.8.8", "8.8.4.4"]  # Google DNS fallback
    return dns_servers


def check_internet_connection() -> bool:
    """Check if internet connection is available."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except (socket.error, OSError):
        return False


def get_system_info() -> Dict:
    """Get system information."""
    import psutil
    return {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "ram_total": psutil.virtual_memory().total,
        "ram_available": psutil.virtual_memory().available,
        "cpu_count": psutil.cpu_count(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "disk_usage": psutil.disk_usage("/").percent,
        "hostname": platform.node(),
    }