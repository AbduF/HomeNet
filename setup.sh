#!/bin/bash

# HomeNet Automated Setup Script for Raspberry Pi 3
# Run this script as root or with sudo: sudo ./setup.sh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root or with sudo.${NC}"
    exit 1
fi

# Step 1: Update system and install dependencies
echo -e "${BLUE}Step 1: Updating system and installing dependencies...${NC}"
apt update -y
apt upgrade -y
apt install -y python3-pip python3-venv ufw dnsmasq arp-scan iptables-persistent nginx certbot python3-certbot-nginx speedtest-cli

# Step 2: Clone or navigate to HomeNet directory
echo -e "${BLUE}Step 2: Setting up HomeNet directory...${NC}"
if [ ! -d "/opt/HomeNet" ]; then
    git clone https://github.com/AbduF/HomeNet.git /opt/HomeNet
fi
cd /opt/HomeNet || exit

# Step 3: Create virtual environment and install Python dependencies
echo -e "${BLUE}Step 3: Setting up Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Step 4: Stop conflicting DNS services (e.g., systemd-resolved)
echo -e "${BLUE}Step 4: Stopping conflicting DNS services...${NC}"
systemctl stop systemd-resolved 2>/dev/null || true
systemctl disable systemd-resolved 2>/dev/null || true

# Step 5: Configure firewall
echo -e "${BLUE}Step 5: Configuring firewall...${NC}"
ufw --force enable
ufw allow 80
ufw allow 443
ufw allow 22  # SSH (optional)

# Step 6: Configure Nginx
echo -e "${BLUE}Step 6: Configuring Nginx...${NC}"
cp homenet_nginx.conf /etc/nginx/sites-available/homenet
ln -sf /etc/nginx/sites-available/homenet /etc/nginx/sites-enabled/homenet
rm -f /etc/nginx/sites-enabled/default  # Remove default site
nginx -t
systemctl restart nginx

# Step 7: Set up HTTPS with Certbot (if domain is provided)
read -p "Enter your domain name (e.g., homenet.example.com) or press Enter to skip HTTPS setup: " domain
if [ -n "$domain" ]; then
    echo -e "${BLUE}Step 7: Setting up HTTPS with Certbot...${NC}"
    certbot --nginx -d "$domain" --non-interactive --agree-tos --email admin@example.com --redirect
    # Auto-renew Certbot
    echo "0 0 * * * root certbot renew --quiet --post-hook \"systemctl reload nginx\"" | tee -a /etc/crontab > /dev/null
else
    echo -e "${YELLOW}Skipping HTTPS setup. Use HTTP only.${NC}"
fi

# Step 8: Create systemd service for Gunicorn
echo -e "${BLUE}Step 8: Creating systemd service for Gunicorn...${NC}"
cat > /etc/systemd/system/homenet.service <<EOF
[Unit]
Description=HomeNet Service
After=network.target

[Service]
User=root
WorkingDirectory=/opt/HomeNet
Environment="PATH=/opt/HomeNet/venv/bin"
ExecStart=/opt/HomeNet/venv/bin/gunicorn -w 2 -b 127.0.0.1:5000 app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable homenet
systemctl start homenet

# Step 9: Configure dnsmasq and firewall rules
echo -e "${BLUE}Step 9: Configuring dnsmasq and firewall rules...${NC}"
# Temporarily start the app to run setup
python app.py > /dev/null 2>&1 &
SETUP_PID=$!
sleep 5
curl -X POST -u admin:123456 http://localhost:5000/api/setup
kill $SETUP_PID 2>/dev/null
systemctl restart homenet

# Step 10: Display completion message
echo -e "${GREEN}"
echo "==========================================="
echo "HomeNet Setup Completed Successfully!"
echo "==========================================="
echo "Access your dashboard at:"
if [ -n "$domain" ]; then
    echo "https://$domain"
else
    echo "http://$(hostname -I | awk '{print $1}'):5000"
fi
echo ""
echo "Default credentials:"
echo "Username: admin"
echo "Password: 123456 (Change this in .env file!)"
echo ""
echo "To manage the service:"
echo "  - Start: sudo systemctl start homenet"
echo "  - Stop: sudo systemctl stop homenet"
echo "  - Restart: sudo systemctl restart homenet"
echo "  - Logs: sudo journalctl -u homenet -f"
echo ""
echo "To update:"
echo "  cd /opt/HomeNet && git pull && sudo systemctl restart homenet"
echo ""
echo "To troubleshoot:"
echo "  - Check dnsmasq: sudo systemctl status dnsmasq"
echo "  - Check logs: sudo journalctl -xeu dnsmasq.service"
echo "  - Test DNS: dig @localhost facebook.com"
echo "  - Test speed: speedtest-cli --simple"
echo "==========================================="
echo -e "${NC}"