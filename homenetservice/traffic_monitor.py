"""
HomeNet — Traffic Monitor
Monitors network traffic per host using packet capture and interface stats.
"""

import threading
import time
import psutil
from typing import Dict, List, Optional, Callable
from collections import defaultdict
from scapy.all import sniff, IP, TCP, UDP, conf


class TrafficMonitor:
    """Monitors and tracks network traffic per host."""

    def __init__(self, interface: str = "eth0"):
        self.interface = interface
        self.running = False
        self.traffic_data: Dict[str, Dict] = defaultdict(lambda: {
            "bytes_sent": 0,
            "bytes_recv": 0,
            "packets_sent": 0,
            "packets_recv": 0,
            "last_updated": time.time(),
        })
        self.category_data: Dict[str, Dict] = defaultdict(lambda: {
            "gaming": 0, "social_media": 0, "streaming": 0, "other": 0
        })
        self.monitor_thread: Optional[threading.Thread] = None
        self.callback: Optional[Callable] = None

    def start(self, callback: Callable = None, interval: int = 5):
        """Start traffic monitoring in background thread."""
        self.running = True
        self.callback = callback
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, args=(interval,), daemon=True
        )
        self.monitor_thread.start()

    def stop(self):
        """Stop traffic monitoring."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

    def _monitor_loop(self, interval: int):
        """Main monitoring loop using interface statistics."""
        while self.running:
            try:
                self._capture_interface_stats()
                if self.callback:
                    self.callback(dict(self.traffic_data))
                time.sleep(interval)
            except Exception as e:
                print(f"Monitor error: {e}")
                time.sleep(interval)

    def _capture_interface_stats(self):
        """Capture traffic stats from network interface."""
        try:
            net_io = psutil.net_io_counters(pernic=True)
            if self.interface in net_io:
                stats = net_io[self.interface]
                # Distribute across known hosts proportionally
                total_hosts = len(self.traffic_data) or 1
                per_host_sent = stats.bytes_sent // total_hosts
                per_host_recv = stats.bytes_recv // total_hosts

                for ip in list(self.traffic_data.keys()):
                    self.traffic_data[ip]["bytes_sent"] += per_host_sent
                    self.traffic_data[ip]["bytes_recv"] += per_host_recv
                    self.traffic_data[ip]["last_updated"] = time.time()
        except Exception:
            pass

    def process_packet(self, packet):
        """Process a single captured packet (for detailed analysis)."""
        if not packet.haslayer(IP):
            return

        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        pkt_len = len(packet)

        # Track by source IP
        if src_ip.startswith("192.168.") or src_ip.startswith("10.") or src_ip.startswith("172."):
            self.traffic_data[src_ip]["bytes_sent"] += pkt_len
            self.traffic_data[src_ip]["packets_sent"] += 1
            self.traffic_data[src_ip]["last_updated"] = time.time()

        # Track by destination IP
        if dst_ip.startswith("192.168.") or dst_ip.startswith("10.") or dst_ip.startswith("172."):
            self.traffic_data[dst_ip]["bytes_recv"] += pkt_len
            self.traffic_data[dst_ip]["packets_recv"] += 1
            self.traffic_data[dst_ip]["last_updated"] = time.time()

        # Categorize traffic
        self._categorize_traffic(packet, src_ip, dst_ip)

    def _categorize_traffic(self, packet, src_ip: str, dst_ip: str):
        """Categorize traffic based on port and DNS."""
        if packet.haslayer(TCP):
            dst_port = packet[TCP].dport
            src_port = packet[TCP].sport

            if dst_port in [443, 80] and packet.haslayer("DNS"):
                # Could check DNS query for domain categorization
                pass

            # Gaming ports
            gaming_ports = {27015, 27016, 27017, 3478, 3479, 3480}
            if dst_port in gaming_ports or src_port in gaming_ports:
                self.category_data[src_ip]["gaming"] += len(packet)

            # Common streaming ports
            streaming_ports = {1935, 8554, 554}  # RTMP, RTSP
            if dst_port in streaming_ports:
                self.category_data[src_ip]["streaming"] += len(packet)

    def get_traffic_data(self) -> Dict:
        """Get current traffic data."""
        return dict(self.traffic_data)

    def get_category_data(self) -> Dict:
        """Get traffic categorized by type."""
        return dict(self.category_data)

    def reset(self):
        """Reset all traffic counters."""
        self.traffic_data.clear()
        self.category_data.clear()

    def start_sniffing(self, interface: str = None):
        """Start packet-level sniffing for detailed traffic analysis."""
        iface = interface or self.interface
        conf.verb = 0

        def packet_handler(pkt):
            if self.running:
                self.process_packet(pkt)

        self.sniff_thread = threading.Thread(
            target=lambda: sniff(iface=iface, prn=packet_handler, store=False),
            daemon=True
        )
        self.sniff_thread.start()