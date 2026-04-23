"""
HomeNet - Configuration Module
"""

import json
from pathlib import Path
import logging


class Config:
    """Configuration manager for HomeNet."""

    DEFAULT_CONFIG = {
        'language': 'en',
        'theme': 'dark',
        'blocking_enabled': False,
        'network_interface': 'auto',
        'scan_interval': 60,
        'traffic_log_interval': 60,
        'alert_new_host': True,
        'alert_high_traffic': True,
        'high_traffic_threshold': 1000000000,  # 1GB
        'auto_block_schedules': True,
        'email_enabled': False,
        'smtp_host': '',
        'smtp_port': 587,
        'smtp_user': '',
        'smtp_password': '',
        'admin_email': 'abdalfaqeeh@gmail.com'
    }

    def __init__(self, config_path):
        self.config_path = Path(config_path)
        self.logger = logging.getLogger("HomeNet.Config")
        self.config = self.load()

    def load(self):
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                return {**self.DEFAULT_CONFIG, **config}
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")
                return self.DEFAULT_CONFIG.copy()
        else:
            return self.DEFAULT_CONFIG.copy()

    def save(self):
        """Save configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            self.logger.info("Configuration saved")
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")

    def get(self, key, default=None):
        """Get configuration value."""
        return self.config.get(key, default)

    def set(self, key, value):
        """Set configuration value."""
        self.config[key] = value
        self.save()

    def update(self, updates):
        """Update multiple configuration values."""
        self.config.update(updates)
        self.save()
