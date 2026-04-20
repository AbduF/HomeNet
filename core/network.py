"""
HomeNet - Network Scanner Module
Network discovery and host detection
"""

import logging
import subprocess
import re
from datetime import datetime
import psutil


class NetworkScanner:
    """Network scanner for discovering hosts."""

    def __init__(self):
        self.logger = logging.getLogger("HomeNet.NetworkScanner")

    def get_local_network_info(self):
        """Get local network interface information."""
        try:
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()

            network_info = []
            for iface, addrs in interfaces.items():
                if iface == 'lo':
                    continue

                iface_stats = stats.get(iface)
                if not iface_stats:
                    continue

                info = {
                    'interface': iface,
                    'ip': None,
                    'mac': None,
                    'netmask': None,
                    'broadcast': None,
                    'is_up': iface_stats.isup
                }

                for addr in addrs:
                    if addr.family.name == 'AF_INET':
                        info['ip'] = addr.address
                        info['netmask'] = addr.netmask
                    elif addr.family.name == 'AF_LINK':
                        info['mac'] = addr.address

                if info['ip']:
                    network_info.append(info)

            return network_info
        except Exception as e:
            self.logger.error(f"Error getting network info: {e}")
            return []

    def get_default_gateway(self):
        """Get default gateway IP."""
        try:
            gateways = psutil.net_if_stats()
            # Try to read from route
            result = subprocess.run(['ip', 'route', 'show', 'default'],
                                 capture_output=True, text=True)
            if result.returncode == 0:
                match = re.search(r'default via (\S+)', result.stdout)
                if match:
                    return match.group(1)
        except Exception as e:
            self.logger.error(f"Error getting gateway: {e}")
        return None

    def get_subnet_from_interface(self, interface='eth0'):
        """Calculate subnet from interface IP."""
        try:
            ip = None
            netmask = None

            for iface, addrs in psutil.net_if_addrs().items():
                if iface == interface:
                    for addr in addrs:
                        if addr.family.name == 'AF_INET':
                            ip = addr.address
                            netmask = addr.netmask

            if ip and netmask:
                # Convert netmask to CIDR
                binary_str = ''
                for octet in netmask.split('.'):
                    binary_str += bin(int(octet))[2:].zfill(8)

                cidr = str(len(binary_str.rstrip('0')))
                return f"{ip}/{cidr}"
        except Exception as e:
            self.logger.error(f"Error calculating subnet: {e}")

        return None

    def scan_arp_table(self):
        """Scan ARP table for known hosts."""
        hosts = []

        try:
            # Read ARP table
            result = subprocess.run(['ip', 'neigh', 'show'],
                                 capture_output=True, text=True)

            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if not line:
                        continue

                    parts = line.split()
                    if len(parts) < 4:
                        continue

                    ip = parts[0]
                    mac = None

                    # Parse line
                    for i, part in enumerate(parts):
                        if part == 'lladdr' and i + 1 < len(parts):
                            mac = parts[i + 1]
                            break

                    if mac and mac != '(INCOMPLETE)':
                        host = {
                            'ip_address': ip,
                            'mac_address': mac.upper(),
                            'hostname': self.resolve_hostname(ip),
                            'last_seen': datetime.now().isoformat()
                        }
                        hosts.append(host)

            self.logger.info(f"Found {len(hosts)} hosts in ARP table")
            return hosts

        except Exception as e:
            self.logger.error(f"Error scanning ARP table: {e}")
            return []

    def scan_network_nmap(self):
        """Scan network using nmap (if available)."""
        try:
            # Get local IP and subnet
            local_ip = None
            for iface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family.name == 'AF_INET' and not addr.address.startswith('127.'):
                        local_ip = addr.address
                        break

            if not local_ip:
                return []

            # Get subnet
            subnet = '.'.join(local_ip.split('.')[:3]) + '.0/24'

            result = subprocess.run(
                ['nmap', '-sn', '-oX', '-', subnet],
                capture_output=True, text=True
            )

            if result.returncode == 0:
                return self.parse_nmap_xml(result.stdout)

        except FileNotFoundError:
            self.logger.warning("nmap not installed, using ARP scan")
        except Exception as e:
            self.logger.error(f"Error with nmap scan: {e}")

        return self.scan_arp_table()

    def parse_nmap_xml(self, xml_output):
        """Parse nmap XML output."""
        import xml.etree.ElementTree as ET
        hosts = []

        try:
            root = ET.fromstring(xml_output)
            for host in root.findall('.//host'):
                ip = host.find('.//address[@addrtype="ipv4"]')
                mac = host.find('.//address[@addrtype="mac"]')
                hostname_elem = host.find('.//hostname')

                if ip is not None:
                    host_info = {
                        'ip_address': ip.get('addr'),
                        'mac_address': mac.get('addr').upper() if mac is not None else None,
                        'hostname': hostname_elem.get('name') if hostname_elem is not None else None,
                        'last_seen': datetime.now().isoformat()
                    }
                    hosts.append(host_info)

        except Exception as e:
            self.logger.error(f"Error parsing nmap XML: {e}")

        return hosts

    def resolve_hostname(self, ip):
        """Resolve hostname for IP."""
        try:
            import socket
            hostname, _, _ = socket.gethostbyaddr(ip)
            return hostname
        except:
            return None

    def detect_os(self, hostname_info=None):
        """Attempt to detect OS from available info."""
        if not hostname_info:
            return 'Unknown'

        hostname = hostname_info.get('hostname', '') or ''

        # Simple heuristics based on hostname
        hostname_lower = hostname.lower()

        if 'iphone' in hostname_lower or 'android' in hostname_lower:
            return 'Mobile'
        elif 'macbook' in hostname_lower or 'imac' in hostname_lower:
            return 'macOS'
        elif 'ubuntu' in hostname_lower or 'debian' in hostname_lower:
            return 'Linux'
        elif 'windows' in hostname_lower:
            return 'Windows'
        elif 'raspberrypi' in hostname_lower or 'raspbian' in hostname_lower:
            return 'Raspberry Pi OS'

        return 'Unknown'

    def detect_device_type(self, hostname_info=None):
        """Detect device type from available info."""
        if not hostname_info:
            return 'Unknown'

        hostname = hostname_info.get('hostname', '') or ''

        hostname_lower = hostname.lower()

        if 'iphone' in hostname_lower or 'ipad' in hostname_lower:
            return 'Mobile'
        elif 'android' in hostname_lower:
            return 'Android'
        elif 'macbook' in hostname_lower or 'imac' in hostname_lower:
            return 'Desktop'
        elif 'laptop' in hostname_lower or 'notebook' in hostname_lower:
            return 'Laptop'
        elif 'tv' in hostname_lower or 'roku' in hostname_lower or 'firestick' in hostname_lower:
            return 'Smart TV'
        elif 'ps5' in hostname_lower or 'xbox' in hostname_lower or 'switch' in hostname_lower:
            return 'Gaming Console'
        elif 'echo' in hostname_lower or 'alexa' in hostname_lower:
            return 'Smart Speaker'
        elif 'nest' in hostname_lower or 'ring' in hostname_lower:
            return 'Smart Home'

        return 'Unknown'

    def get_mac_vendor(self, mac):
        """Get vendor from MAC address (simplified)."""
        if not mac:
            return 'Unknown'

        # Common OUI prefixes
        vendors = {
            '00:1A:2B': 'Cisco',
            '00:50:56': 'VMware',
            '08:00:27': 'Oracle VirtualBox',
            'B8:27:EB': 'Raspberry Pi',
            'DC:A6:32': 'Raspberry Pi',
            'E4:5F:01': 'Raspberry Pi',
            '00:1C:B3': 'Apple',
            '3C:22:FB': 'Apple',
            '00:26:BB': 'Apple',
            'A4:83:E7': 'Apple',
            'F0:18:98': 'Apple',
            '20:AB:37': 'Samsung',
            'B4:3A:28': 'Samsung',
            'D0:C5:D3': 'Google',
            'F4:F5:D8': 'Google',
            '94:65:2D': 'OnePlus',
            '2E:8B:FD': 'Huawei',
            '34:00:A3': 'Intel',
            '00:15:5D': 'Microsoft Hyper-V',
        }

        prefix = ':'.join(mac.split(':')[:3])
        return vendors.get(prefix, 'Unknown')

    def full_scan(self):
        """Perform full network scan."""
        self.logger.info("Starting full network scan...")

        hosts = self.scan_arp_table()

        # Enrich host information
        for host in hosts:
            host['os_type'] = self.detect_os(host)
            host['device_type'] = self.detect_device_type(host)
            host['mac_vendor'] = self.get_mac_vendor(host.get('mac_address'))

        self.logger.info(f"Scan complete. Found {len(hosts)} hosts")
        return hosts
