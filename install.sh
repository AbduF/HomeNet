#!/bin/bash
# HomeNet Web Mode Installer
# Proudly developed in UAE / Al Ain

set -e

echo "🌐 HomeNet Web Mode Installer"
echo "🇦🇪 UAE / Al Ain"
echo "================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check if running on Raspberry Pi
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [[ "$NAME" != *"Raspbian"* && "$NAME" != *"Debian"* && "$NAME" != *"Ubuntu"* ]]; then
        print_info "Note: Not detected as Raspberry Pi OS, but continuing..."
    fi
fi

# Step 1: Update system
print_info "Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Step 2: Install system dependencies
print_info "Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    nmap \
    git \
    curl \
    libatlas-base-dev

# Step 3: Clone or update repo
if [ -d "HomeNet" ]; then
    print_info "HomeNet directory exists, updating..."
    cd HomeNet
    git pull
else
    print_info "Cloning HomeNet repository..."
    git clone https://github.com/AbduF/HomeNet.git
    cd HomeNet
fi

# Step 4: Create virtual environment
print_info "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Step 5: Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip

# Step 6: Install Python dependencies
print_info "Installing Python dependencies..."
pip install -r requirements.txt

# Step 7: Set capabilities for nmap
print_info "Configuring nmap permissions..."
sudo setcap cap_net_raw,cap_net_admin=eip $(which python3) 2>/dev/null || true

# Step 8: Configure systemd service
print_info "Creating systemd service..."
sudo bash -c 'cat > /etc/systemd/system/homenet.service << EOF
[Unit]
Description=HomeNet Web Interface
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/HomeNet
Environment="PATH=/home/pi/HomeNet/venv/bin"
ExecStart=/home/pi/HomeNet/venv/bin/python3 /home/pi/HomeNet/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF'

# Step 9: Enable and start service
print_info "Enabling and starting HomeNet service..."
sudo systemctl daemon-reload
sudo systemctl enable homenet.service
sudo systemctl start homenet.service

# Step 10: Get IP address
IP_ADDRESS=$(hostname -I | awk '{print $1}')

echo ""
echo "================================"
print_success "Installation Complete!"
echo "================================"
echo ""
echo "🌐 Access HomeNet at:"
echo "   http://localhost:5000"
echo "   http://$IP_ADDRESS:5000"
echo ""
echo "🔑 Default Credentials:"
echo "   Username: admin"
echo "   Password: 123456"
echo ""
echo "🔧 Service Commands:"
echo "   sudo systemctl status homenet"
echo "   sudo systemctl stop homenet"
echo "   sudo systemctl restart homenet"
echo ""
echo "📝 Logs:"
echo "   sudo journalctl -u homenet -f"
echo ""
echo "🇦🇪 Proudly developed in UAE / Al Ain"
echo "📧 Support: abdalfaqeeh@gmail.com"
echo ""