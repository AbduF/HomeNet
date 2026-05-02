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
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(24)
CORS(app, resources={r"/*": {"origins": "*"}})
auth = HTTPBasicAuth()

# Session configuration
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=1800
)

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'homenet.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Logging
log_handler = RotatingFileHandler(
    'homenet.log',
    maxBytes=1024 * 1024,
    backupCount=5,
    encoding='utf-8'
)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(log_handler)
logging.getLogger().setLevel(logging.ERROR)

# Basic Auth Users (Default: admin/123456)
users = {
    os.environ.get('ADMIN_USER', 'admin'): generate_password_hash(os.environ.get('ADMIN_PASSWORD', '123456'))
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

@app.before_request
def before_request():
    g.lang = request.args.get('lang', 'en')
    session.permanent = True

last_scan_time = 0

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect(DB_PATH, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    cursor = conn.cursor()

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

    # Indexes for performance
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
    """Detect active network interface (eth0, wlan0, etc.)"""
    try:
        result = subprocess.run(['ip', '-o', 'link', 'show'], capture_output=True, text=True, check=True)
        for line in result.stdout.split('\n'):
            if 'UP' in line:
                if 'eth0' in line:
                    return 'eth0'
                elif 'wlan0' in line:
                    return 'wlan0'
                elif 'enp' in line:
                    return line.split()[1].replace(':', '')
        return 'eth0'  # Default fallback
    except subprocess.CalledProcessError:
        return 'eth0'  # Default fallback

def stop_conflicting_dns_services():
    """Stop services that may conflict with dnsmasq (e.g., systemd-resolved)"""
    try:
        result = subprocess.run(['systemctl', 'list-unit-files', 'systemd-resolved.service'],
                              capture_output=True, text=True)
        if 'systemd-resolved.service' in result.stdout:
            subprocess.run(['sudo', 'systemctl', 'stop', 'systemd-resolved'], check=False)
            subprocess.run(['sudo', 'systemctl', 'disable', 'systemd-resolved'], check=False)
    except Exception as e:
        logging.warning(f"Could not stop systemd-resolved: {e}")

def get_connected_hosts():
    """Scan the local network for connected devices using arp-scan with cooldown"""
    global last_scan_time
    current_time = time.time()
    if current_time - last_scan_time < 300:  # 5-minute cooldown
        return []
    last_scan_time = current_time

    try:
        subprocess.run(['which', 'arp-scan'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        logging.error("arp-scan is not installed. Run: sudo apt install arp-scan")
        return []

    try:
        active_interface = get_active_network_interface()
        result = subprocess.run(
            ['sudo', 'arp-scan', '--interface=' + active_interface, '--localnet', '--timeout=100'],
            capture_output=True,
            text=True,
            check=True
        )
        hosts = []
        pi_ip = subprocess.run(['hostname', '-I'], capture_output=True, text=True).stdout.strip().split()[0]
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
    """Load blocklists from hardcoded defaults"""
    return {
        'social_media': ['facebook.com', 'twitter.com', 'instagram.com', 'tiktok.com', 'snapchat.com', 'linkedin.com'],
        'gaming': ['steamcommunity.com', 'xbox.com', 'playstation.com', 'epicgames.com', 'roblox.com'],
        'adult': ['pornhub.com', 'xvideos.com', 'xhamster.com']
    }

def setup_dns_blocking():
    """Set up DNS blocking using dnsmasq with optimized settings"""
    try:
        stop_conflicting_dns_services()
        subprocess.run(['which', 'dnsmasq'], check=True, stdout=subprocess.PIPE)
    except subprocess.CalledProcessError:
        try:
            subprocess.run(['sudo', 'apt', 'install', '-y', 'dnsmasq'], check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install dnsmasq: {e.stderr}")
            return False

    try:
        tmp_dir = os.path.join(os.path.dirname(__file__), 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)
        subprocess.run(['sudo', 'cp', '/etc/dnsmasq.conf', '/etc/dnsmasq.conf.bak'], check=True)

        active_interface = get_active_network_interface()
        ip = subprocess.run(['hostname', '-I'], capture_output=True, text=True).stdout.strip().split()[0]
        if not ip:
            logging.error("Could not determine IP address.")
            return False

        # Fixed dnsmasq config (no deprecated options)
        dnsmasq_conf = f"""# HomeNet DNS Configuration
no-resolv
interface={active_interface}
listen-address={ip}
bind-interfaces
server=8.8.8.8
server=8.8.4.4
cache-size=100
conf-dir=/etc/dnsmasq.d
log-queries
log-facility=/var/log/dnsmasq.log
"""
        dnsmasq_conf_path = os.path.join(tmp_dir, 'dnsmasq.conf')
        with open(dnsmasq_conf_path, 'w') as f:
            f.write(dnsmasq_conf)
        subprocess.run(['sudo', 'cp', dnsmasq_conf_path, '/etc/dnsmasq.conf'], check=True)

        os.makedirs('/etc/dnsmasq.d', exist_ok=True)
        blocklists = load_blocklists()
        blocklists_conf_path = os.path.join(tmp_dir, 'blocklists.conf')
        with open(blocklists_conf_path, 'w') as f:
            for category, domains in blocklists.items():
                for domain in domains:
                    f.write(f"address=/{domain}/0.0.0.0\n")
        subprocess.run(['sudo', 'cp', blocklists_conf_path, '/etc/dnsmasq.d/blocklists.conf'], check=True)

        subprocess.run(['sudo', 'systemctl', 'restart', 'dnsmasq'], check=True)
        time.sleep(2)
        status = subprocess.run(['sudo', 'systemctl', 'is-active', 'dnsmasq'], capture_output=True, text=True)
        if status.stdout.strip() != 'active':
            logs = subprocess.run(['sudo', 'journalctl', '-xeu', 'dnsmasq.service'], capture_output=True, text=True)
            logging.error(f"dnsmasq failed to start. Logs: {logs.stderr}")
            return False

        subprocess.run(['sudo', 'systemctl', 'enable', 'dnsmasq'], check=True)
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"DNS setup failed: {e.stderr}")
        return False

def setup_firewall():
    """Set up time-based firewall rules with optimized iptables"""
    try:
        if os.geteuid() != 0:
            logging.error("Firewall setup requires root privileges.")
            return False

        subprocess.run(['iptables', '-F'], check=True)
        subprocess.run(['iptables', '-X'], check=True)
        subprocess.run(['iptables', '-A', 'INPUT', '-i', 'lo', '-j', 'ACCEPT'], check=True)
        subprocess.run(['iptables', '-A', 'OUTPUT', '-o', 'lo', '-j', 'ACCEPT'], check=True)
        subprocess.run(['iptables', '-A', 'INPUT', '-m', 'conntrack', '--ctstate', 'ESTABLISHED,RELATED', '-j', 'ACCEPT'], check=True)
        subprocess.run(['iptables', '-A', 'OUTPUT', '-m', 'conntrack', '--ctstate', 'ESTABLISHED,RELATED', '-j', 'ACCEPT'], check=True)
        subprocess.run(['iptables', '-A', 'OUTPUT', '-p', 'udp', '--dport', '53', '-j', 'ACCEPT'], check=True)
        subprocess.run(['iptables', '-A', 'OUTPUT', '-p', 'tcp', '--dport', '53', '-j', 'ACCEPT'], check=True)
        subprocess.run(['iptables', '-A', 'OUTPUT', '-p', 'tcp', '--dport', '80', '-j', 'ACCEPT'], check=True)
        subprocess.run(['iptables', '-A', 'OUTPUT', '-p', 'tcp', '--dport', '443', '-j', 'ACCEPT'], check=True)
        subprocess.run(['iptables', '-A', 'OUTPUT', '-p', 'icmp', '-j', 'ACCEPT'], check=True)
        subprocess.run(['iptables', '-A', 'OUTPUT', '-d', '192.168.0.0/16', '-j', 'ACCEPT'], check=True)
        subprocess.run(['iptables', '-A', 'OUTPUT', '-d', '10.0.0.0/8', '-j', 'ACCEPT'], check=True)
        subprocess.run(['iptables', '-A', 'OUTPUT', '-d', '172.16.0.0/12', '-j', 'ACCEPT'], check=True)
        subprocess.run(['iptables', '-A', 'OUTPUT', '-m', 'time', '--timestart', '22:00', '--timestop', '00:00', '-j', 'DROP'], check=True)
        subprocess.run(['iptables', '-A', 'OUTPUT', '-m', 'time', '--timestart', '22:00', '--timestop', '00:00', '-j', 'LOG', '--log-prefix', 'HOMENET BLOCKED: '], check=True)

        try:
            subprocess.run(['apt', 'install', '-y', 'iptables-persistent'], check=True)
            subprocess.run(['netfilter-persistent', 'save'], check=True)
        except subprocess.CalledProcessError as e:
            logging.warning(f"Could not save iptables rules permanently: {e.stderr}")

        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Firewall setup failed: {e.stderr}")
        return False

# --- Routes ---
@app.route('/')
@auth.login_required
def dashboard():
    hosts = db_query("SELECT * FROM hosts ORDER BY last_seen DESC LIMIT 100")
    traffic = db_query('''
        SELECT h.ip, h.hostname, t.timestamp, t.bytes_sent, t.bytes_received
        FROM traffic t
        JOIN hosts h ON t.host_id = h.id
        ORDER BY t.timestamp DESC
        LIMIT 100
    ''')
    alerts = db_query('''
        SELECT a.id, a.alert_type, a.message, a.timestamp, h.ip, h.hostname
        FROM alerts a
        JOIN hosts h ON a.host_id = h.id
        ORDER BY a.timestamp DESC
        LIMIT 100
    ''')
    dns_blocks = db_query('''
        SELECT d.domain, d.timestamp, h.ip, h.hostname
        FROM dns_blocks d
        JOIN hosts h ON d.host_id = h.id
        ORDER BY d.timestamp DESC
        LIMIT 100
    ''')
    return render_template(
        'index.html',
        translations=translations.translations[g.lang],
        hosts=hosts,
        traffic=traffic,
        alerts=alerts,
        dns_blocks=dns_blocks
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not hasattr(g, 'login_attempts'):
            g.login_attempts = 0
        g.login_attempts += 1
        if g.login_attempts > 5:
            return render_template('login.html', translations=translations.translations[g.lang], error=translations.translations[g.lang]['too_many_attempts'])

        if username in users and check_password_hash(users[username], password):
            session['logged_in'] = True
            session['username'] = username
            session['login_attempts'] = 0
            return redirect(url_for('dashboard'))
        return render_template('login.html', translations=translations.translations[g.lang], error=translations.translations[g.lang]['login_error'])
    return render_template('login.html', translations=translations.translations[g.lang])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/hosts')
@auth.login_required
def get_hosts():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 50
        offset = (page - 1) * per_page
        hosts = db_query(f"SELECT * FROM hosts ORDER BY last_seen DESC LIMIT {per_page} OFFSET {offset}")
        return jsonify([dict(host) for host in hosts])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/traffic')
@auth.login_required
def get_traffic():
    try:
        limit = request.args.get('limit', 100, type=int)
        traffic = db_query(f'''
            SELECT h.ip, h.hostname, t.timestamp, t.bytes_sent, t.bytes_received
            FROM traffic t
            JOIN hosts h ON t.host_id = h.id
            ORDER BY t.timestamp DESC
            LIMIT {limit}
        ''')
        return jsonify([dict(row) for row in traffic])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan_hosts', methods=['POST'])
@auth.login_required
def scan_hosts():
    try:
        hosts = get_connected_hosts()
        for host in hosts:
            existing_host = db_query(
                "SELECT id FROM hosts WHERE ip = ? OR mac = ?",
                (host['ip'], host['mac']),
                one=True
            )
            if not existing_host:
                db_query(
                    "INSERT INTO hosts (ip, mac, hostname, os, first_seen, last_seen) VALUES (?, ?, ?, ?, ?, ?)",
                    (host['ip'], host['mac'], host.get('hostname', ''), host.get('os', ''), datetime.now().isoformat(), datetime.now().isoformat())
                )
                new_host_id = db_query("SELECT id FROM hosts WHERE ip = ?", (host['ip'],), one=True)['id']
                db_query(
                    "INSERT INTO alerts (host_id, alert_type, message, timestamp) VALUES (?, ?, ?, ?)",
                    (new_host_id, 'new_host', f"New host detected: {host['ip']}", datetime.now().isoformat())
                )
        return jsonify({'message': f"Found {len(hosts)} hosts"}), 200
    except Exception as e:
        logging.error(f"Error in scan_hosts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/setup', methods=['POST'])
@auth.login_required
def api_setup():
    try:
        dns_success = setup_dns_blocking()
        firewall_success = setup_firewall()
        message = translations.translations[g.lang]['setup_success'] if (dns_success and firewall_success) else translations.translations[g.lang]['setup_failed']
        return jsonify({
            'dns': 'success' if dns_success else 'failed',
            'firewall': 'success' if firewall_success else 'failed',
            'message': message
        }), 200 if (dns_success and firewall_success) else 500
    except Exception as e:
        logging.error(f"Error in api_setup: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/speedtest')
@auth.login_required
def speedtest():
    try:
        # Test availability (ping Google DNS)
        subprocess.run(['ping', '-c', '1', '8.8.8.8'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Test download speed (using speedtest-cli)
        try:
            result = subprocess.run(['speedtest-cli', '--simple', '--timeout=10'],
                                  capture_output=True, text=True, check=True, timeout=15)
            speed_data = {}
            for line in result.stdout.split('\n'):
                if ':' in line:
                    key, value = line.split(':')
                    speed_data[key.strip()] = f"{value.strip()} Mbps"
            return jsonify({
                'status': 'online',
                'speed': speed_data,
                'message': translations.translations[g.lang]['internet_online']
            }), 200
        except FileNotFoundError:
            return jsonify({
                'status': 'online',
                'speed': None,
                'message': translations.translations[g.lang]['internet_online_no_speedtest']
            }), 200
        except subprocess.TimeoutExpired:
            return jsonify({
                'status': 'online',
                'speed': None,
                'message': translations.translations[g.lang]['internet_online_no_speedtest']
            }), 200
    except subprocess.CalledProcessError:
        return jsonify({
            'status': 'offline',
            'speed': None,
            'message': translations.translations[g.lang]['internet_offline']
        }), 503

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

# Static files
app.static_folder = 'static'
app.static_url_path = '/static'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)