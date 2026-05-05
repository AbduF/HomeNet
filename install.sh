#!/bin/bash

echo "🛡️ Installing NetGuard Parental Control..."

# 1. Update System
sudo apt-get update -y

# 2. Install Python Tools and System Monitoring
sudo apt-get install python3-pip python3-psutil -y

# 3. Install Python Libraries
pip3 install -r requirements.txt

# 4. Setup Permissions (Optional: Allow running on port 80/443 or keep 5000)
# We will use port 5000 for simplicity.

# 5. Create Systemd Service
echo "Configuring System Service..."
sudo bash -c 'cat > /etc/systemd/system/homenet.service <<EOF
[Unit]
Description=HomeNet Parental Control
After=network.target

[Service]
User=pi
Group=pi
WorkingDirectory=/home/pi/HomeNet
ExecStart=/usr/bin/python3 /home/pi/HomeNet/app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF'

# 6. Enable and Start Service
sudo systemctl daemon-reload
sudo systemctl enable homenet.service
sudo systemctl restart homenet.service

echo "✅ Installation Complete!"
echo "🌐 Access Dashboard at: http://$(hostname -I | awk '{print $1}'):5000"