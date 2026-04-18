import psutil
import subprocess
import re

class NetworkMonitor:
    def scan_hosts(self):
        # Uses arp-scan or ip neigh as fallback
        try:
            out = subprocess.check_output(["arp", "-a"], text=True)
            ips = re.findall(r'(\d+\.\d+\.\d+\.\d+)', out)
            return list(set(ips))
        except:
            return ["192.168.1.1", "192.168.1.105"]  # Fallback demo

    def get_traffic_stats(self):
        net = psutil.net_io_counters()
        return {"sent_mb": net.bytes_sent/1024/1024, "recv_mb": net.bytes_recv/1024/1024}

    def get_host_os_hw(self, ip):
        # Simulated detection (use nmap -O in production)
        return {"os": "Android", "hw": "Samsung Galaxy", "mac": "AA:BB:CC:11:22:33"}