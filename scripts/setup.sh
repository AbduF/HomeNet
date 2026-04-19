#!/bin/bash

# HomeNet Setup Script
# Run as root or with sudo

# Update system and install dependencies
echo "Updating system and installing dependencies..."
apt-get update -y
apt-get install -y python3-pip python3-dev nginx git

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r ../requirements.txt

# Create static and templates directories
echo "Creating directories..."
mkdir -p ../static
mkdir -p ../templates

# Generate logo (if not exists)
echo "Generating logo..."
python3 ../generate_logo.py

# Configure Nginx
echo "Configuring Nginx..."
cp ../homenet.conf /etc/nginx/sites-available/homenet.conf
ln -s /etc/nginx/sites-available/homenet.conf /etc/nginx/sites-enabled/
nginx -t && systemctl restart nginx

# Create systemd service for FastAPI
echo "Setting up FastAPI as a systemd service..."
cat > /etc/systemd/system/homenet.service <<EOL
[Unit]
Description=HomeNet Admin Service
After=network.target

[Service]
User=$SUDO_USER
WorkingDirectory=$(pwd)/..
ExecStart=/usr/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Enable and start the service
systemctl daemon-reload
systemctl enable homenet
systemctl start homenet

# Print completion message
echo "HomeNet setup complete!"
echo "Access the admin dashboard at: http://$(hostname -I | awk '{print $1}')/admin"