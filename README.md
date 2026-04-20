# HomeNet - Parental Network Controller 🌐

<p align="center">
  <strong>🛡️ Block kids' internet 11 PM - 12 AM | Monitor traffic | AI Assistant included</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Platform-Raspberry%20Pi%203-orange.svg" alt="Platform">
  <img src="https://img.shields.io/badge/UI-Bilingual%20(EN/AR)-purple.svg" alt="UI">
  <img src="https://img.shields.io/badge/AI-GLM5%20Flash-blue.svg" alt="AI">
</p>

<p align="center">
  Proudly developed in UAE, Al Ain 🇦🇪
</p>

---

## ⚡ 3-Minute Quick Start

### Step 1: Flash Raspberry Pi OS
```
Download Raspberry Pi Imager → Select Raspberry Pi OS Lite
Enable SSH, configure WiFi, set hostname: HomeNet
```

### Step 2: One-Command Install
```bash
ssh pi@HomeNet.local
curl -sL https://raw.githubusercontent.com/AbduF/HomeNet/main/install.sh | bash
```

### Step 3: Access & Login
```
🌐 http://HomeNet.local:5000
🔐 Login: admin / 123456
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| ⏰ **Time Blocking** | Block 11 PM - 12 AM (customizable) |
| 📱 **Host Control** | See all devices, block/unblock any |
| 📊 **Traffic Monitor** | Real-time bandwidth, top consumers |
| 🎮 **App Blocking** | Gaming, Social, Streaming categories |
| 🤖 **AI Assistant** | Smart help powered by GLM5 |
| 🔔 **Smart Alerts** | New device, high traffic notifications |
| 🌐 **Bilingual** | English & Arabic with RTL |
| 📧 **Email Alerts** | SMTP notifications |

---

## 🤖 AI-Powered Parental Help

Ask questions in plain English or Arabic:

```
"Block gaming apps for my kids"
"Set up 11 PM bedtime blocking"
"Why is my Pi slow?"
"How to block TikTok?"
"Add trusted device"
```

**Get age-appropriate advice:**
- Age 6-7: No gaming, 1hr streaming
- Age 8-12: Light gaming (1hr), supervised
- Age 13-15: Moderate gaming (2hr)
- Age 16+: Guided access with education focus

---

## 🖥️ System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Raspberry Pi** | Pi 3 | Pi 4 |
| **RAM** | 512MB | 1GB+ |
| **Storage** | 8GB SD | 16GB+ |
| **OS** | Raspberry Pi OS Lite | Raspberry Pi OS |
| **Network** | Ethernet | Ethernet |

---

## 📦 Installation

### One-Command Install (Recommended)
```bash
curl -sL https://raw.githubusercontent.com/AbduF/HomeNet/main/install.sh | bash
```

### Manual Install
```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install dependencies
sudo apt install -y python3 python3-pip python3-venv iptables git

# 3. Clone and setup
git clone https://github.com/AbduF/HomeNet.git ~/HomeNet
cd ~/HomeNet
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Run
python3 main.py
```

---

## 🔧 Configuration

### Default Blocking Schedule
| Time | Action |
|------|--------|
| 11:00 PM | Internet blocked for kids |
| 12:00 AM | Internet restored |

### Blocked Apps (Default)
| Category | Apps |
|----------|------|
| Gaming | Steam, Roblox, Minecraft, Xbox, PlayStation |
| Social | TikTok, Instagram, Snapchat, Facebook |
| Streaming | Netflix, YouTube, Disney+, Spotify |

### Environment Variables
```bash
export GLM_API_KEY=your_api_key   # Optional: Enable AI
export SCAN_INTERVAL=300          # Scan every 5 minutes (Pi 3 optimized)
export LOG_LEVEL=INFO            # Debug logging
```

---

## 🛠️ Management Commands

```bash
# Service management
sudo systemctl start homonet     # Start
sudo systemctl stop homonet      # Stop
sudo systemctl restart homonet   # Restart
sudo systemctl status homonet     # Check status

# View logs
tail -f ~/HomeNet/logs/homenet.log

# Reset password
sqlite3 ~/HomeNet/homenet.db "UPDATE users SET password_hash='8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92' WHERE username='admin';"
```

---

## 📐 Network Setup

### Recommended: Pi as Gateway
```
Internet → Raspberry Pi → Switch → Home Devices
```

Enable gateway:
```bash
sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
```

### Alternative: Pi Inline
Place Pi between router and family devices for monitoring-only.

---

## 🤖 Enable AI Assistant

1. Get free GLM5 API key: https://open.bigmodel.cn/
2. Add to config.json:
```json
{
  "glm_api_key": "your_key_here"
}
```
3. Restart service

**Free tier: 1000 calls/day**

---

## 📋 Default Login

| Field | Value |
|-------|-------|
| Username | `admin` |
| Password | `123456` |

⚠️ **Change password immediately after first login!**

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Can't login | Reset: `sqlite3 ~/HomeNet/homenet.db "UPDATE..."` |
| Pi slow | Increase scan interval to 5 min |
| No alerts | Configure SMTP in Settings |
| Blocking not working | Check iptables: `sudo iptables -L HOMENET` |

---

## 📁 Project Structure

```
HomeNet/
├── main.py           # Entry point
├── app.py           # Main app
├── install.sh       # 3-step installer
├── requirements.txt  # Dependencies
├── core/            # Backend modules
│   ├── database.py
│   ├── network.py
│   ├── monitor.py
│   ├── blocker.py
│   ├── ai_assistant.py   # 🤖 AI
│   └── speedtest.py
├── gui/             # Frontend views
│   ├── dashboard.py
│   ├── hosts.py
│   ├── traffic.py
│   ├── rules.py
│   ├── alerts.py
│   ├── ai_help.py        # 🤖 AI Help
│   └── settings.py
└── logs/           # Application logs
```

---

## 📄 License

MIT License - Free for personal and commercial use.

---

## 📧 Support

**Developer**: AbduF
**Email**: abdalfaqeeh@gmail.com
**Location**: Al Ain, UAE 🇦🇪
**GitHub**: https://github.com/AbduF/HomeNet

---

<p align="center">
  Made with ❤️ for families in UAE and around the world
</p>
