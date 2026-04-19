#!/bin/bash
###############################################################################
# HomeNet — Setup Script
# Proudly developed in UAE 🇦🇪
# Installs all dependencies, sets up database, and creates system service
###############################################################################

set -e

echo "================================================"
echo "  🌐 HomeNet Installer v1.0.0"
echo "  🇦🇪 Proudly developed in UAE"
echo "================================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Please run with sudo: sudo bash setup.sh"
    exit 1
fi

INSTALL_DIR="/opt/homenetservice"
DATA_DIR="/var/lib/homenetservice"
LOG_DIR="/var/log/homenetservice"

echo "📦 Installing system dependencies..."
apt-get update
apt-get install -y python3 python3-pip python3-venv iptables nftables \
    tcpdump nmap speedtest-cli net-tools iproute2 libpcap-dev \
    python3-dev python3-tk

echo ""
echo "📁 Creating directories..."
mkdir -p "$INSTALL_DIR" "$DATA_DIR" "$LOG_DIR"

echo ""
echo " Creating Python virtual environment..."
cd "$INSTALL_DIR"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

echo ""
echo "📚 Installing Python packages..."
pip install scapy speedtest-cli psutil customtkinter pillow \
    plyer schedule netifaces dnspython requests python-dotenv

echo ""
echo " Setting up firewall rules..."
# Enable IP forwarding
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sysctl -p 2>/dev/null || true

# Enable NAT for LAN
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE 2>/dev/null || true
iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE 2>/dev/null || true

echo ""
echo "🗄️ Initializing database..."
python3 -c "
import sys
sys.path.insert(0, '$INSTALL_DIR')
from homenetservice.database import init_db
init_db()
print('✅ Database initialized at $DATA_DIR/homenetservice.db')
"

echo ""
echo "📋 Installing systemd service..."
cat > /etc/systemd/system/homenetservice.service << EOF
[Unit]
Description=HomeNet Parental Network Controller
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python3 -m homenetservice.main
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable homenetservice 2>/dev/null || true

echo ""
echo "🔐 Creating default admin account..."
echo "   Username: admin"
echo "   Password: 123456"
echo "   ⚠️  Please change the password after first login!"

echo ""
echo "================================================"
echo "  ✅ HomeNet installation complete!"
echo "================================================"
echo ""
echo "  To start the service:   sudo systemctl start homenetservice"
echo "  To launch CLI:          homenetservice-cli"
echo "  To launch GUI:          homenetservice-gui"
echo ""
echo "  Default login: admin / 123456"
echo "================================================"