"""
HomeNet - Parental Network Controller
Fixed app.py for Raspberry Pi 3 compatibility
Bugs fixed:
  1. SESSION_COOKIE_SECURE=True breaks non-HTTPS login → set dynamically
  2. DB_PATH os.makedirs fails when dirname is '' → guarded
  3. Login route uses session but dashboard uses HTTPBasicAuth → unified to session auth
  4. os.makedirs('/etc/dnsmasq.d') fails without sudo → wrapped
  5. get_connected_hosts rate-limit uses global mutable state → thread-safe
  6. iptables -A time rules wrong order (LOG before DROP) → fixed
  7. filesizeformat filter missing in Jinja2 → added custom filter
"""

import sqlite3
import subprocess
import os
import re
import time
import logging
import threading
from logging.handlers import RotatingFileHandler
from functools import wraps
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request, abort, g, session, redirect, url_for
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import translations
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(24)
CORS(app, resources={r"/*": {"origins": "*"}})

# ── Session security: only enforce Secure cookie over HTTPS ──────────────────
# On a local Raspberry Pi without TLS, SESSION_COOKIE_SECURE=True
# causes Flask to never send the cookie → login always fails.
_is_https = os.environ.get('HTTPS_ENABLED', 'false').lower() == 'true'
app.config.update(
    SESSION_COOKIE_SECURE=_is_https,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=1800
)

# ── Database ─────────────────────────────────────────────────────────────────
_db_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_db_dir, 'homenet.db')

# ── Logging ──────────────────────────────────────────────────────────────────
log_handler = RotatingFileHandler(
    'homenet.log', maxBytes=1024 * 1024, backupCount=5, encoding='utf-8'
)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(log_handler)
logging.getLogger().setLevel(logging.ERROR)

# ── Users ─────────────────────────────────────────────────────────────────────
ADMIN_USER = os.environ.get('ADMIN_USER', 'admin')
ADMIN_PASS = os.environ.get('ADMIN_PASSWORD', '123456')
users = {
    ADMIN_USER: generate_password_hash(ADMIN_PASS)
}

