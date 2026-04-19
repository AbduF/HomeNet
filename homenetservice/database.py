"""
HomeNet — Database Manager
SQLite database for hosts, traffic logs, alerts, and user management.
"""

import sqlite3
import hashlib
import datetime
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any

DB_DIR = Path("/var/lib/homenetservice")
DB_PATH = DB_DIR / "homenetservice.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT,
    is_admin BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS hosts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT UNIQUE NOT NULL,
    mac_address TEXT,
    hostname TEXT,
    os_type TEXT,
    hardware_info TEXT,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_blocked BOOLEAN DEFAULT 0,
    is_whitelisted BOOLEAN DEFAULT 0,
    notes TEXT,
    UNIQUE(ip_address)
);

CREATE TABLE IF NOT EXISTS traffic_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    host_id INTEGER,
    ip_address TEXT,
    bytes_sent INTEGER DEFAULT 0,
    bytes_recv INTEGER DEFAULT 0,
    packets_sent INTEGER DEFAULT 0,
    packets_recv INTEGER DEFAULT 0,
    category TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (host_id) REFERENCES hosts(id)
);

CREATE TABLE IF NOT EXISTS daily_traffic (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    host_id INTEGER,
    ip_address TEXT,
    date TEXT NOT NULL,
    bytes_sent INTEGER DEFAULT 0,
    bytes_recv INTEGER DEFAULT 0,
    total_bytes INTEGER DEFAULT 0,
    FOREIGN KEY (host_id) REFERENCES hosts(id),
    UNIQUE(host_id, date)
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_type TEXT NOT NULL,
    message TEXT,
    severity TEXT DEFAULT 'info',
    host_ip TEXT,
    is_read BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS block_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_type TEXT NOT NULL,
    target TEXT NOT NULL,
    category TEXT,
    enabled BOOLEAN DEFAULT 1,
    schedule TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS speed_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    download_mbps REAL,
    upload_mbps REAL,
    ping_ms REAL,
    server TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_traffic_host ON traffic_log(host_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_daily_traffic_host ON daily_traffic(host_id, date);
CREATE INDEX IF NOT EXISTS idx_alerts_unread ON alerts(is_read);
"""


def init_db(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Initialize database and create tables."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.commit()

    # Create default admin user if not exists
    cursor = conn.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        password_hash = hashlib.sha256("123456".encode()).hexdigest()
        conn.execute(
            "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
            ("admin", password_hash, True)
        )
        conn.commit()

    return conn


class DatabaseManager:
    """High-level database operations for HomeNet."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.conn = init_db(db_path)

    # ─── User Management ──────────────────────────────────────────────────

    def authenticate(self, username: str, password: str) -> bool:
        """Verify user credentials."""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor = self.conn.execute(
            "SELECT id FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        return cursor.fetchone() is not None

    def update_user(self, username: str, new_username: str = None,
                    new_password: str = None, email: str = None) -> bool:
        """Update user credentials."""
        updates = []
        params = []

        if new_username:
            updates.append("username = ?")
            params.append(new_username)
        if new_password:
            password_hash = hashlib.sha256(new_password.encode()).hexdigest()
            updates.append("password_hash = ?")
            params.append(password_hash)
        if email is not None:
            updates.append("email = ?")
            params.append(email)

        if not updates:
            return False

        params.append(username)
        query = f"UPDATE users SET {', '.join(updates)} WHERE username = ?"
        self.conn.execute(query, params)
        self.conn.commit()
        return True

    def reset_password(self, email: str, new_password: str) -> bool:
        """Reset password via email verification."""
        password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        cursor = self.conn.execute(
            "UPDATE users SET password_hash = ? WHERE email = ? AND email != ''",
            (password_hash, email)
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def get_admin_user(self) -> Dict:
        """Get admin user info (without password hash)."""
        cursor = self.conn.execute(
            "SELECT id, username, email, is_admin, created_at FROM users WHERE is_admin = 1 LIMIT 1"
        )
        row = cursor.fetchone()
        return dict(row) if row else {}

    # ── Host Management ──────────────────────────────────────────────────

    def add_or_update_host(self, ip: str, mac: str = "", hostname: str = "",
                           os_type: str = "", hardware_info: str = "") -> int:
        """Add a new host or update existing one."""
        now = datetime.datetime.now().isoformat()

        cursor = self.conn.execute(
            "SELECT id FROM hosts WHERE ip_address = ?", (ip,)
        )
        existing = cursor.fetchone()

        if existing:
            self.conn.execute(
                """UPDATE hosts SET mac_address = ?, hostname = ?, os_type = ?,
                   hardware_info = ?, last_seen = ? WHERE ip_address = ?""",
                (mac, hostname, os_type, hardware_info, now, ip)
            )
            self.conn.commit()
            return existing["id"]
        else:
            cursor = self.conn.execute(
                """INSERT INTO hosts (ip_address, mac_address, hostname,
                   os_type, hardware_info, first_seen, last_seen)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (ip, mac, hostname, os_type, hardware_info, now, now)
            )
            self.conn.commit()

            # Alert for new host
            self.add_alert("new_host", f"New device discovered: {hostname or ip} ({ip})", "warning", ip)
            return cursor.lastrowid

    def get_all_hosts(self) -> List[Dict]:
        """Get all discovered hosts."""
        cursor = self.conn.execute(
            "SELECT *, strftime('%Y-%m-%d %H:%M', last_seen) as last_seen_fmt "
            "FROM hosts ORDER BY last_seen DESC"
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_host_by_ip(self, ip: str) -> Optional[Dict]:
        """Get host details by IP address."""
        cursor = self.conn.execute("SELECT * FROM hosts WHERE ip_address = ?", (ip,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def block_host(self, ip: str, block: bool = True) -> bool:
        """Block or unblock a host."""
        self.conn.execute(
            "UPDATE hosts SET is_blocked = ? WHERE ip_address = ?",
            (block, ip)
        )
        self.conn.commit()
        return True

    def delete_host(self, ip: str) -> bool:
        """Remove a host from the database."""
        self.conn.execute("DELETE FROM hosts WHERE ip_address = ?", (ip,))
        self.conn.commit()
        return True

    # ─── Traffic Logging ──────────────────────────────────────────────────

    def log_traffic(self, ip: str, bytes_sent: int = 0, bytes_recv: int = 0,
                    packets_sent: int = 0, packets_recv: int = 0,
                    category: str = "") -> None:
        """Log traffic for a host."""
        host = self.get_host_by_ip(ip)
        host_id = host["id"] if host else None

        self.conn.execute(
            """INSERT INTO traffic_log
               (host_id, ip_address, bytes_sent, bytes_recv,
                packets_sent, packets_recv, category)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (host_id, ip, bytes_sent, bytes_recv, packets_sent, packets_recv, category)
        )

        # Update daily totals
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        self.conn.execute(
            """INSERT INTO daily_traffic (host_id, ip_address, date,
               bytes_sent, bytes_recv, total_bytes)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(host_id, date) DO UPDATE SET
               bytes_sent = bytes_sent + ?,
               bytes_recv = bytes_recv + ?,
               total_bytes = total_bytes + ?""",
            (host_id, ip, today, bytes_sent, bytes_recv, bytes_sent + bytes_recv,
             bytes_sent, bytes_recv, bytes_sent + bytes_recv)
        )
        self.conn.commit()

    def get_traffic_summary(self, hours: int = 24) -> List[Dict]:
        """Get traffic summary for all hosts."""
        cursor = self.conn.execute(
            """SELECT h.ip_address, h.hostname, h.mac_address,
               COALESCE(SUM(t.bytes_sent), 0) as total_sent,
               COALESCE(SUM(t.bytes_recv), 0) as total_recv,
               COALESCE(SUM(t.bytes_sent + t.bytes_recv), 0) as total_bytes,
               COUNT(t.id) as packet_count
               FROM hosts h
               LEFT JOIN traffic_log t ON h.id = t.host_id
               WHERE t.timestamp > datetime('now', ?) OR t.timestamp IS NULL
               GROUP BY h.ip_address
               ORDER BY total_bytes DESC""",
            (f"-{hours} hours",)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_host_traffic_history(self, ip: str, days: int = 7) -> List[Dict]:
        """Get daily traffic history for a specific host."""
        cursor = self.conn.execute(
            """SELECT date, bytes_sent, bytes_recv, total_bytes
               FROM daily_traffic
               WHERE ip_address = ? AND date > date('now', ?)
               ORDER BY date ASC""",
            (ip, f"-{days} days")
        )
        return [dict(row) for row in cursor.fetchall()]

    # ─── Alerts ───────────────────────────────────────────────────────────

    def add_alert(self, alert_type: str, message: str,
                  severity: str = "info", host_ip: str = "") -> int:
        """Add a new alert."""
        cursor = self.conn.execute(
            """INSERT INTO alerts (alert_type, message, severity, host_ip)
               VALUES (?, ?, ?, ?)""",
            (alert_type, message, severity, host_ip)
        )
        self.conn.commit()

        # Cleanup old alerts (keep last 500)
        self.conn.execute(
            """DELETE FROM alerts WHERE id NOT IN
               (SELECT id FROM alerts ORDER BY created_at DESC LIMIT 500)"""
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_alerts(self, unread_only: bool = False, limit: int = 50) -> List[Dict]:
        """Get recent alerts."""
        query = "SELECT * FROM alerts"
        if unread_only:
            query += " WHERE is_read = 0"
        query += " ORDER BY created_at DESC LIMIT ?"

        cursor = self.conn.execute(query, (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def mark_alerts_read(self) -> None:
        """Mark all alerts as read."""
        self.conn.execute("UPDATE alerts SET is_read = 1 WHERE is_read = 0")
        self.conn.commit()

    def get_unread_count(self) -> int:
        """Get count of unread alerts."""
        cursor = self.conn.execute("SELECT COUNT(*) FROM alerts WHERE is_read = 0")
        return cursor.fetchone()[0]

    # ─── Speed Test History ───────────────────────────────────────────────

    def save_speed_test(self, download: float, upload: float,
                        ping: float, server: str = "") -> int:
        """Save a speed test result."""
        cursor = self.conn.execute(
            """INSERT INTO speed_tests (download_mbps, upload_mbps, ping_ms, server)
               VALUES (?, ?, ?, ?)""",
            (download, upload, ping, server)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_speed_tests(self, limit: int = 20) -> List[Dict]:
        """Get recent speed test results."""
        cursor = self.conn.execute(
            "SELECT * FROM speed_tests ORDER BY timestamp DESC LIMIT ?", (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]

    # ─── Block Rules ──────────────────────────────────────────────────────

    def add_block_rule(self, rule_type: str, target: str,
                       category: str = "", schedule: str = "",
                       enabled: bool = True) -> int:
        """Add a new block rule."""
        cursor = self.conn.execute(
            """INSERT INTO block_rules (rule_type, target, category, schedule, enabled)
               VALUES (?, ?, ?, ?, ?)""",
            (rule_type, target, category, schedule, enabled)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_block_rules(self) -> List[Dict]:
        """Get all block rules."""
        cursor = self.conn.execute("SELECT * FROM block_rules ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]

    def toggle_rule(self, rule_id: int, enabled: bool) -> bool:
        """Enable or disable a block rule."""
        self.conn.execute(
            "UPDATE block_rules SET enabled = ? WHERE id = ?",
            (enabled, rule_id)
        )
        self.conn.commit()
        return True

    def delete_rule(self, rule_id: int) -> bool:
        """Delete a block rule."""
        self.conn.execute("DELETE FROM block_rules WHERE id = ?", (rule_id,))
        self.conn.commit()
        return True

    # ─── Utility ──────────────────────────────────────────────────────────

    def close(self) -> None:
        """Close database connection."""
        self.conn.close()