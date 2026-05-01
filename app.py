
from flask import Flask, render_template, jsonify, request, abort
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import subprocess
import os
import re
from datetime import datetime, timedelta
import logging

# Initialize Flask app
app = Flask(__name__)
CORS(app)
auth = HTTPBasicAuth()

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
DB_PATH = os.path.join(os.path.dirname(__file__), 'homenet.db')

# Logging
logging.basicConfig(
    filename='homenet.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Basic Auth Users (CHANGE THIS IN PRODUCTION!)
users = {
    "admin": generate_password_hash("securepassword123")
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

# --- Database Setup ---
def init_db():
    """Initialize the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
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
            alert_type TEXT,
            message TEXT,
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
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_traffic_host_id ON traffic(host_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_traffic_timestamp ON traffic(timestamp)")
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# --- Helper Functions ---
def db_query(query, args=(), one=False):
    """Execute a database query."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def is_valid_ip(ip):
    """Validate an IP address."""
    try:
        import ipaddress
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def is_valid_mac(mac):
    """Validate a MAC address."""
    return re.match(r'^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$', mac) is not None

def get_connected_hosts():
    """Scan the local network for connected devices."""
    try:
        # Check if arp-scan is installed
        subprocess.run(['which', 'arp-scan'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        logging.error("arp-scan is not installed. Run: sudo apt install arp-scan")
        return []

    try:
        result = subprocess.run(['arp-scan', '--localnet'], capture_output=True, text=True, check=True)
        hosts = []
        for line in result.stdout.split('\n'):
            if ':' in line and '.' in line and 'Starting' not in line and 'Interface' not in line:
                parts = line.split()
                if len(parts) >= 2:
                    ip = parts[0]
                    mac = parts[1]
                    hosts.append({'ip': ip, 'mac': mac, 'hostname': '', 'os': ''})
        return hosts
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running arp-scan: {e}")
        return []

def load_blocklists():
    """Load blocklists from hardcoded defaults (can be extended to files later)."""
    return {
        'social_media': [
            'facebook.com', 'twitter.com', 'instagram.com', 'tiktok.com',
            'snapchat.com', 'linkedin.com', 'pinterest.com', 'reddit.com'
        ],
        'gaming': [
            'steamcommunity.com', 'xbox.com', 'playstation.com', 'nintendo.com',
            'epicgames.com', 'origin.com', 'blizzard.com', 'roblox.com'
        ],
        'adult': [
            'pornhub.com', 'xvideos.com', 'xhamster.com', 'youporn.com'
        ]
    }

def setup_dns_blocking():
    """Set up DNS blocking using dnsmasq."""
    try:
        # Check if dnsmasq is installed
        subprocess.run(['which', 'dnsmasq'], check=True, stdout=subprocess.PIPE)
    except subprocess.CalledProcessError:
        logging.info("Installing dnsmasq...")
        try:
            subprocess.run(['sudo', 'apt', 'install', '-y', 'dnsmasq'], check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install dnsmasq: {e}")
            return False

    try:
        # Backup original config
        subprocess.run(['sudo', 'cp', '/etc/dnsmasq.conf', '/etc/dnsmasq.conf.bak'], check=True)

        # Get the server's IP
        ip = subprocess.run(['hostname', '-I'], capture_output=True, text=True).stdout.strip().split()[0]
        if not ip:
            logging.error("Could not determine IP address.")
            return False

        # Configure dnsmasq
        dnsmasq_conf = f"""# HomeNet DNS Configuration
interface=eth0
listen-address={ip}
bind-interfaces

# Forward DNS queries to Google DNS
server=8.8.8.8
server=8.8.4.4

# Block lists
conf-dir=/etc/dnsmasq.d

# Log queries
log-queries
log-dhcp
log-facility=/var/log/dnsmasq.log
"""
        with open('/tmp/dnsmasq.conf', 'w') as f:
            f.write(dnsmasq_conf)
        subprocess.run(['sudo', 'cp', '/tmp/dnsmasq.conf', '/etc/dnsmasq.conf'], check=True)

        # Create blocklist directory
        subprocess.run(['sudo', 'mkdir', '-p', '/etc/dnsmasq.d'], check=True)

        # Add blocklists
        blocklists = load_blocklists()
        with open('/tmp/blocklists.conf', 'w') as f:
            for category, domains in blocklists.items():
                for domain in domains:
                    f.write(f"address=/{domain}/0.0.0.0\n")

        subprocess.run(['sudo', 'cp', '/tmp/blocklists.conf', '/etc/dnsmasq.d/blocklists.conf'], check=True)

        # Restart dnsmasq
        subprocess.run(['sudo', 'systemctl', 'restart', 'dnsmasq'], check=True)
        subprocess.run(['sudo', 'systemctl', 'enable', 'dnsmasq'], check=True)

        logging.info("DNS blocking setup completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"DNS setup failed: {e}")
        return False

def setup_firewall():
    """Set up time-based firewall rules (block after 10 PM)."""
    try:
        # Check for root
        if os.geteuid() != 0:
            logging.error("Firewall setup requires root privileges.")
            return False

        # Flush existing rules
        subprocess.run(['sudo', 'iptables', '-F'], check=True)
        subprocess.run(['sudo', 'iptables', '-X'], check=True)

        # Allow loopback and established connections
        subprocess.run(['sudo', 'iptables', '-A', 'INPUT', '-i', 'lo', '-j', 'ACCEPT'], check=True)
        subprocess.run(['sudo', 'iptables', '-A', 'OUTPUT', '-o', 'lo', '-j', 'ACCEPT'], check=True)
        subprocess.run(['sudo', 'iptables', '-A', 'INPUT', '-m', 'conntrack', '--ctstate', 'ESTABLISHED,RELATED', '-j', 'ACCEPT'], check=True)
        subprocess.run(['sudo', 'iptables', '-A', 'OUTPUT', '-m', 'conntrack', '--ctstate', 'ESTABLISHED,RELATED', '-j', 'ACCEPT'], check=True)

        # Allow DNS, HTTP, HTTPS, ICMP
        subprocess.run(['sudo', 'iptables', '-A', 'OUTPUT', '-p', 'udp', '--dport', '53', '-j', 'ACCEPT'], check=True)
        subprocess.run(['sudo', 'iptables', '-A', 'OUTPUT', '-p', 'tcp', '--dport', '53', '-j', 'ACCEPT'], check=True)
        subprocess.run(['sudo', 'iptables', '-A', 'OUTPUT', '-p', 'tcp', '--dport', '80', '-j', 'ACCEPT'], check=True)
        subprocess.run(['sudo', 'iptables', '-A', 'OUTPUT', '-p', 'tcp', '--dport', '443', '-j', 'ACCEPT'], check=True)
        subprocess.run(['sudo', 'iptables', '-A', 'OUTPUT', '-p', 'icmp', '-j', 'ACCEPT'], check=True)

        # Allow local network traffic
        subprocess.run(['sudo', 'iptables', '-A', 'OUTPUT', '-d', '192.168.0.0/16', '-j', 'ACCEPT'], check=True)
        subprocess.run(['sudo', 'iptables', '-A', 'OUTPUT', '-d', '10.0.0.0/8', '-j', 'ACCEPT'], check=True)
        subprocess.run(['sudo', 'iptables', '-A', 'OUTPUT', '-d', '172.16.0.0/12', '-j', 'ACCEPT'], check=True)

        # Block all traffic after 10 PM (22:00) until 12 AM (00:00)
        subprocess.run(['sudo', 'iptables', '-A', 'OUTPUT', '-m', 'time', '--timestart', '22:00', '--timestop', '00:00', '-j', 'DROP'], check=True)

        # Log blocked traffic
        subprocess.run(['sudo', 'iptables', '-A', 'OUTPUT', '-m', 'time', '--timestart', '22:00', '--timestop', '00:00', '-j', 'LOG', '--log-prefix', 'HOMENET BLOCKED: '], check=True)

        # Save rules
        subprocess.run(['sudo', 'apt', 'install', '-y', 'iptables-persistent'], check=True)
        subprocess.run(['sudo', 'netfilter-persistent', 'save'], check=True)

        logging.info("Firewall setup completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Firewall setup failed: {e}")
        return False

# --- API Endpoints ---
@app.route('/')
@auth.login_required
def dashboard():
    """Render the dashboard."""
    return render_template('index.html')

@app.route('/api/hosts')
@auth.login_required
def get_hosts():
    """Get all connected hosts."""
    try:
        hosts = db_query("SELECT * FROM hosts")
        return jsonify([{
            'id': host['id'],
            'ip': host['ip'],
            'mac': host['mac'],
            'hostname': host['hostname'],
            'os': host['os'],
            'first_seen': host['first_seen'],
            'last_seen': host['last_seen']
        } for host in hosts])
    except Exception as e:
        logging.error(f"Error in get_hosts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/traffic')
@auth.login_required
def get_traffic():
    """Get traffic data for all hosts."""
    try:
        traffic = db_query('''
            SELECT h.ip, h.hostname, t.timestamp, t.bytes_sent, t.bytes_received
            FROM traffic t
            JOIN hosts h ON t.host_id = h.id
            ORDER BY t.timestamp DESC
        ''')
        return jsonify([{
            'ip': row['ip'],
            'hostname': row['hostname'],
            'timestamp': row['timestamp'],
            'bytes_sent': row['bytes_sent'],
            'bytes_received': row['bytes_received']
        } for row in traffic])
    except Exception as e:
        logging.error(f"Error in get_traffic: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts')
@auth.login_required
def get_alerts():
    """Get all alerts."""
    try:
        alerts = db_query('''
            SELECT a.id, a.alert_type, a.message, a.timestamp, h.ip, h.hostname
            FROM alerts a
            JOIN hosts h ON a.host_id = h.id
            ORDER BY a.timestamp DESC
        ''')
        return jsonify([{
            'id': alert['id'],
            'alert_type': alert['alert_type'],
            'message': alert['message'],
            'timestamp': alert['timestamp'],
            'ip': alert['ip'],
            'hostname': alert['hostname']
        } for alert in alerts])
    except Exception as e:
        logging.error(f"Error in get_alerts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dns_blocks')
@auth.login_required
def get_dns_blocks():
    """Get all DNS blocks."""
    try:
        blocks = db_query('''
            SELECT d.domain, d.timestamp, h.ip, h.hostname
            FROM dns_blocks d
            JOIN hosts h ON d.host_id = h.id
            ORDER BY d.timestamp DESC
        ''')
        return jsonify([{
            'domain': block['domain'],
            'timestamp': block['timestamp'],
            'ip': block['ip'],
            'hostname': block['hostname']
        } for block in blocks])
    except Exception as e:
        logging.error(f"Error in get_dns_blocks: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/hosts', methods=['POST'])
@auth.login_required
def add_host():
    """Add a new host."""
    try:
        data = request.json
        if not all(k in data for k in ['ip', 'mac']):
            abort(400, description="Missing required fields: ip, mac")

        if not is_valid_ip(data['ip']):
            abort(400, description="Invalid IP address")
        if not is_valid_mac(data['mac']):
            abort(400, description="Invalid MAC address")

        host_id = db_query(
            "INSERT INTO hosts (ip, mac, hostname, os, first_seen, last_seen) VALUES (?, ?, ?, ?, ?, ?)",
            (data['ip'], data['mac'], data.get('hostname', ''), data.get('os', ''), data.get('first_seen', datetime.now().isoformat()), data.get('last_seen', datetime.now().isoformat())),
            one=True
        ).lastrowid
        return jsonify({'id': host_id}), 201
    except sqlite3.IntegrityError:
        abort(409, description="Host with this IP or MAC already exists")
    except Exception as e:
        logging.error(f"Error in add_host: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/setup', methods=['POST'])
@auth.login_required
def api_setup():
    """Set up DNS and firewall via API."""
    try:
        dns_success = setup_dns_blocking()
        firewall_success = setup_firewall()
        return jsonify({
            'dns': 'success' if dns_success else 'failed',
            'firewall': 'success' if firewall_success else 'failed',
            'message': 'Setup completed' if (dns_success and firewall_success) else 'Partial setup'
        }), 200 if (dns_success and firewall_success) else 500
    except Exception as e:
        logging.error(f"Error in api_setup: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})

# --- Main ---
if __name__ == '__main__':
    logging.info("Starting HomeNet...")
    app.run(host='0.0.0.0', port=5000, debug=False)
