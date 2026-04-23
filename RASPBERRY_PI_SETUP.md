# HomeNet Raspberry Pi 3 Installation Guide

## Complete Step-by-Step Guide (5 Minutes)

This guide will help you set up HomeNet on a Raspberry Pi 3 in your home network.

### Prerequisites

- Raspberry Pi 3 (or 3B+)
- 16GB+ microSD card
- Raspberry Pi OS Lite or Desktop
- Ethernet cable (recommended) or WiFi
- Power supply (5V 2.5A)
- SSH client (Windows: PuTTY, macOS/Linux: Terminal)

---

## Step 1: Flash the SD Card (1 minute)

### Download Tools
1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Install and launch it

### Configure Raspberry Pi OS
1. Click **"Choose OS"** → Select **"Raspberry Pi OS Lite (64-bit)"** (for headless) or **"Raspberry Pi OS (64-bit)"** (for desktop)

2. Click **"Choose Storage"** → Select your SD card

3. Click the **gear icon** (advanced options) and configure:
   ```
   ✓ Set hostname: HomeNet
   ✓ Enable SSH: ✓
     ✓ Allow password-authentication: ✓
     ✓ Set password for default user: your-secure-password
   ✓ Configure WiFi (if not using Ethernet):
     ✓ SSID: YourWiFiName
     ✓ Password: YourWiFiPassword
     ✓ WiFi country: AE (for UAE)
   ✓ Set locale settings:
     ✓ Timezone: Asia/Dubai
     ✓ Keyboard layout: us
   ```

4. Click **"Write"** and wait for completion

---

## Step 2: Initial Connection (1 minute)

### For Ethernet Users
1. Insert SD card and power on the Pi
2. Wait 1-2 minutes for boot
3. Connect via SSH:
   ```bash
   ssh pi@HomeNet.local
   # Password: your-secure-password
   ```

### For WiFi Users
1. Same as above, but Pi will connect to WiFi automatically

### First Login Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Set hostname
sudo hostnamectl set-hostname HomeNet
sudo sed -i 's/raspberrypi/HomeNet/g' /etc/hosts

# Verify hostname
hostname
# Should output: HomeNet
```

---

## Step 3: Install HomeNet (2 minutes)

### Clone the Repository
```bash
cd ~
git clone https://github.com/AbduF/HomeNet.git
cd HomeNet
```

### Run Automatic Setup
```bash
chmod +x setup.sh
./setup.sh
```

### OR Manual Installation
```bash
# Install dependencies
sudo apt install -y python3-pip python3-venv iptables git

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
mkdir -p logs data backups
```

---

## Step 4: Configure Permissions (0.5 minutes)

### Allow iptables Access
```bash
# Create sudoers file for iptables
echo "pi ALL=(ALL) NOPASSWD: /sbin/iptables, /sbin/ip6tables" | sudo tee /etc/sudoers.d/homenet
sudo chmod 440 /etc/sudoers.d/homenet
```

### Verify iptables Works
```bash
sudo iptables -L
# Should show empty chains or default rules
```

---

## Step 5: Run HomeNet (0.5 minutes)

### Test Run
```bash
source venv/bin/activate
python3 main.py
```

You should see:
```
HomeNet - Parental Network Controller
Starting application...
```

### Create Auto-Start Service
```bash
# Create service file
cat > HomeNet.service << 'EOF'
[Unit]
Description=HomeNet - Parental Network Controller
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/HomeNet
ExecStart=/home/pi/HomeNet/venv/bin/python3 /home/pi/HomeNet/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Install service
sudo cp HomeNet.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable HomeNet
```

### Start the Service
```bash
# Start now
sudo systemctl start HomeNet

# Check status
sudo systemctl status HomeNet

# View logs
sudo journalctl -u HomeNet -f
```

---

## Network Setup for Blocking

### Option A: Pi as Gateway (Full Control)

This makes the Raspberry Pi the main router:

```
Internet → Raspberry Pi → Switch → Home Devices
```

```bash
# Enable IP forwarding
sudo sysctl -w net.ipv4.ip_forward=1
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf

# Configure NAT
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables -A FORWARD -i eth0 -o eth1 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i eth1 -o eth0 -j ACCEPT

# Save rules
sudo apt install -y iptables-persistent
sudo sh -c "iptables-save > /etc/iptables.rules"
```

### Option B: Pi Inline (Bridge Mode)

Place Pi between router and devices:

```
Router → Raspberry Pi → Switch → Devices
```

```bash
# Create bridge
sudo apt install -y bridge-utils

