"""
HomeNet — Configuration Manager
Handles all application settings, time blocking rules, and categories.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any

CONFIG_DIR = Path("/var/lib/homenetservice")
CONFIG_FILE = CONFIG_DIR / "homenetservice.json"

# ─── Default Configuration ───────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "general": {
        "language": "en",  # "en" or "ar"
        "admin_username": "admin",
        "admin_password_hash": "123456",  # Default (changed on first login)
        "recovery_email": "",
        "interface": "eth0",  # Network interface to monitor
        "log_level": "INFO",
    },
    "time_blocking": {
        "enabled": True,
        "block_start": "23:00",  # 11 PM
        "block_end": "00:00",    # 12 AM (midnight)
        "block_days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
        "whitelisted_hosts": [],
    },
    "categories": {
        "gaming": {
            "enabled": False,
            "domains": [
                "*.playstation.com", "*.xbox.com", "*.steam.com",
                "*.epicgames.com", "*.ea.com", "*.blizzard.com",
                "*.nintendo.com", "*.riotgames.com", "*.valve.com",
                "*.ubisoft.com", "*.activision.com", "*.take2games.com",
            ],
            "ports": [27015, 27016, 27017, 27018, 27019, 3478, 3479, 3480],
        },
        "social_media": {
            "enabled": False,
            "domains": [
                "*.facebook.com", "*.instagram.com", "*.tiktok.com",
                "*.twitter.com", "*.x.com", "*.snapchat.com",
                "*.linkedin.com", "*.pinterest.com", "*.reddit.com",
                "*.whatsapp.com", "*.telegram.org", "*.discord.com",
                "*.messenger.com", "*.fbcdn.net", "*.twimg.com",
            ],
            "ports": [],
        },
        "streaming": {
            "enabled": False,
            "domains": [
                "*.netflix.com", "*.youtube.com", "*.ytimg.com",
                "*.twitch.tv", "*.hulu.com", "*.disneyplus.com",
                "*.primevideo.com", "*.hbomax.com", "*.spotify.com",
                "*.apple.com", "*.soundcloud.com", "*.deezer.com",
                "*.crunchyroll.com", "*.paramountplus.com",
                "*.peacocktv.com", "*.max.com",
            ],
            "ports": [],
        },
    },
    "alerts": {
        "new_host_notification": True,
        "high_traffic_threshold_mb": 500,
        "email_alerts": False,
        "desktop_notifications": True,
    },
    "hosts": {},  # Discovered hosts will be stored here
    "rules": [],  # Custom blocking rules
}

# ─── Category Domain Lists (expanded) ────────────────────────────────────────

GAMING_DOMAINS = [
    "playstation.com", "xbox.com", "steam.com", "epicgames.com",
    "ea.com", "blizzard.com", "nintendo.com", "riotgames.com",
    "valve.com", "ubisoft.com", "activision.com", "take2games.com",
    "roblox.com", "minecraft.net", "gamepass.com", "psn.com",
    "xboxlive.com", "steamcommunity.com", "steamusercontent.com",
    "cdn.cloudflare.steamstatic.com", "cloudfront.steamstatic.com",
    "akamai.steamstatic.com", "fastly.steamstatic.com",
]

SOCIAL_MEDIA_DOMAINS = [
    "facebook.com", "instagram.com", "tiktok.com", "twitter.com",
    "x.com", "snapchat.com", "linkedin.com", "pinterest.com",
    "reddit.com", "whatsapp.com", "telegram.org", "discord.com",
    "messenger.com", "fbcdn.net", "twimg.com", "cdninstagram.com",
    "fb.com", "fb.watch", "ig.me", "tiktokv.com", "musical.ly",
    "snap.com", "snap-dev.net", "sc-cdn.net", "sc-gw.com",
    "t.co", "twitpic.com", "vine.co", "periscope.tv",
    "clubhouseapi.com", "beehiiv.com", "threads.net",
    "bsky.app", "bsky.social",
]

STREAMING_DOMAINS = [
    "netflix.com", "youtube.com", "ytimg.com", "twitch.tv",
    "hulu.com", "disneyplus.com", "primevideo.com", "hbomax.com",
    "spotify.com", "apple.com", "soundcloud.com", "deezer.com",
    "crunchyroll.com", "paramountplus.com", "peacocktv.com",
    "max.com", "vimeo.com", "dailymotion.com", "tubi.tv",
    "pluto.tv", "plex.tv", "emby.media", "jellyfin.org",
    "roku.com", "firetv.com", "chromecast.com",
    "googlevideo.com", "youtu.be", "ytimg.com",
    "nflxvideo.net", "nflximg.net", "nflxext.com",
    "amazonvideo.com", "media-amazon.com", "aiv-cdn.net",
    "hbo.com", "hbogo.com", "hbonow.com", "disney.com",
    "disneystreaming.com", "bamgrid.com",
]


class ConfigManager:
    """Manages HomeNet configuration with persistence."""

    def __init__(self, config_path: Path = CONFIG_FILE):
        self.config_path = config_path
        self.config: Dict[str, Any] = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return DEFAULT_CONFIG.copy()
        return DEFAULT_CONFIG.copy()

    def save(self) -> None:
        """Save configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value using dot notation (e.g., 'time_blocking.enabled')."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """Set a config value using dot notation."""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save()

    def is_time_to_block(self) -> bool:
        """Check if current time falls within blocking period."""
        import datetime
        if not self.get("time_blocking.enabled", False):
            return False

        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M")
        current_day = now.strftime("%a").lower()[:3]

        # Check if today is a blocked day
        block_days = self.get("time_blocking.block_days", [])
        if block_days and current_day not in block_days:
            return False

        block_start = self.get("time_blocking.block_start", "23:00")
        block_end = self.get("time_blocking.block_end", "00:00")

        # Handle overnight blocking (e.g., 23:00 to 06:00)
        if block_start > block_end:
            return current_time >= block_start or current_time <= block_end
        else:
            return block_start <= current_time <= block_end

    def is_host_whitelisted(self, ip: str) -> bool:
        """Check if a host IP is whitelisted from time blocking."""
        whitelist = self.get("time_blocking.whitelisted_hosts", [])
        return ip in whitelist

    def get_blocked_domains(self) -> List[str]:
        """Get all blocked domains across enabled categories."""
        domains = set()
        cats = self.get("categories", {})
        for cat_name, cat_config in cats.items():
            if cat_config.get("enabled", False):
                for domain in cat_config.get("domains", []):
                    domains.add(domain.lstrip("*."))
        return list(domains)

    def get_blocked_ports(self) -> List[int]:
        """Get all blocked ports across enabled categories."""
        ports = set()
        cats = self.get("categories", {})
        for cat_config in cats.values():
            if cat_config.get("enabled", False):
                for port in cat_config.get("ports", []):
                    ports.add(port)
        return list(ports)

    def reset_to_defaults(self) -> None:
        """Reset configuration to factory defaults."""
        self.config = DEFAULT_CONFIG.copy()
        self.save()