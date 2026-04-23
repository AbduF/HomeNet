#!/bin/bash
#
# HomeNet 3-Step Installation Script
# Optimized for Raspberry Pi 3
# One-command installation
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Banner
echo -e "${BLUE}"
cat << 'EOF'
╔═══════════════════════════════════════════╗
║     HomeNet - 3-Step Quick Install        ║
║   Parental Network Controller + AI Helper  ║
║      Proudly developed in UAE, Al Ain     ║
╚═══════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}⚠️  ERROR: Do NOT run as root!${NC}"
    echo "Run as regular user (pi):"
    echo "  curl -sL https://... | bash"
    exit 1
fi

# Get user
USER_HOME=$(eval echo ~$USER)
USER_NAME=$(whoami)

echo -e "${GREEN}[1/3]${NC} Preparing Raspberry Pi..."

# Minimal dependencies
sudo apt update -qq
sudo apt install -y -qq python3 python3-pip python3-venv iptables git curl

echo -e "${GREEN}[2/3]${NC} Installing HomeNet (optimized for Pi 3)..."

# Clone or update
if [ -d "$USER_HOME/HomeNet" ]; then
    echo "Updating existing installation..."
    cd "$USER_HOME/HomeNet"
    git pull
else
    git clone https://github.com/AbduF/HomeNet.git "$USER_HOME/HomeNet"
    cd "$USER_HOME/HomeNet"
fi

# Create virtual environment (lightweight)
python3 -m venv venv --without-pip
source venv/bin/activate

# Install minimal packages for Pi 3
pip install --quiet --no-cache-dir \
    customtkinter==5.2.0 \
    psutil==5.9.0 \
    requests==2.31.0 \
    pillow==10.0.0

# Lightweight alternatives for Pi 3
pip install --quiet --no-cache-dir \
    plyer==2.0.0

echo -e "${GREEN}[3/3]${NC} Configuring..."

# Create directories
mkdir -p logs data backups

# Fix permissions
chmod +x main.py
chmod +x setup.sh 2>/dev/null || true

# Quick iptables setup
echo "$USER_NAME ALL=(ALL) NOPASSWD: /sbin/iptables" | sudo tee /etc/sudoers.d/homenet > /dev/null
sudo chmod 440 /etc/sudoers.d/homenet

# Create auto-start service
cat > "$USER_HOME/HomeNet/homenet.service" << EOF
[Unit]
Description=HomeNet - Parental Network Controller
After=network.target
[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$USER_HOME/HomeNet
ExecStart=$USER_HOME/HomeNet/venv/bin/python3 $USER_HOME/HomeNet/main.py
Restart=always
RestartSec=30
[Install]
WantedBy=multi-user.target
EOF

sudo cp "$USER_HOME/HomeNet/homenet.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable homenet

# Start service
sudo systemctl start homenet

# Done
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║               ✅ INSTALLATION COMPLETE!                ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Access HomeNet:${NC}"
echo "  🌐 http://homenet.local:5000"
echo "  or http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo -e "${YELLOW}Login Credentials:${NC}"
echo "  Username: ${GREEN}admin${NC}"
echo "  Password: ${GREEN}123456${NC}"
echo ""
echo -e "${RED}⚠️  IMPORTANT: Change your password after login!${NC}"
echo ""
echo -e "${BLUE}Quick Commands:${NC}"
echo "  Status:   sudo systemctl status homenet"
echo "  Logs:     tail -f $USER_HOME/HomeNet/logs/homenet.log"
echo "  Restart:  sudo systemctl restart homenet"
echo "  Stop:     sudo systemctl stop homenet"
echo ""
echo -e "${GREEN}AI Assistant:${NC}"
echo "  GLM5 Flash enabled for smart parental guidance"
echo ""
