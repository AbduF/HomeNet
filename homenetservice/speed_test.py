"""
HomeNet — Internet Speed Test
Tests download, upload speed and ping using speedtest-cli.
"""

import speedtest
import socket
from typing import Dict, Optional
from .database import DatabaseManager


class SpeedTester:
    """Performs internet speed tests."""

    def __init__(self, db: DatabaseManager):
        self.db = db
        self._st = None

    def _get_speedtest(self) -> speedtest.Speedtest:
        """Get or create speedtest instance."""
        if self._st is None:
            self._st = speedtest.Speedtest()
        return self._st

    def run_test(self, callback=None) -> Dict:
        """Run a complete speed test."""
        st = self._get_speedtest()
        result = {
            "download_mbps": 0,
            "upload_mbps": 0,
            "ping_ms": 0,
            "server": "",
            "success": False,
            "error": "",
        }

        try:
            if callback:
                callback("selecting_server", 0)

            st.get_best_server()
            result["server"] = st.best["host"]
            result["ping_ms"] = st.results.ping

            if callback:
                callback("testing_download", 30)

            result["download_mbps"] = st.download() / 1_000_000  # Convert to Mbps

            if callback:
                callback("testing_upload", 60)

            result["upload_mbps"] = st.upload() / 1_000_000  # Convert to Mbps

            result["success"] = True

            if callback:
                callback("complete", 100)

            # Save to database
            self.db.save_speed_test(
                result["download_mbps"],
                result["upload_mbps"],
                result["ping_ms"],
                result["server"]
            )

        except speedtest.ConfigRetrievalError:
            result["error"] = "Failed to retrieve speedtest configuration"
        except speedtest.SpeedtestBestServerFailure:
            result["error"] = "Failed to find best server"
        except Exception as e:
            result["error"] = str(e)

        return result

    def check_connection(self) -> Dict:
        """Quick connection check (ping only)."""
        result = {
            "connected": False,
            "ping_ms": 0,
            "error": "",
        }

        try:
            st = self._get_speedtest()
            st.get_best_server()
            result["connected"] = True
            result["ping_ms"] = st.results.ping
        except Exception as e:
            result["error"] = str(e)

        return result

    def get_history(self) -> list:
        """Get speed test history."""
        return self.db.get_speed_tests(limit=20)