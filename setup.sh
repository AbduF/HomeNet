#!/bin/bash
###############################################################################
# HomeNet — Setup Script (Fixed)
# Proudly developed in UAE 🇦
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

# Ensure we're running from the HomeNet repository root
if [ ! -d "homenetservice" ]; then
    echo "❌ Error: Run this script from the HomeNet repository root directory."
    echo "   cd ~/HomeNet && sudo bash setup.sh"
    exit 1
fi

INSTALL_DIR="/opt/homenetservice"
DATA_DIR="/var/lib/homenetservice"
LOG_DIR="/var/log/homenetservice"
SRC_DIR="$(pwd)"

echo "📦 Installing system dependencies..."
apt-get update -qq
apt-get install -y python3 python3-pip python3-venv iptables nftables \
    tcpdump nmap net-tools iproute2 libpcap-dev python3-dev python3-tk 2>/dev/null

echo ""
echo "📁 Creating directories..."
mkdir -p "$INSTALL_DIR" "$DATA_DIR" "$LOG_DIR"

echo ""
echo "🗄️ Initializing database (from source directory)..."
PYTHONPATH="$SRC_DIR" python3 -c "
import sys
sys.path.insert(0, '$SRC_DIR')
from homenetservice.database import init_db
init_db()
print('✅ Database initialized at $DATA_DIR/homenetservice.db')
"

echo ""
echo "📦 Deploying application to $INSTALL_DIR..."
rsync -av --delete "$SRC_DIR/" "$INSTALL_DIR/"
chown -R root:root "$INSTALL_DIR"
chmod -R 755 "$INSTALL_DIR"

echo ""
echo "🐍 Creating Python virtual environment..."
cd "$INSTALL_DIR"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q

echo ""
echo "📚 Installing Python packages..."
pip install -r requirements.txt -q

echo ""
echo "🔥 Enabling IP forwarding & NAT..."
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sysctl -p 2>/dev/null || true
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE 2>/dev/null || true
iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE 2>/dev/null || true

echo ""
echo "📋 Installing systemd service..."
cat > /etc/systemd/system/homenetservice.service << EOF
[Unit]
Description=HomeNet Parental Network Controller
After=network.target nss-lookup.target
Wants=network-online.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=$INSTALL_DIR/homenetservice.conf
ExecStart=$INSTALL_DIR/venv/bin/python -m homenetservice.main --mode service
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable homenetservice 2>/dev/null || true

echo ""
echo "================================================"
echo "  ✅ HomeNet installation complete!"
echo "================================================"
echo ""
echo "  To start the service:   sudo systemctl start homenetservice"
echo "  To launch CLI:          homenetservice-cli"
echo "  To launch GUI:          homenetservice-gui"
echo ""
echo "  🔐 Default login: admin / 123456"
echo "  ⚠️  Change password immediately after first login!"
echo "================================================"