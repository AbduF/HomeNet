from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
import psutil
import speedtest
import nmap
import threading
import time
from datetime import datetime
from functools import wraps
import socket

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Load config
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)

def load_i18n(lang='en'):
    try:
        with open(f'i18n/{lang}.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    config = load_config()
    i18n = load_i18n(config['settings']['language'])
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == config['admin']['username'] and password == config['admin']['password']:
            session['logged_in'] = True
            session['username'] = username
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': i18n.get('invalid_credentials', 'Invalid credentials')})
    
    return render_template('login.html', i18n=i18n, config=config)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    config = load_config()
    i18n = load_i18n(config['settings']['language'])
    return render_template('dashboard.html', i18n=i18n, config=config)

@app.route('/api/hosts')
@login_required
def get_hosts():
    try:
        nm = nmap.PortScanner()
        # Get local network range
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        network = '.'.join(local_ip.split('.')[:-1]) + '.0/24'
        
        nm.scan(hosts=network, arguments='-sn')
        hosts = []
        
        for host in nm.all_hosts():
            host_info = {
                'ip': host,
                'mac': 'Unknown',
                'vendor': 'Unknown',
                'status': 'up'
            }
            
            if 'mac' in nm[host]['addresses']:
                host_info['mac'] = nm[host]['addresses']['mac']
                if 'vendor' in nm[host] and nm[host]['vendor']:
                    host_info['vendor'] = list(nm[host]['vendor'].values())[0]
            
            hosts.append(host_info)
        
        return jsonify(hosts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/traffic')
@login_required
def get_traffic():
    try:
        net = psutil.net_io_counters()
        return jsonify({
            'bytes_sent': net.bytes_sent,
            'bytes_recv': net.bytes_recv,
            'packets_sent': net.packets_sent,
            'packets_recv': net.packets_recv,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/speedtest', methods=['POST'])
@login_required
def run_speedtest():
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download = st.download() / 1_000_000
        upload = st.upload() / 1_000_000
        ping = st.results.ping
        
        return jsonify({
            'download': round(download, 2),
            'upload': round(upload, 2),
            'ping': round(ping, 2)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rules', methods=['GET', 'POST'])
@login_required
def manage_rules():
    config = load_config()
    
    if request.method == 'POST':
        data = request.json
        if 'rules' in data:
            config['rules'] = data['rules']
        if 'block_schedule' in data:
            config['settings']['block_schedule'] = data['block_schedule']
        save_config(config)
        return jsonify({'success': True})
    
    return