# Configure /etc/network/interfaces
sudo nano /etc/network/interfaces
```

Add:
```
auto br0
iface br0 inet static
    address 192.168.1.254
    netmask 255.255.255.0
    bridge_ports eth0 eth1
```

### Option C: Pi as Access Point

```bash
# Install hostapd
sudo apt install -y hostapd

# Configure as AP
sudo nano /etc/hostapd/hostapd.conf
```

Add:
```
interface=wlan0
bridge=br0
ssid=HomeNet-Controlled
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=YourSecurePassword
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
```

---

## Access HomeNet

### From Local Network
```
Open browser: http://HomeNet.local:5000
Or: http://192.168.1.x:5000
```

### Default Login
```
Username: admin
Password: 123456
```

### First-Time Configuration
1. **Change Password**: Settings → Account
2. **Scan Network**: Click "Scan Network" button
3. **Configure Blocking**: Rules → Add schedule (11 PM - 12 AM)
4. **Set Alerts**: Settings → Email (optional)

---

## Troubleshooting

### Can't Connect via SSH
```bash
# Check if SSH is enabled
ls /boot/ssh

# If not, create empty file
sudo touch /boot/ssh

# Reboot
sudo reboot
```

### WiFi Not Connecting
```bash
# Check WiFi status
iwconfig
rfkill list wifi

# Scan for networks
sudo iwlist wlan0 scan | grep ESSID

# Check WiFi config
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```

### HomeNet Won't Start
```bash
# Check for errors
source venv/bin/activate
python3 main.py --debug

# Check logs
tail -f logs/homenet.log

# Check port availability
sudo netstat -tlnp | grep 5000
```

### Blocking Not Working
```bash
# Check iptables
sudo iptables -L -n -v

# Check if HOMENET chain exists
sudo iptables -L HOMENET -n

# Manually test blocking
sudo iptables -A HOMENET -d 8.8.8.8 -j DROP
ping 8.8.8.8  # Should timeout
sudo iptables -D HOMENET -d 8.8.8.8 -j DROP
```

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `sudo systemctl start HomeNet` | Start service |
| `sudo systemctl stop HomeNet` | Stop service |
| `sudo systemctl restart HomeNet` | Restart service |
| `sudo systemctl status HomeNet` | Check status |
| `sudo journalctl -u HomeNet -f` | View logs |
| `tail -f ~/HomeNet/logs/homenet.log` | Application logs |
| `sudo iptables -L -n -v` | View firewall rules |

---

## Network Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         INTERNET                                  │
│                            🌐                                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Ethernet
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   RASPBERRY PI 3                                │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    HomeNet App                             │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │  │
│  │  │Dashboard│  │ Hosts   │  │ Traffic │  │ Rules   │        │  │
│  │  │  📊     │  │  💻     │  │  📈     │  │  🛡️     │        │  │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │  │
│  │                                                              │  │
│  │  ┌─────────────────────────────────────────────┐           │  │
│  │  │         iptables Blocking Engine             │           │  │
│  │  │  Schedule: 11 PM - 12 AM (Block All)         │           │  │
│  │  │  Apps: Gaming, Social, Streaming             │           │  │
│  │  └─────────────────────────────────────────────┘           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                            │                                      │
│  Network Interface:        │                                      │
│  • eth0: 192.168.1.x (WAN) │                                      │
│  • eth1: 192.168.2.1 (LAN) │                                      │
└────────────────────────────┼────────────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    │     SWITCH      │
                    └────────┬────────┘
                             │
    ┌─────────┬─────────┬────┴────┬─────────┬─────────┐
    │         │         │         │         │         │
    ▼         ▼         ▼         ▼         ▼         ▼
┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
│ Kids' │ │ Kids' │ │Parents│ │ Smart │ │ Gaming│ │ Smart │
│Phone  │ │Laptop │ │Phone  │ │  TV   │ │Console│ │Speaker│
│📱     │ │💻     │ │📱     │ │📺     │ │🎮     │ │🔊     │
└───────┘ └───────┘ └───────┘ └───────┘ └───────┘ └───────┘
   ❌        ❌        ✓         ✓         ❌        ✓
(Blocked) (Blocked) (Allowed) (Allowed) (Blocked) (Allowed)

LEGEND:
❌ = Blocked during schedule
✓ = Always allowed
```

---

## Support

For help or issues:
- **Email**: abdalfaqeeh@gmail.com
- **GitHub Issues**: https://github.com/AbduF/HomeNet/issues
- **Documentation**: https://github.com/AbduF/HomeNet/wiki

---

<p align="center">
  Made with ❤️ in UAE, Al Ain 🇦🇪
</p>
