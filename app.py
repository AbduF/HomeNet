import os
import json
import datetime
from flask import Flask, render_template, jsonify, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_netguard' # Change this in production

# --- Configuration ---
BLOCK_START_HOUR = 22
BLOCK_END_HOUR = 5
BLOCKLIST_FILE = 'blocklist.txt'
CREDENTIALS_FILE = 'credentials.json'

# --- Setup Credentials ---
def init_credentials():
    """Ensures credentials exist. Resets if corrupted."""
    try:
        if not os.path.exists(CREDENTIALS_FILE):
            with open(CREDENTIALS_FILE, 'w') as f:
                json.dump({"username": "admin", "password": "123456"}, f)
    except Exception as e:
        print(f"Error initializing credentials: {e}")

def verify_user(username, password):
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            data = json.load(f)
            return data.get('username') == username and data.get('password') == password
    except Exception:
        return False

def update_password(new_password):
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            data = json.load(f)
        data['password'] = new_password
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump(data, f)
        return True
    except Exception:
        return False

def is_blocked_time():
    now = datetime.datetime.now().hour
    return now >= BLOCK_START_HOUR or now < BLOCK_END_HOUR

def get_system_stats():
    try:
        import psutil
        net_io = psutil.net_io_counters()
        connections = psutil.net_connections(kind='inet')
        unique_ips = set([conn.raddr.ip for conn in connections if conn.raddr])
        host_count = len(unique_ips) + 2 
        
        return {
            'hosts': host_count,
            'dl_speed': 15.0, # Simulated value
            'total_volume': round(net_io.bytes_recv / (1024**3), 1)
        }
    except Exception as e:
        return {'hosts': 0, 'dl_speed': 0, 'total_volume': 0}

def load_blocklist():
    if not os.path.exists(BLOCKLIST_FILE):
        return []
    try:
        with open(BLOCKLIST_FILE, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception:
        return []

# --- Routes ---

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    if verify_user(data.get('username'), data.get('password')):
        session['logged_in'] = True
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('logged_in', None)
    return jsonify({'success': True})

@app.route('/api/change_password', methods=['POST'])
def api_change_password():
    if not session.get('logged_in'):
        return jsonify({'success': False}), 403
    data = request.json
    if verify_user(data.get('username'), data.get('old_password')):
        if update_password(data.get('new_password')):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'System error'}), 500
    return jsonify({'success': False, 'message': 'Old password incorrect'}), 400

@app.route('/api/add_block', methods=['POST'])
def add_block():
    if not session.get('logged_in'):
        return jsonify({'success': False}), 403
    data = request.json
    url = data.get('url', '').strip()
    url = url.replace('http://', '').replace('https://', '').split('/')[0]
    
    if not url or '.' not in url:
        return jsonify({'success': False, 'message': 'Invalid URL'})
    
    current_list = load_blocklist()
    if url not in current_list:
        try:
            with open(BLOCKLIST_FILE, 'a') as f:
                f.write(url + '\n')
            return jsonify({'success': True})
        except Exception:
            return jsonify({'success': False, 'message': 'Write error'})
            
    return jsonify({'success': False, 'message': 'Already in list'})

@app.route('/api/toggle_rule', methods=['POST'])
def toggle_rule():
    if not session.get('logged_in'):
        return jsonify({'success': False}), 403
    return jsonify({'success': True}) # Placeholder logic

@app.route('/api/status')
def api_status():
    if not session.get('logged_in'):
        return jsonify({'success': False, 'redirect': '/login'}), 403
        
    stats = get_system_stats()
    return jsonify({
        'status': "Blocked" if is_blocked_time() else "Active",
        'hosts': stats['hosts'],
        'dl_speed': stats['dl_speed'],
        'blocked_urls': load_blocklist(),
        'schedule': f"{BLOCK_START_HOUR}:00 - {BLOCK_END_HOUR}:00"
    })

if __name__ == '__main__':
    init_credentials()
    app.run(host='0.0.0.0', port=5000, debug=False)