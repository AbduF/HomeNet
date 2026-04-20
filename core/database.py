"""
HomeNet - Database Module
SQLite database for storing application data
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import logging


class Database:
    """SQLite database handler for HomeNet."""

    def __init__(self, db_path):
        self.db_path = db_path
        self.logger = logging.getLogger("HomeNet.Database")
        self.init_database()

    def get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Initialize database tables."""
        self.logger.info("Initializing database...")

        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'admin',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')

        # Hosts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hosts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mac_address TEXT UNIQUE NOT NULL,
                ip_address TEXT,
                hostname TEXT,
                device_type TEXT,
                os_type TEXT,
                os_version TEXT,
                mac_vendor TEXT,
                blocked INTEGER DEFAULT 0,
                trusted INTEGER DEFAULT 0,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP,
                notes TEXT
            )
        ''')

        # Traffic logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS traffic_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                host_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                bytes_sent INTEGER DEFAULT 0,
                bytes_received INTEGER DEFAULT 0,
                packets_sent INTEGER DEFAULT 0,
                packets_received INTEGER DEFAULT 0,
                FOREIGN KEY (host_id) REFERENCES hosts(id)
            )
        ''')

        # Rules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                category TEXT,
                pattern TEXT NOT NULL,
                action TEXT DEFAULT 'block',
                enabled INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Schedules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                days TEXT,
                enabled INTEGER DEFAULT 1,
                block_all INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                severity TEXT DEFAULT 'info',
                title TEXT NOT NULL,
                message TEXT,
                host_id INTEGER,
                acknowledged INTEGER DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (host_id) REFERENCES hosts(id)
            )
        ''')

        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        # Create default admin user (password: 123456)
        password_hash = self.hash_password("123456")
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, password_hash, email, role)
            VALUES (?, ?, ?, ?)
        ''', ('admin', password_hash, 'abdalfaqeeh@gmail.com', 'admin'))

        # Insert default blocking rules
        self.insert_default_rules(cursor)

        conn.commit()
        conn.close()
        self.logger.info("Database initialized successfully")

    def insert_default_rules(self, cursor):
        """Insert default blocking rules."""
        default_rules = [
            # Gaming
            ('Steam', 'app', 'gaming', 'steamcommunity.com', 'block'),
            ('Epic Games', 'app', 'gaming', 'epicgames.com', 'block'),
            ('Roblox', 'app', 'gaming', 'roblox.com', 'block'),
            ('Minecraft', 'app', 'gaming', 'minecraft.net', 'block'),
            ('Xbox Live', 'app', 'gaming', 'xboxlive.com', 'block'),
            ('PlayStation', 'app', 'gaming', 'playstation.net', 'block'),
            ('Nintendo', 'app', 'gaming', 'nintendo.com', 'block'),

            # Social Media
            ('Facebook', 'app', 'social', 'facebook.com', 'block'),
            ('Instagram', 'app', 'social', 'instagram.com', 'block'),
            ('TikTok', 'app', 'social', 'tiktok.com', 'block'),
            ('Snapchat', 'app', 'social', 'snapchat.com', 'block'),
            ('Twitter/X', 'app', 'social', 'twitter.com', 'block'),
            ('LinkedIn', 'app', 'social', 'linkedin.com', 'block'),

            # Streaming
            ('Netflix', 'app', 'streaming', 'netflix.com', 'block'),
            ('YouTube', 'app', 'streaming', 'youtube.com', 'block'),
            ('Disney+', 'app', 'streaming', 'disneyplus.com', 'block'),
            ('Amazon Prime', 'app', 'streaming', 'primevideo.com', 'block'),
            ('HBO Max', 'app', 'streaming', 'hbomax.com', 'block'),
            ('Spotify', 'app', 'streaming', 'spotify.com', 'block'),
        ]

        for rule in default_rules:
            cursor.execute('''
                INSERT OR IGNORE INTO rules (name, type, category, pattern, action)
                VALUES (?, ?, ?, ?, ?)
            ''', rule)

    def hash_password(self, password):
        """Hash password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_user(self, username, password):
        """Verify user credentials."""
        conn = self.get_connection()
        cursor = conn.cursor()

        password_hash = self.hash_password(password)
        cursor.execute('''
            SELECT * FROM users WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))

        user = cursor.fetchone()
        conn.close()

        if user:
            # Update last login
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (user['id'],))
            conn.commit()
            conn.close()

        return dict(user) if user else None

    def get_user(self, username):
        """Get user by username."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

    def update_user_password(self, username, new_password):
        """Update user password."""
        conn = self.get_connection()
        cursor = conn.cursor()
        password_hash = self.hash_password(new_password)
        cursor.execute('''
            UPDATE users SET password_hash = ? WHERE username = ?
        ''', (password_hash, username))
        conn.commit()
        conn.close()

    def update_user_email(self, username, email):
        """Update user email."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET email = ? WHERE username = ?
        ''', (email, username))
        conn.commit()
        conn.close()

    def add_user(self, username, password, email=None, role='user'):
        """Add new user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        password_hash = self.hash_password(password)
        cursor.execute('''
            INSERT INTO users (username, password_hash, email, role)
            VALUES (?, ?, ?, ?)
        ''', (username, password_hash, email, role))
        conn.commit()
        conn.close()

    # Host Management
    def get_hosts(self):
        """Get all hosts."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM hosts ORDER BY last_seen DESC')
        hosts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return hosts

    def get_host(self, host_id=None, mac_address=None):
        """Get host by ID or MAC."""
        conn = self.get_connection()
        cursor = conn.cursor()
        if host_id:
            cursor.execute('SELECT * FROM hosts WHERE id = ?', (host_id,))
        else:
            cursor.execute('SELECT * FROM hosts WHERE mac_address = ?', (mac_address,))
        host = cursor.fetchone()
        conn.close()
        return dict(host) if host else None

    def add_host(self, mac_address, ip_address=None, hostname=None, **kwargs):
        """Add or update host."""
        conn = self.get_connection()
        cursor = conn.cursor()

        existing = self.get_host(mac_address=mac_address)

        if existing:
            cursor.execute('''
                UPDATE hosts SET
                    ip_address = COALESCE(?, ip_address),
                    hostname = COALESCE(?, hostname),
                    last_seen = CURRENT_TIMESTAMP
                WHERE mac_address = ?
            ''', (ip_address, hostname, mac_address))
        else:
            cursor.execute('''
                INSERT INTO hosts (mac_address, ip_address, hostname, **kwargs)
                VALUES (?, ?, ?, 0, 0)
            ''', (mac_address, ip_address, hostname))

        conn.commit()
        conn.close()

        return self.get_host(mac_address=mac_address)

    def update_host(self, host_id, **kwargs):
        """Update host details."""
        allowed_fields = ['hostname', 'device_type', 'os_type', 'blocked', 'trusted', 'notes']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not updates:
            return

        conn = self.get_connection()
        cursor = conn.cursor()

        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [host_id]

        cursor.execute(f'''
            UPDATE hosts SET {set_clause} WHERE id = ?
        ''', values)

        conn.commit()
        conn.close()

    def block_host(self, host_id, blocked=True):
        """Block or unblock host."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE hosts SET blocked = ? WHERE id = ?', (1 if blocked else 0, host_id))
        conn.commit()
        conn.close()

    # Rules Management
    def get_rules(self, category=None, enabled=None):
        """Get blocking rules."""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM rules WHERE 1=1'
        params = []

        if category:
            query += ' AND category = ?'
            params.append(category)

        if enabled is not None:
            query += ' AND enabled = ?'
            params.append(enabled)

        cursor.execute(query, params)
        rules = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rules

    def add_rule(self, name, pattern, rule_type='app', category=None, action='block'):
        """Add blocking rule."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO rules (name, type, category, pattern, action)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, rule_type, category, pattern, action))
        conn.commit()
        conn.close()

    def toggle_rule(self, rule_id, enabled):
        """Enable or disable rule."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE rules SET enabled = ? WHERE id = ?', (1 if enabled else 0, rule_id))
        conn.commit()
        conn.close()

    def delete_rule(self, rule_id):
        """Delete rule."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM rules WHERE id = ?', (rule_id,))
        conn.commit()
        conn.close()

    # Schedules
    def get_schedules(self):
        """Get all schedules."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM schedules ORDER BY start_time')
        schedules = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return schedules

    def add_schedule(self, name, start_time, end_time, days=None, block_all=True):
        """Add blocking schedule."""
        days_json = json.dumps(days) if days else json.dumps([0, 1, 2, 3, 4, 5, 6])

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO schedules (name, start_time, end_time, days, block_all)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, start_time, end_time, days_json, 1 if block_all else 0))
        conn.commit()
        conn.close()

    def toggle_schedule(self, schedule_id, enabled):
        """Enable or disable schedule."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE schedules SET enabled = ? WHERE id = ?', (1 if enabled else 0, schedule_id))
        conn.commit()
        conn.close()

    def delete_schedule(self, schedule_id):
        """Delete schedule."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM schedules WHERE id = ?', (schedule_id,))
        conn.commit()
        conn.close()

    # Traffic Logging
    def log_traffic(self, host_id, bytes_sent, bytes_received, packets_sent, packets_received):
        """Log traffic data."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO traffic_logs (host_id, bytes_sent, bytes_received, packets_sent, packets_received)
            VALUES (?, ?, ?, ?, ?)
        ''', (host_id, bytes_sent, bytes_received, packets_sent, packets_received))
        conn.commit()
        conn.close()

    def get_traffic_stats(self, host_id=None, hours=24):
        """Get traffic statistics."""
        conn = self.get_connection()
        cursor = conn.cursor()

        since = datetime.now() - timedelta(hours=hours)

        if host_id:
            cursor.execute('''
                SELECT * FROM traffic_logs
                WHERE host_id = ? AND timestamp >= ?
                ORDER BY timestamp DESC
            ''', (host_id, since))
        else:
            cursor.execute('''
                SELECT * FROM traffic_logs
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            ''', (since,))

        stats = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return stats

    def get_top_consumers(self, hours=24, limit=10):
        """Get top traffic consumers."""
        conn = self.get_connection()
        cursor = conn.cursor()

        since = datetime.now() - timedelta(hours=hours)

        cursor.execute('''
            SELECT h.*, SUM(t.bytes_sent + t.bytes_received) as total_bytes
            FROM hosts h
            LEFT JOIN traffic_logs t ON h.id = t.host_id AND t.timestamp >= ?
            GROUP BY h.id
            ORDER BY total_bytes DESC
            LIMIT ?
        ''', (since, limit))

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    # Alerts
    def get_alerts(self, acknowledged=None, limit=100):
        """Get alerts."""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM alerts WHERE 1=1'
        params = []

        if acknowledged is not None:
            query += ' AND acknowledged = ?'
            params.append(acknowledged)

        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)

        cursor.execute(query, params)
        alerts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return alerts

    def add_alert(self, alert_type, title, message, severity='info', host_id=None):
        """Add new alert."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO alerts (type, title, message, severity, host_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (alert_type, title, message, severity, host_id))
        conn.commit()
        conn.close()

    def acknowledge_alert(self, alert_id):
        """Acknowledge alert."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE alerts SET acknowledged = 1 WHERE id = ?', (alert_id,))
        conn.commit()
        conn.close()

    def acknowledge_all_alerts(self):
        """Acknowledge all alerts."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE alerts SET acknowledged = 1')
        conn.commit()
        conn.close()

    # Settings
    def get_setting(self, key, default=None):
        """Get setting value."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        conn.close()

        if row:
            try:
                return json.loads(row['value'])
            except:
                return row['value']
        return default

    def set_setting(self, key, value):
        """Set setting value."""
        value_json = json.dumps(value) if not isinstance(value, str) else value

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
        ''', (key, value_json))
        conn.commit()
        conn.close()