# ── Jinja custom filter: human-readable file sizes ───────────────────────────
def filesizeformat(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return '0 B'
    for unit in ['B', 'KB', 'MB', 'GB']:
        if value < 1024:
            return f'{value:.1f} {unit}'
        value /= 1024
    return f'{value:.1f} TB'

app.jinja_env.filters['filesizeformat'] = filesizeformat

# ── Auth decorator (session-based) ───────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            # API routes return 401; HTML routes redirect to login
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Unauthorized'}), 401
            return redirect(url_for('login', lang=request.args.get('lang', 'en')))
        return f(*args, **kwargs)
    return decorated

@app.before_request
def before_request():
    g.lang = request.args.get('lang', session.get('lang', 'en'))
    session['lang'] = g.lang
    session.permanent = True

# ── Database Setup ────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS hosts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL UNIQUE,
            mac TEXT NOT NULL,
            hostname TEXT,
            os TEXT,
            first_seen TEXT,
            last_seen TEXT
        );
        CREATE TABLE IF NOT EXISTS traffic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            host_id INTEGER,
            timestamp TEXT,
            bytes_sent INTEGER,
            bytes_received INTEGER,
            FOREIGN KEY (host_id) REFERENCES hosts (id)
        );
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            host_id INTEGER,
            alert_type TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT,
            FOREIGN KEY (host_id) REFERENCES hosts (id)
        );
        CREATE TABLE IF NOT EXISTS dns_blocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT NOT NULL,
            timestamp TEXT,
            host_id INTEGER,
            FOREIGN KEY (host_id) REFERENCES hosts (id)
        );
        CREATE INDEX IF NOT EXISTS idx_hosts_ip ON hosts(ip);
        CREATE INDEX IF NOT EXISTS idx_hosts_mac ON hosts(mac);
        CREATE INDEX IF NOT EXISTS idx_traffic_host_id ON traffic(host_id);
        CREATE INDEX IF NOT EXISTS idx_traffic_timestamp ON traffic(timestamp);
        CREATE INDEX IF NOT EXISTS idx_alerts_host_id ON alerts(host_id);
        CREATE INDEX IF NOT EXISTS idx_dns_blocks_domain ON dns_blocks(domain);
    ''')
    conn.commit()
    conn.close()

init_db()

# ── Helper Functions ──────────────────────────────────────────────────────────
def db_query(query, args=(), one=False):
    conn = sqlite3.connect(DB_PATH, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def is_valid_ip(ip):
    try:
        import ipaddress
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def is_valid_mac(mac):
    return re.match(r'^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$', mac) is not None

def get_active_network_interface():
    try:
        result = subprocess.run(['ip', '-o', 'link', 'show'], capture_output=True, text=True, check=True)
        for line in result.stdout.split('\n'):
            if 'UP' in line:
                if 'eth0' in line:
                    return 'eth0'
                elif 'wlan0' in line:
                    return 'wlan0'
        return None
    except subprocess.CalledProcessError:
        return None

def stop_conflicting_dns_services():
    try:
        subprocess.run(['sudo', 'systemctl', 'stop', 'systemd-resolved'], check=False,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(['sudo', 'systemctl', 'disable', 'systemd-resolved'], check=False,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        logging.warning(f"Could not stop systemd-resolved: {e}")

# Thread-safe scan rate limiter
_scan_lock = threading.Lock()
_last_scan_time = 0

def get_connected_hosts():
    global _last_scan_time
    with _scan_lock:
        current_time = time.time()
        if current_time - _last_scan_time < 300:
            return []
        _last_scan_time = current_time

    try:
        subprocess.run(['which', 'arp-scan'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        logging.error("arp-scan not installed. Run: sudo apt install arp-scan")
        return []

    try:
        active_interface = get_active_network_interface()
        if not active_interface:
            logging.error("No active network interface found (eth0 or wlan0).")
            return []

        result = subprocess.run(
            ['sudo', 'arp-scan', f'--interface={active_interface}', '--localnet', '--timeout=100'],
            capture_output=True, text=True, check=True
        )

        pi_ip = subprocess.run(['hostname', '-I'], capture_output=True, text=True).stdout.strip().split()
        pi_ip = pi_ip[0] if pi_ip else ''

        hosts = []
        for line in result.stdout.split('\n'):
            if ':' in line and '.' in line and 'Starting' not in line and 'Interface' not in line:
                parts = line.split()
                if len(parts) >= 2:
                    ip, mac = parts[0], parts[1]
                    if ip != pi_ip and is_valid_ip(ip) and is_valid_mac(mac):
                        hosts.append({'ip': ip, 'mac': mac, 'hostname': '', 'os': ''})
        return hosts
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running arp-scan: {e.stderr}")
        return []

def load_blocklists():
    return {
        'social_media': ['facebook.com', 'twitter.com', 'instagram.com', 'tiktok.com',
                         'snapchat.com', 'linkedin.com'],
        'gaming': ['steamcommunity.com', 'xbox.com', 'playstation.com', 'epicgames.com', 'roblox.com'],
        'adult': ['pornhub.com', 'xvideos.com', 'xhamster.com']
    }

def setup_dns_blocking():
    try:
        subprocess.run(['which', 'dnsmasq'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        try:
            subprocess.run(['sudo', 'apt', 'install', '-y', 'dnsmasq'], check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install dnsmasq: {e.stderr}")
            return False

    try:
        stop_conflicting_dns_services()

        tmp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)

        subprocess.run(['sudo', 'cp', '/etc/dnsmasq.conf', '/etc/dnsmasq.conf.bak'],
                       check=False, stderr=subprocess.PIPE)

        active_interface = get_active_network_interface()
        if not active_interface:
            logging.error("No active network interface found.")
            return False

        ip_result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        ip_parts = ip_result.stdout.strip().split()
        if not ip_parts:
            logging.error("Could not determine IP address.")
            return False
        ip = ip_parts[0]

        dnsmasq_conf = f"""# HomeNet DNS Configuration
no-resolv
no-poll
interface={active_interface}
listen-address={ip}
bind-interfaces
server=1.1.1.1
server=1.0.0.1
cache-size=100
dnssec-validation=no
conf-dir=/etc/dnsmasq.d
log-queries
log-facility=/var/log/dnsmasq.log
"""
        conf_path = os.path.join(tmp_dir, 'dnsmasq.conf')
        with open(conf_path, 'w') as f:
            f.write(dnsmasq_conf)
        subprocess.run(['sudo', 'cp', conf_path, '/etc/dnsmasq.conf'], check=True)

        # Create /etc/dnsmasq.d if missing (needs sudo on Pi)
        subprocess.run(['sudo', 'mkdir', '-p', '/etc/dnsmasq.d'],
                       check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        blocklist_path = os.path.join(tmp_dir, 'blocklists.conf')
        with open(blocklist_path, 'w') as f:
            for category, domains in load_blocklists().items():
                for domain in domains:
                    f.write(f"address=/{domain}/0.0.0.0\n")
        subprocess.run(['sudo', 'cp', blocklist_path, '/etc/dnsmasq.d/blocklists.conf'], check=True)

        subprocess.run(['sudo', 'systemctl', 'restart', 'dnsmasq'], check=True)
        time.sleep(2)

        status = subprocess.run(['sudo', 'systemctl', 'is-active', 'dnsmasq'],
                                capture_output=True, text=True)
        if status.stdout.strip() != 'active':
            logging.error("dnsmasq failed to start. Check: journalctl -xeu dnsmasq.service")
            return False

        subprocess.run(['sudo', 'systemctl', 'enable', 'dnsmasq'], check=True)
        return True

    except subprocess.CalledProcessError as e:
        logging.error(f"DNS setup failed: {e.stderr}")
        return False

def setup_firewall():
    try:
        if os.geteuid() != 0:
            logging.error("Firewall setup requires root privileges.")
            return False

        # Flush existing rules
        for cmd in [['iptables', '-F'], ['iptables', '-X']]:
            subprocess.run(cmd, check=True)

        rules = [
            # Loopback
            ['iptables', '-A', 'INPUT',  '-i', 'lo', '-j', 'ACCEPT'],
            ['iptables', '-A', 'OUTPUT', '-o', 'lo', '-j', 'ACCEPT'],
            # Established
            ['iptables', '-A', 'INPUT',  '-m', 'conntrack', '--ctstate', 'ESTABLISHED,RELATED', '-j', 'ACCEPT'],
            ['iptables', '-A', 'OUTPUT', '-m', 'conntrack', '--ctstate', 'ESTABLISHED,RELATED', '-j', 'ACCEPT'],
            # DNS
            ['iptables', '-A', 'OUTPUT', '-p', 'udp', '--dport', '53', '-j', 'ACCEPT'],
            ['iptables', '-A', 'OUTPUT', '-p', 'tcp', '--dport', '53', '-j', 'ACCEPT'],
            # HTTP/HTTPS
            ['iptables', '-A', 'OUTPUT', '-p', 'tcp', '--dport', '80',  '-j', 'ACCEPT'],
            ['iptables', '-A', 'OUTPUT', '-p', 'tcp', '--dport', '443', '-j', 'ACCEPT'],
            # ICMP
            ['iptables', '-A', 'OUTPUT', '-p', 'icmp', '-j', 'ACCEPT'],
            # LAN
            ['iptables', '-A', 'OUTPUT', '-d', '192.168.0.0/16', '-j', 'ACCEPT'],
            ['iptables', '-A', 'OUTPUT', '-d', '10.0.0.0/8',     '-j', 'ACCEPT'],
            ['iptables', '-A', 'OUTPUT', '-d', '172.16.0.0/12',  '-j', 'ACCEPT'],
            # Time-based block: LOG first (for dmesg), then DROP
            # Note: xt_time uses UTC by default on Raspberry Pi — 22:00 UTC
            ['iptables', '-A', 'OUTPUT', '-m', 'time',
             '--timestart', '22:00', '--timestop', '00:00',
             '-j', 'LOG', '--log-prefix', 'HOMENET BLOCKED: '],
            ['iptables', '-A', 'OUTPUT', '-m', 'time',
             '--timestart', '22:00', '--timestop', '00:00',
             '-j', 'DROP'],
        ]
        for rule in rules:
            subprocess.run(rule, check=True)

        # Persist rules
        try:
            subprocess.run(['which', 'netfilter-persistent'], check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(['netfilter-persistent', 'save'], check=True)
        except subprocess.CalledProcessError:
            logging.warning("netfilter-persistent not found. Rules may not survive reboot.")
            logging.warning("Install with: sudo apt install iptables-persistent")

        return True

    except subprocess.CalledProcessError as e:
        logging.error(f"Firewall setup failed: {e.stderr}")
        return False

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route('/')
@login_required
def dashboard():
    hosts = db_query("SELECT * FROM hosts ORDER BY last_seen DESC LIMIT 100")
    traffic = db_query('''
        SELECT h.ip, h.hostname, t.timestamp, t.bytes_sent, t.bytes_received
        FROM traffic t
        JOIN hosts h ON t.host_id = h.id
        ORDER BY t.timestamp DESC LIMIT 100
    ''')
    alerts = db_query('''
        SELECT a.id, a.alert_type, a.message, a.timestamp, h.ip, h.hostname
        FROM alerts a
        JOIN hosts h ON a.host_id = h.id
        ORDER BY a.timestamp DESC LIMIT 100
    ''')
    dns_blocks = db_query('''
        SELECT d.domain, d.timestamp, h.ip, h.hostname
        FROM dns_blocks d
        JOIN hosts h ON d.host_id = h.id
        ORDER BY d.timestamp DESC LIMIT 100
    ''')
    return render_template(
        'index.html',
        translations=translations.translations[g.lang],
        g=g,
        hosts=hosts,
        traffic=traffic,
        alerts=alerts,
        dns_blocks=dns_blocks
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # Simple brute-force guard using session (resets per session)
        attempts = session.get('login_attempts', 0)
        if attempts >= 5:
            error = translations.translations[g.lang].get('too_many_attempts',
                                                          'Too many attempts. Try again later.')
        elif username in users and check_password_hash(users[username], password):
            session.clear()
            session['logged_in'] = True
            session['username'] = username
            session['login_attempts'] = 0
            return redirect(url_for('dashboard', lang=g.lang))
        else:
            session['login_attempts'] = attempts + 1
            error = translations.translations[g.lang].get('login_error',
                                                          'Invalid username or password')

    return render_template(
        'login.html',
        translations=translations.translations[g.lang],
        g=g,
        error=error
    )

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ── API Routes ─────────────────────────────────────────────────────────────────
@app.route('/api/hosts')
@login_required
def get_hosts():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 50
        offset = (page - 1) * per_page
        hosts = db_query(
            "SELECT * FROM hosts ORDER BY last_seen DESC LIMIT ? OFFSET ?",
            (per_page, offset)
        )
        return jsonify([dict(h) for h in hosts])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/traffic')
@login_required
def get_traffic():
    try:
        limit = min(request.args.get('limit', 100, type=int), 500)
        traffic = db_query('''
            SELECT h.ip, h.hostname, t.timestamp, t.bytes_sent, t.bytes_received
            FROM traffic t
            JOIN hosts h ON t.host_id = h.id
            ORDER BY t.timestamp DESC LIMIT ?
        ''', (limit,))
        return jsonify([dict(r) for r in traffic])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts')
@login_required
def get_alerts():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 50
        offset = (page - 1) * per_page
        alerts = db_query('''
            SELECT a.id, a.alert_type, a.message, a.timestamp, h.ip, h.hostname
            FROM alerts a
            JOIN hosts h ON a.host_id = h.id
            ORDER BY a.timestamp DESC LIMIT ? OFFSET ?
        ''', (per_page, offset))
        return jsonify([dict(a) for a in alerts])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dns_blocks')
@login_required
def get_dns_blocks():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 50
        offset = (page - 1) * per_page
        blocks = db_query('''
            SELECT d.domain, d.timestamp, h.ip, h.hostname
            FROM dns_blocks d
            JOIN hosts h ON d.host_id = h.id
            ORDER BY d.timestamp DESC LIMIT ? OFFSET ?
        ''', (per_page, offset))
        return jsonify([dict(b) for b in blocks])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan_hosts', methods=['POST'])
@login_required
def scan_hosts():
    try:
        hosts = get_connected_hosts()
        new_count = 0
        for host in hosts:
            existing = db_query(
                "SELECT id FROM hosts WHERE ip = ? OR mac = ?",
                (host['ip'], host['mac']), one=True
            )
            now = datetime.now().isoformat()
            if not existing:
                db_query(
                    "INSERT INTO hosts (ip, mac, hostname, os, first_seen, last_seen) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (host['ip'], host['mac'], host.get('hostname', ''),
                     host.get('os', ''), now, now)
                )
                new_host = db_query("SELECT id FROM hosts WHERE ip = ?", (host['ip'],), one=True)
                if new_host:
                    db_query(
                        "INSERT INTO alerts (host_id, alert_type, message, timestamp) "
                        "VALUES (?, ?, ?, ?)",
                        (new_host['id'], 'new_host', f"New host detected: {host['ip']}", now)
                    )
                new_count += 1
            else:
                # Update last_seen
                db_query("UPDATE hosts SET last_seen = ? WHERE ip = ?", (now, host['ip']))

        return jsonify({'message': f"Scan complete: {len(hosts)} hosts found, {new_count} new"}), 200
    except Exception as e:
        logging.error(f"Error in scan_hosts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/setup', methods=['POST'])
@login_required
def api_setup():
    try:
        dns_success = setup_dns_blocking()
        firewall_success = setup_firewall()
        ok = dns_success and firewall_success
        lang = g.lang
        message = (translations.translations[lang].get('setup_success', 'Setup complete!')
                   if ok else
                   translations.translations[lang].get('setup_failed', 'Setup failed. Check logs.'))
        return jsonify({
            'dns':      'success' if dns_success else 'failed',
            'firewall': 'success' if firewall_success else 'failed',
            'message':  message
        }), 200 if ok else 500
    except Exception as e:
        logging.error(f"Error in api_setup: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/speedtest')
@login_required
def speedtest():
    try:
        subprocess.run(['ping', '-c', '1', '-W', '3', '8.8.8.8'],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        return jsonify({
            'status': 'offline',
            'speed': None,
            'message': translations.translations[g.lang].get('internet_offline', 'Internet offline')
        }), 503

    try:
        result = subprocess.run(['speedtest-cli', '--simple'],
                                capture_output=True, text=True, check=True, timeout=60)
        speed_data = {}
        for line in result.stdout.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                speed_data[key.strip()] = value.strip()
        return jsonify({
            'status': 'online',
            'speed': speed_data,
            'message': translations.translations[g.lang].get('internet_online', 'Internet online')
        })
    except FileNotFoundError:
        return jsonify({
            'status': 'online',
            'speed': None,
            'message': translations.translations[g.lang].get('internet_online_no_speedtest',
                                                             'Online (speedtest-cli not installed)')
        })
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return jsonify({
            'status': 'online',
            'speed': None,
            'message': 'Online (speed test timed out)'
        })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

# ── Static files ───────────────────────────────────────────────────────────────
app.static_folder = 'static'
app.static_url_path = '/static'

if __name__ == '__main__':
    # debug=False is important for production on Pi
    # threaded=True allows concurrent requests (scan + dashboard)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
