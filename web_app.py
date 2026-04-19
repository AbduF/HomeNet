from flask import Flask, render_template, request, jsonify
import json
import psutil
import speedtest
import nmap
import threading
from datetime import datetime

app = Flask(__name__)
config = json.load(open('config.json'))

@app.route('/')
def dashboard():
    return render_template('dashboard.html', config=config)

@app.route('/api/hosts')
def get_hosts():
    nm = nmap.PortScanner()
    nm.scan(hosts='192.168.1.0/24', arguments='-sn')
    hosts = []
    for host in nm.all_hosts():
        hosts.append({
            'ip': host,
            'mac': nm[host]['addresses'].get('mac', 'Unknown'),
            'status': 'up'
        })
    return jsonify(hosts)

@app.route('/api/traffic')
def get_traffic():
    net = psutil.net_io_counters()
    return jsonify({
        'bytes_sent': net.bytes_sent,
        'bytes_recv': net.bytes_recv,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/speedtest', methods=['POST'])
def run_speedtest():
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download = st.download() / 1_000_000
        upload = st.upload() / 1_000_000
        return jsonify({
            'download': round(download, 2),
            'upload': round(upload, 2),
            'ping': st.results.ping
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)