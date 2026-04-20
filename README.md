# HomeNet - Parental Network Controller 🌐

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Platform-Linux|Raspberry%20Pi-orange.svg" alt="Platform">
  <img src="https://img.shields.io/badge/UI-Bilingual%20(EN/AR)-purple.svg" alt="UI">
</p>

<p align="center">
  <strong>🛡️ Parental Network Controller with time blocking, traffic monitoring & bilingual UI</strong>
</p>

<p align="center">
  Proudly developed in UAE, Al Ain 🇦🇪
</p>

---

## 📖 Table of Contents

- [Features](#-features)
- [Screenshots](#-screenshots)
- [Quick Start (5 Minutes)](#-quick-start-5-minutes)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Network Diagram](#-network-diagram)
- [Raspberry Pi Setup](#-raspberry-pi-setup)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

---

## ✨ Features

### 🕐 Time-Based Blocking
- **Default Schedule**: 11 PM - 12 AM (configurable)
- Block all internet during bedtime
- Customizable days and times
- Easy schedule management

### 👨‍💻 Host Management
- Automatic network scanning
- Device identification (OS, Type, Vendor)
- Block/Unblock individual devices
- Real-time device status
- MAC address tracking

### 📊 Traffic Monitoring
- Real-time bandwidth monitoring
- Download/Upload speed tracking
- Traffic history and analytics
- Top bandwidth consumers
- Built-in speed test

### 🎮 App & Content Blocking
- **Gaming**: Steam, Epic, Roblox, Minecraft, Xbox, PlayStation
- **Social Media**: Facebook, Instagram, TikTok, Snapchat, Twitter
- **Streaming**: Netflix, YouTube, Disney+, Amazon Prime, Spotify
- Custom domain blocking

### 🔔 Smart Alerts
- New device notifications
- High traffic warnings
- Blocked connection attempts
- Email notifications

### 🌐 Bilingual Interface
- **English** 🇺🇸
- **العربية** 🇸🇦 (Arabic with RTL support)

---

## 🖥️ Screenshots

### Dashboard
```
┌─────────────────────────────────────────────────────────────┐
│  🌐 HomeNet - Parental Network Controller                   │
├────────────┬────────────────────────────────────────────────┤
│ 🏠 Dashboard│  Network Overview                              │
│ 💻 Hosts    │                                                │
│ 📊 Traffic  │  ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│ 🛡️ Rules   │  │  5      │ │  🛡️     │ │  3      │          │
│ 🔔 Alerts   │  │ Hosts   │ │Blocking │ │ Alerts  │          │
│ ⚙️ Settings │  └─────────┘ └─────────┘ └─────────┘          │
│            │                                                │
│ [Blocking] │  Download: 45.2 Mbps  Upload: 8.1 Mbps          │
│  [  OFF  ] │                                                │
└────────────┴────────────────────────────────────────────────┘
```

### Login Screen
```
┌─────────────────────────────────────────┐
│                                         │
│           🌐 HomeNet                    │
│    Parental Network Controller          │
│                                         │
│   ┌───────────────────────────────┐    │
│   │  Username                      │    │
│   │  Password                       │    │
│   │                                 │    │
│   │      [ Login ]                  │    │
│   └───────────────────────────────┘    │
│                                         │
│     Proudly developed in UAE, Al Ain    │
│    Contact: abdalfaqeeh@gmail.com       │
└─────────────────────────────────────────┘
```

---

## ⚡ Quick Start (5 Minutes)

### Step 1: Flash Raspberry Pi OS
```bash
# Download Raspberry Pi Imager from https://www.raspberrypi.com/software/
# Select Raspberry Pi OS Lite (or Desktop)
# Configure WiFi/Ethernet and enable SSH
```

### Step 2: Connect and Update
```bash
ssh pi@raspberrypi.local
sudo apt update && sudo apt upgrade -y
```

### Step 3: Install Dependencies
```bash
sudo apt install -y python3-pip python3-venv iptables
pip3 install virtualenv
```

### Step 4: Clone and Setup
```bash
cd ~
git clone https://github.com/AbduF/HomeNet.git
cd HomeNet
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 5: Run HomeNet
```bash
# For GUI (with X server)
python3 main.py

# For headless/background operation
python3 main.py --headless
```

### Step 6: Access the App
```
Open browser or VNC to: http://<raspberry-pi-ip>:5000
Default login: admin / 123456
```

---

## 📦 Installation

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.10+ | Required |
| Raspberry Pi OS | Bullseye+ | Recommended |
| Linux | Any | Full iptables support |
| Network Access | Required | For monitoring |

### Install on Raspberry Pi

```bash
# Create dedicated user (recommended)
sudo useradd -m -s /bin/bash homesafe
sudo usermod -aG sudo homesafe

# Switch to user
sudo su - homesafe

# Clone repository
git clone https://github.com/AbduF/HomeNet.git
cd HomeNet

# Install system dependencies
sudo apt update
sudo apt install -y \
    python3-pip \
    python3-venv \
    iptables \
    dnsutils \
    net-tools \
    wireless-tools \
    iw

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Set up iptables permissions
sudo apt install -y iptables-persistent
```

### Desktop Installation (Ubuntu/Debian)

```bash
# Clone repository
git clone https://github.com/AbduF/HomeNet.git
cd HomeNet

# Install dependencies
sudo apt update
sudo apt install -y python3-pip python3-venv iptables
pip3 install -r requirements.txt

# Run
python3 main.py
```

### Windows/Mac (Limited Features)

> ⚠️ **Note**: Full blocking features require Linux with iptables.
> Windows/Mac can use monitoring features only.

```bash
# Clone and run
git clone https://github.com/AbduF/HomeNet.git
cd HomeNet
pip install -r requirements.txt
python main.py
```

---

## ⚙️ Configuration

### Default Settings

| Setting | Default | Description |
|---------|---------|-------------|
| Username | `admin` | Login username |
| Password | `123456` | Login password |
| Language | `en` | English (also `ar` for Arabic) |
| Blocking | `OFF` | Default blocking state |
| Scan Interval | `60s` | Network scan frequency |

### Configuration File

Edit `config.json` in the application directory:

```json
{
    "language": "en",
    "theme": "dark",
    "blocking_enabled": false,
    "network_interface": "auto",
    "scan_interval": 60,
    "traffic_log_interval": 60,
    "alert_new_host": true,
    "alert_high_traffic": true,
    "high_traffic_threshold": 1000000000,
    "auto_block_schedules": true,
    "email_enabled": false,
    "smtp_host": "",
    "smtp_port": 587,
    "smtp_user": "",
    "smtp_password": "",
    "admin_email": "abdalfaqeeh@gmail.com"
}
```

### Blocking Schedule Configuration

Default blocking time: **11:00 PM - 12:00 AM (23:00 - 00:00)**

To customize, edit via the Rules tab in the application or modify `homenet.db`:

```sql
-- View schedules
SELECT * FROM schedules;

-- Add custom schedule
INSERT INTO schedules (name, start_time, end_time, days, enabled)
VALUES ('Homework Time', '15:00', '18:00', '[0,1,2,3,4]', 1);
```

---

## 🚀 Usage

### Starting the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Run with GUI
python3 main.py

# Run in background
python3 main.py --headless &

# Run as service (recommended for Raspberry Pi)
sudo cp HomeNet.service /etc/systemd/system/
sudo systemctl enable HomeNet
sudo systemctl start HomeNet
```

### Accessing the Application

| Method | URL/Command | Notes |
|--------|-------------|-------|
| Local GUI | Run directly | On Pi desktop |
| VNC | `vnc://pi-ip:5900` | If VNC enabled |
| Web | `http://pi-ip:5000` | If web mode enabled |
| SSH Tunnel | `ssh -L 5000:localhost:5000` | Remote access |

### Default Login

```
Username: admin
Password: 123456
```

> ⚠️ **IMPORTANT**: Change default password immediately after first login!

### First-Time Setup

1. **Login** with default credentials
2. **Change Password** in Settings
3. **Configure Email** for alerts (optional)
4. **Scan Network** to discover devices
5. **Set Blocking Rules** for gaming/social apps
6. **Configure Schedule** for bedtime blocking
7. **Test Blocking** to ensure it works

---

## 🔌 Network Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         HOME NETWORK                                │
│                                                                     │
│    ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐  │
│    │  Kids'   │     │ Parents' │     │  Smart   │     │  Gaming  │  │
│    │ Devices  │     │ Devices  │     │  Home    │     │ Console │  │
│    │ 📱💻🎮   │     │  📱💻    │     │  📺🔌   │     │   🎮    │  │
│    └────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘  │
│         │                │                │                │        │
│         └────────────────┼────────────────┼────────────────┘        │
│                          │                │                          │
│                     ┌────▼────┐      ┌─────▼─────┐                     │
│                     │  Switch │      │ WiFi AP   │                     │
│                     │ /Router │      │  (AP)     │                     │
│                     └────┬────┘      └─────┬─────┘                     │
│                          │                │                          │
│          ┌───────────────┼────────────────┼┘                          │
│          │               │                │                           │
│    ┌─────▼─────┐  ┌──────▼──────┐  ┌──────▼──────┐                     │
│    │           │  │             │  │             │                     │
│    │  Internet │  │  Raspberry  │  │   Family    │                     │
│    │    🌐     │  │     Pi 3     │  │   Devices   │                     │
│    │           │  │             │  │             │                     │
│    └───────────┘  │  ┌───────┐  │  └─────────────┘                     │
│                   │  │HomeNet│  │                                      │
│                   │  │ App   │  │                                      │
│                   │  │🛡️📊🔔│  │                                      │
│                   │  └───────┘  │                                      │
│                   └─────────────┘                                      │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │                  HomeNet Dashboard                          │     │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │     │
│  │  │ Hosts: 5 │  │ Traffic  │  │ Rules: 20 │  │ Alerts: 3│    │     │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │     │
│  │                                                             │     │
│  │  Blocking: [11 PM - 12 AM]  Status: ● Active               │     │
│  └─────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
```

### Network Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                       BLOCKING FLOW                              │
└─────────────────────────────────────────────────────────────────┘

   INCOMING              HOMENET                    OUTGOING
   TRAFFIC              IPTABLES                     TRAFFIC
     │                    CHAIN                        │
     │                     │                         │
     ▼                     ▼                         ▲
┌─────────┐    ┌─────────────────────┐    ┌──────────────┐
│Internet │───▶│    HOMENET CHAIN    │───▶│   LAN/WiFi   │
│  WAN    │    │                     │    │   Devices    │
└─────────┘    │ ┌─────────────────┐ │    └──────────────┘
               │ │ Schedule Check │ │
               │ │  11PM - 12AM?   │ │
               │ └────────┬────────┘ │
               │          │           │
               │    ┌─────▼─────┐     │
               │    │  MATCH?   │     │
               │    └─────┬─────┘     │
               │          │           │
               │    ┌─────▼─────┐     │
               │    │   RULE    │     │
               │    │  MATCH?   │     │
               │    └─────┬─────┘     │
               │          │           │
               │    ┌─────▼─────┐     │
               │    │  ACTION   │     │
               │    │ACCEPT/DROP│     │
               │    └───────────┘     │
               └─────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    TRAFFIC MONITORING                           │
└─────────────────────────────────────────────────────────────────┘

   DEVICES              MONITOR                  DATABASE
     │                     │                        │
     │     ┌───────────────┼────────────────┐       │
     │     │               │                │       │
     ▼     ▼               ▼                ▼       ▼
┌────────┐┌────────┐ ┌────────────┐ ┌─────────────────────────┐
│ Host 1 ││ Host 2 │ │  Real-time │ │    Traffic Logs        │
│ 📱     ││  💻    │ │  Monitor   │ │  ┌─────────────────┐   │
└────────┘└────────┘ │            │ │  │ timestamp       │   │
                     │  psutil    │ │  │ bytes_sent      │   │
                     │  + ARP     │ │  │ bytes_received  │   │
                     │  scanning  │ │  │ host_id         │   │
                     └────────────┘ │  └─────────────────┘   │
                                    └─────────────────────────┘
```

---

## 🍓 Raspberry Pi Setup

### Complete 5-Minute Guide

#### Step 1: Prepare the SD Card (2 minutes)

```bash
# Download Raspberry Pi Imager from:
# https://www.raspberrypi.com/software/

# Steps:
# 1. Select "Raspberry Pi OS Lite (64-bit)"
# 2. Click the gear icon for advanced options:
#    - Set hostname: HomeNet
#    - Enable SSH with password authentication
#    - Configure WiFi (if needed)
#    - Set username/password: pi / yourpassword
# 3. Write to SD card
# 4. Insert SD card and power on Pi
```

#### Step 2: Initial Setup (1 minute)

```bash
# SSH into your Pi
ssh pi@homenet.local

# Update system
sudo apt update && sudo apt upgrade -y

# Set hostname
sudo hostnamectl set-hostname HomeNet
echo "127.0.1.1 HomeNet" | sudo tee -a /etc/hosts

# Enable required services
sudo systemctl enable ssh
sudo systemctl start ssh
```

#### Step 3: Install HomeNet (1.5 minutes)

```bash
# Install dependencies
sudo apt install -y python3-pip python3-venv iptables git

# Clone HomeNet
cd ~
git clone https://github.com/AbduF/HomeNet.git
cd HomeNet

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

#### Step 4: Configure Network (0.5 minutes)

```bash
# Make HomeNet start automatically
sudo cp HomeNet.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable HomeNet

# Allow HomeNet to control iptables
echo "pi ALL=(ALL) NOPASSWD: /sbin/iptables, /sbin/ip6tables" | sudo tee /etc/sudoers.d/homenet
```

#### Step 5: Run and Access (Ongoing)

```bash
# Start HomeNet service
sudo systemctl start HomeNet

# Check status
sudo systemctl status HomeNet

# View logs
sudo journalctl -u HomeNet -f

# Access web interface
# Open browser: http://HomeNet:5000
# Default login: admin / 123456
```

### Network Placement

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   Modem/Router                                              │
│   (192.168.1.1)                                             │
│        │                                                    │
│        │ WAN                                                │
│        ▼                                                    │
│   ┌─────────────┐                                           │
│   │  Raspberry  │◄─── Patch cable to LAN port               │
│   │    Pi 3     │                                           │
│   │ HomeNet App │                                           │
│   └──────┬──────┘                                           │
│          │ LAN                                              │
│          │ (Bridge/ NAT)                                   │
│          ▼                                                  │
│   ┌─────────────┐                                           │
│   │  Family     │◄─── All home devices connect here         │
│   │  Network    │                                           │
│   └─────────────┘                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Making Pi a Gateway

```bash
# Enable IP forwarding
sudo sysctl -w net.ipv4.ip_forward=1
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf

# Set up NAT
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables -A FORWARD -i eth0 -o eth1 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i eth1 -o eth0 -j ACCEPT

# Save iptables rules
sudo sh -c "iptables-save > /etc/iptables.rules"

# Add to startup
sudo tee /etc/network/if-pre-up.d/iptables > /dev/null <<'EOF'
#!/bin/sh
iptables-restore < /etc/iptables.rules
EOF
sudo chmod +x /etc/network/if-pre-up.d/iptables
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Login Failed

```bash
# Reset password via database
sqlite3 ~/HomeNet/homenet.db
SQL> UPDATE users SET password_hash = '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92' WHERE username = 'admin';
SQL> .quit
# New password: 123456
```

#### 2. iptables Permission Denied

```bash
# Check sudoers configuration
sudo visudo

# Add this line:
username ALL=(ALL) NOPASSWD: /sbin/iptables, /sbin/ip6tables
```

#### 3. Network Scanning Returns No Hosts

```bash
# Install nmap for better scanning
sudo apt install -y nmap

# Check ARP table
ip neigh show

# Scan manually
sudo nmap -sn 192.168.1.0/24
```

#### 4. Blocking Not Working

```bash
# Check if iptables chain exists
sudo iptables -L -n -v

# Check if HOMENET chain is present
sudo iptables -L HOMENET -n

# Manually add test rule
sudo iptables -A HOMENET -d 8.8.8.8 -j DROP

# Test blocking
ping 8.8.8.8

# Remove test rule
sudo iptables -D HOMENET -d 8.8.8.8 -j DROP
```

#### 5. GUI Won't Start

```bash
# Check Python version
python3 --version  # Must be 3.10+

# Install missing dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Try running with verbose output
python3 -v main.py

# Check for display issues (for SSH)
echo $DISPLAY
# If empty, set it or use --headless
python3 main.py --headless
```

#### 6. High CPU Usage

```bash
# Check running processes
top

# Reduce scan frequency
# Edit config.json:
# "scan_interval": 60  # Increase to 300 (5 minutes)
```

### Debug Mode

```bash
# Run with debug logging
LOG_LEVEL=DEBUG python3 main.py

# View application logs
tail -f ~/HomeNet/logs/homenet.log
```

### Reset Everything

```bash
# Stop service
sudo systemctl stop HomeNet

# Backup database
cp ~/HomeNet/homenet.db ~/HomeNet/homenet.db.bak

# Reset to defaults
rm ~/HomeNet/homenet.db
python3 main.py  # Will recreate database

# Restore custom rules (if needed)
# Copy back specific tables from backup
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Fork the repository
# Clone your fork
git clone https://github.com/YOUR-USERNAME/HomeNet.git
cd HomeNet

# Create feature branch
git checkout -b feature/AmazingFeature

# Make changes and commit
git commit -m 'Add some AmazingFeature'

# Push to branch
git push origin feature/AmazingFeature

# Open Pull Request
```

### Coding Standards

- Follow PEP 8
- Add docstrings to functions
- Use type hints where possible
- Include translations for new text

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 HomeNet
Author: AbduF

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software to deal in the Software without restriction.
```

---

## 📧 Contact & Support

**Developer**: AbduF
**Email**: abdalfaqeeh@gmail.com
**Location**: Al Ain, UAE 🇦🇪

### Get Help

- 📖 [Wiki](https://github.com/AbduF/HomeNet/wiki)
- 🐛 [Issues](https://github.com/AbduF/HomeNet/issues)
- 💬 [Discussions](https://github.com/AbduF/HomeNet/discussions)

### Report Bugs

Found a bug? Please [open an issue](https://github.com/AbduF/HomeNet/issues/new) with:
- Description of the bug
- Steps to reproduce
- Expected vs actual behavior
- System information (`uname -a`)

---

## 🙏 Acknowledgments

- **Python Community** - For amazing libraries
- **CustomTkinter** - For modern GUI components
- **Scapy** - For network packet manipulation
- **Raspberry Pi Foundation** - For the amazing single-board computers
- **All Contributors** - For improvements and fixes

---

<p align="center">
  Made with ❤️ in UAE, Al Ain
</p>
