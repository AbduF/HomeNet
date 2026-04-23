# Push HomeNet to GitHub

## Step-by-Step Instructions

### 1. Create GitHub Account
If you don't have one, sign up at [github.com](https://github.com)

### 2. Create New Repository
1. Click the **"+"** icon (top right) → **"New repository"**
2. Configure:
   - **Owner**: AbduF (or your username)
   - **Repository name**: `HomeNet`
   - **Description**: "Parental Network Controller with time blocking, traffic monitoring & bilingual UI. Proudly developed in UAE/Al Ain"
   - **Public** ✓
   - **Add a README file**: ✓
   - **Add .gitignore**: Python
3. Click **"Create repository"**

### 3. Push Existing Code

Navigate to your HomeNet folder and run:

```bash
cd ~/HomeNet

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - HomeNet v1.0.0
- Time-based internet blocking (11 PM - 12 AM)
- Network host monitoring
- Traffic analytics
- App and domain blocking
- Real-time alerts
- Bilingual support (English/Arabic)
- Raspberry Pi 3 ready"

# Add remote
git remote add origin https://github.com/AbduF/HomeNet.git

# Push
git branch -M main
git push -u origin main
```

### 4. Verify Upload
- Go to: `https://github.com/AbduF/HomeNet`
- All files should appear

### 5. Enable GitHub Pages (Optional)
1. Go to repository **Settings**
2. Navigate to **Pages**
3. Source: **Deploy from a branch**
4. Branch: **main** / **(root)**
5. Click **Save**

Your README will be live at: `https://AbduF.github.io/HomeNet`

---

## Repository Structure

```
HomeNet/
├── .gitignore           # Git ignore file
├── README.md            # Main documentation
├── LICENSE              # MIT License
├── requirements.txt     # Python dependencies
├── main.py              # Application entry point
├── app.py               # Main application class
├── setup.sh             # Installation script
├── HomeNet.service      # Systemd service file
├── RASPBERRY_PI_SETUP.md # Pi installation guide
├── GITHUB_PUSH.md        # This file
├── SPEC.md              # Project specification
│
├── core/                # Core modules
│   ├── __init__.py
│   ├── database.py      # SQLite database
│   ├── config.py         # Configuration
│   ├── network.py       # Network scanning
│   ├── monitor.py       # Traffic monitoring
│   ├── blocker.py       # iptables blocking
│   └── speedtest.py     # Speed test
│
├── gui/                 # GUI components
│   ├── __init__.py
│   ├── login.py         # Login window
│   ├── main_window.py   # Main window
│   ├── dashboard.py     # Dashboard view
│   ├── hosts.py         # Host management
│   ├── traffic.py       # Traffic view
│   ├── rules.py         # Rules config
│   ├── alerts.py        # Alerts view
│   └── settings.py      # Settings view
│
├── logs/                # Application logs
├── data/                # Data storage
└── backups/             # Backup directory
```

---

## Badges for Your README

Add these badges to make your repo look professional:

```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux|Raspberry%20Pi-orange.svg)](https://www.raspberrypi.com/)
[![UI](https://img.shields.io/badge/UI-Bilingual%20(EN/AR)-purple.svg)]()
```

---

## Update Your Repository

When you make changes:

```bash
cd ~/HomeNet
git add .
git commit -m "Description of changes"
git push
```

---

## Community Guidelines

1. **Star** the repository if you find it useful
2. **Fork** to create your own version
3. **Submit issues** for bugs or feature requests
4. **Pull requests** are welcome for improvements

---

<p align="center">
  🌐 Proudly developed in UAE, Al Ain 🇦🇪
</p>
