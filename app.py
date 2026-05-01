import sqlite3
import subprocess
import os
import re
import time
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request, abort, g, session, redirect, url_for
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import translations

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(24)  # Random secret key if not set
CORS(app, resources={r"/*": {"origins": "*"}})
auth = HTTPBasicAuth()

# Session configuration for security
app.config.update(
    SESSION_COOKIE_SECURE=True,      # Only send cookies over HTTPS
    SESSION_COOKIE_HTTPONLY=True,     # Prevent JavaScript cookie access
    SESSION_COOKIE_SAMESITE='Lax',    # CSRF protection
    PERMANENT_SESSION_LIFETIME=1800   # 30-minute session timeout
)

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'homenet.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Logging configuration (errors only for performance)
log_handler = RotatingFileHandler(
    'homenet.log',
    maxBytes=1024 * 1024,  # 1 MB
    backupCount=5,
    encoding='utf-8'
)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(log_handler)
logging.getLogger().setLevel(logging.ERROR)  # Only log errors in production

# Basic Auth Users (from environment variables)
users = {
    os.environ.get('ADMIN_USER', 'admin'): generate_password_hash(os.environ.get('ADMIN_PASSWORD', os.urandom(12).hex()))
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

@app.before_request
def before_request():
    g.lang = request.args.get('lang', 'en')
    session.permanent = True

last_scan_time = 0  # Cooldown for host scanning

# --- Database Setup (Optimized for SQLite WAL Mode) ---
def init_db():
    """Initialize the SQLite database with WAL mode for better performance."""
    conn = sqlite3.connect(DB_PATH, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hosts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL UNIQUE,
            mac TEXT NOT NULL,
            hostname TEXT,
            os TEXT,
            first_seen TEXT,
            last_seen TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS traffic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            host_id INTEGER,
            timestamp TEXT,
            bytes_sent INTEGER,
            bytes_received INTEGER,
            FOREIGN KEY (host_id) REFERENCES hosts (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            host_id INTEGER,
            alert_type TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT,
            FOREIGN KEY (host_id) REFERENCES hosts (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dns_blocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT NOT NULL,
            timestamp TEXT,
            host_id INTEGER,
            FOREIGN KEY (host_id) REFERENCES hosts (id)
        )
    ''')

    # Add indexes for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hosts_ip ON hosts(ip)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hosts_mac ON hosts(mac)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_traffic_host_id ON traffic(host_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_traffic_timestamp ON traffic(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_host_id ON alerts(host_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_dns_blocks_domain ON dns_blocks(domain)")

    conn.commit()
    conn.close()

init_db()

# --- Helper Functions ---
def db_query(query, args=(), one=False):
    """Execute a database query with WAL mode and parameterized queries."""
    conn = sqlite3.connect(DB_PATH, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def is_valid_ip(ip)