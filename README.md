
### `README.md`
**Location:** `/home/home/HomeNet/README.md`

```markdown
# 🛡️ NetGuard - Parental Home Network Control

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Raspberry Pi](https://img.shields.io/badge/Raspberry_Pi-3%2B%2B-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A comprehensive, web-based parental control solution designed for the Raspberry Pi. Monitor your home network, manage internet access schedules, and block specific websites with an intuitive bilingual (Arabic/English) interface.

🇦🇪 **Proudly Developed in the United Arab Emirates**

---

## 🌟 Features

NetGuard provides powerful tools to keep your family safe online:

*   **Bilingual Interface**: Full support for English and Arabic with a seamless toggle switch.
*   **Secure Login System**: Protect your settings with a secure Admin dashboard.
*   **Time-Based Blocking**: Automatically restricts internet access during specified hours (Default: 10:00 PM - 5:00 AM).
*   **Manual URL Blocking**: Add specific websites (e.g., social media, games) to a blocklist instantly.
*   **Real-Time Monitoring**: View connected devices, download speeds, and network traffic volume live.
*   **Responsive Design**: Works perfectly on desktops, tablets, and mobile phones.
*   **Easy Deployment**: One-command installation script for Raspberry Pi.

---

## 🖥️ Dashboard Preview

*   **Login Page**: Secure entry point (Default: `admin` / `123456`).
*   **Control Panel**: Toggle switches for Social Media, Games, and Unwanted Sites.
*   **Stats Grid**: Live view of Host Count and Internet Speed.

---

## 📋 Prerequisites

*   **Hardware**: Raspberry Pi 3, 4, or Zero W.
*   **Operating System**: Raspberry Pi OS (Legacy or Bullseye).
*   **Network**: Ethernet or Wi-Fi connection.

---

## 🚀 Installation & Setup

Choose one of the two methods below to install NetGuard.

### Option A: Automated Installation (Recommended)
This method automatically sets up the environment, installs dependencies, and configures the background service to start on boot.

```bash
# 1. Clone the repository
git clone https://github.com/AbduF/HomeNet.git
cd HomeNet

# 2. Run the installer script
chmod +x install.sh
sudo ./install.sh
```

---

### Option B: Manual Installation
Use this method if you prefer to set up the Python environment manually.

```bash
# 1. Clone the repository
git clone https://github.com/AbduF/HomeNet.git
cd HomeNet

# 2. Create a Virtual Environment
sudo python3 -m venv venv

# 3. Fix permissions (Important: Ensures you own the venv folder)
sudo chown -R $(whoami):$(whoami) venv

# 4. Activate the Virtual Environment
source venv/bin/activate

# 5. Install Dependencies
pip install flask psutil

# 6. Run the Application
python app.py
```

*Note: When running manually, press `Ctrl+C` to stop the app. If you want the app to run in the background and restart automatically, use Option A.*

---

## 🌍 Accessing the Dashboard

Once the installation is complete (or you have run the app manually), open a web browser on any device connected to the same network and navigate to:

```
http://<YOUR_PI_IP_ADDRESS>:5000
```
*(Note: You can find your Pi's IP address by running `hostname -I` in the terminal.)*

### Step 4: Login

Use the default credentials to access the dashboard. **Please change the password immediately after logging in.**

*   **Username:** `admin`
*   **Password:** `123456`

---

## 🛠️ Usage

1.  **Check Status**: The top card shows if the network is "Active" or "Blocked" based on the time schedule.
2.  **Block Websites**: Scroll to "Manual URL Blocking", type a domain (e.g., `tiktok.com`), and click **Block**.
3.  **Change Language**: Click the **"English / العربية"** button in the top right corner.
4.  **Manage Security**: Click **"Change Password"** to update your admin credentials.

---

## 📂 Project Structure

```text
HomeNet/
├── app.py                # Main Flask Application
├── install.sh            # Automated Installation Script
├── requirements.txt      # Python Dependencies
├── templates/
│   ├── login.html        # Login Page
│   └── dashboard.html    # Main Dashboard
├── blocklist.txt         # List of manually blocked URLs
├── credentials.json      # Secure storage for username/password
└── venv/                 # Virtual Environment (Created during install)
```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

---

## 📜 License

This project is licensed under the MIT License.

---

## 🌏 Acknowledgments

This project was designed and developed to promote digital safety and well-being within the household.

**Developed with ❤️ in the United Arab Emirates**
```
