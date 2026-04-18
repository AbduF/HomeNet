import requests
import time

class SpeedTest:
    def check_connection(self):
        try:
            requests.get("https://1.1.1.1", timeout=3)
            return True
        except:
            return False

    def run_test(self):
        url = "https://speed.cloudflare.com/__down?bytes=10000000"
        start = time.time()
        try:
            r = requests.get(url, timeout=10)
            mbps = (len(r.content) * 8) / (time.time() - start) / 1e6
            return f"{mbps:.2f} Mbps"
        except:
            return "Failed"