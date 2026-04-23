"""
HomeNet - Speed Test Module
Internet connection speed testing
"""

import logging
import subprocess
import re
import speedtest
from datetime import datetime


class SpeedTest:
    """Internet speed test wrapper."""

    def __init__(self):
        self.logger = logging.getLogger("HomeNet.SpeedTest")
        self.last_result = None

    def run_test(self, server_id=None):
        """Run speed test."""
        try:
            self.logger.info("Starting speed test...")

            st = speedtest.Speedtest()

            # Get best server
            st.get_servers()
            best_server = st.get_best_server()
            self.logger.info(f"Using server: {best_server['host']}")

            # Download test
            self.logger.info("Testing download speed...")
            download_speed = st.download()

            # Upload test
            self.logger.info("Testing upload speed...")
            upload_speed = st.upload()

            # Get ping
            ping = st.results.ping

            # Calculate jitter
            # (simplified - actual jitter requires multiple pings)
            jitter = 0

            result = {
                'timestamp': datetime.now().isoformat(),
                'download_speed': download_speed,
                'download_mbps': download_speed / 1000000,
                'upload_speed': upload_speed,
                'upload_mbps': upload_speed / 1000000,
                'ping_ms': ping,
                'jitter_ms': jitter,
                'server': best_server['host'],
                'server_location': f"{best_server.get('country', 'Unknown')}, {best_server.get('name', 'Unknown')}"
            }

            self.last_result = result
            self.logger.info(f"Speed test complete: {result['download_mbps']:.2f} Mbps down, {result['upload_mbps']:.2f} Mbps up")

            return result

        except Exception as e:
            self.logger.error(f"Speed test error: {e}")
            return None

    def get_servers(self, limit=10):
        """Get available speed test servers."""
        try:
            st = speedtest.Speedtest()
            servers = st.get_servers()
            return list(servers.keys())[:limit]
        except Exception as e:
            self.logger.error(f"Error getting servers: {e}")
            return []

    def get_last_result(self):
        """Get last test result."""
        return self.last_result

    def run_test_with_progress(self, progress_callback=None):
        """Run speed test with progress callback."""
        try:
            st = speedtest.Speedtest()

            if progress_callback:
                progress_callback("Finding best server...")

            st.get_servers()
            best_server = st.get_best_server()

            if progress_callback:
                progress_callback(f"Testing with {best_server['host']}...")

            if progress_callback:
                progress_callback("Testing download speed...")
            download_speed = st.download()

            if progress_callback:
                progress_callback("Testing upload speed...")
            upload_speed = st.upload()

            if progress_callback:
                progress_callback("Measuring latency...")
            ping = st.results.ping

            result = {
                'timestamp': datetime.now().isoformat(),
                'download_speed': download_speed,
                'download_mbps': download_speed / 1000000,
                'upload_speed': upload_speed,
                'upload_mbps': upload_speed / 1000000,
                'ping_ms': ping,
                'server': best_server['host']
            }

            self.last_result = result

            if progress_callback:
                progress_callback("Complete!")

            return result

        except Exception as e:
            self.logger.error(f"Speed test error: {e}")
            return None
