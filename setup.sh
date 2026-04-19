#!/bin/bash
###############################################################################
# HomeNet — Setup Script (v1.1 Fixed)
# Proudly developed in UAE 🇦🇪
###############################################################################

set -e

echo "================================================"
echo "  🌐 HomeNet Installer v1.0.0"
echo "  🇦 Proudly developed in UAE"
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

SRC_DIR="$(pwd)"
INSTALL_DIR="/opt/homenetservice"
DATA_DIR="/var/lib/homenetservice"
LOG_DIR="/var/log/homenetservice"

echo "📦 Installing system dependencies..."
apt-get update -qq
apt-get install -y python3 python3-pip python3-venv iptables nftables \
    tcpdump nmap net-tools iproute2 libpcap-dev python3-dev python3-tk rsync 2>/dev/null

echo ""
echo "📁 Creating directories..."
mkdir -p "$INSTALL_DIR" "$DATA_DIR" "$LOG_DIR"

echo ""
echo "🐍 Creating Python virtual environment & installing packages..."
cd "$SRC_DIR"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo ""
echo "📦 Deploying application to $INSTALL_DIR..."
rsync -av --delete "$SRC_DIR/" "$INSTALL_DIR/"
chown -R root:root "$INSTALL_DIR"
chmod -R 755 "$INSTALL_DIR"

echo ""
echo "🗄️ Initializing database..."
cd "$INSTALL_DIR"
# Use the venv's Python with correct PYTHONPATH
PYTHONPATH="$INSTALL_DIR" ./venv/bin/python3 -c "
import sys
sys.path.insert(0, '$INSTALL_DIR')
from homenetservice.database import init_db
init_db()
print('✅ Database initialized at $DATA_DIR/homenetservice.db')
"

echo ""
echo "🔥 Configuring network & firewall..."
# Prevent duplicate sysctl entries
if ! grep -q "net.ipv4.ip_forward=1" /etc/sysctl.conf; then
    echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
fi
sysctl -p 2>/dev/null || true

# Prevent duplicate MASQUERADE rules
iptables -t nat -C POSTROUTING -o eth0 -j MASQUERADE 2>/dev/null || \
    iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -t nat -C POSTROUTING -o wlan0 -j MASQUERADE 2>/dev/null || \
    iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE

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
echo "  🚀 Start service:  sudo systemctl start homenetservice"
echo "  💻 Launch CLI:     cd $INSTALL_DIR && source venv/bin/activate && python -m homenetservice.cli"
echo "  🖥️ Launch GUI:     cd $INSTALL_DIR && source venv/bin/activate && python -m homenetservice.gui"
echo ""
echo "  🔐 Default login:  admin / 123456"
echo "  ⚠️  Change password immediately after first login!"
echo "================================================"