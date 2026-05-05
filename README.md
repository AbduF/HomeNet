🛡️ NetGuard - Parental Home Network Control

A comprehensive, web-based parental control solution designed for the Raspberry Pi. 
Monitor your home network, manage internet access schedules, and block specific websites with an intuitive bilingual (Arabic/English) interface.

Proudly Developed in the 🌟United Arab Emirates🌟

🌟 Features
NetGuard provides powerful tools to keep your family safe online:

Bilingual Interface: Full support for English and Arabic with a seamless toggle switch.
Secure Login System: Protect your settings with a secure Admin dashboard.
Time-Based Blocking: Automatically restricts internet access during specified hours (Default: 10:00 PM - 5:00 AM).
Manual URL Blocking: Add specific websites (e.g., social media, games) to a blocklist instantly.
Real-Time Monitoring: View connected devices, download speeds, and network traffic volume live.
Responsive Design: Works perfectly on desktops, tablets, and mobile phones.
Easy Deployment: One-command installation script for Raspberry Pi.

🖥️ Dashboard Preview

🌟Login Page: Secure entry point (Default: admin / 123456).

🌟Control Panel: Toggle switches for Social Media, Games, and Unwanted Sites.

🌟Stats Grid: Live view of Host Count and Internet Speed.

📋 Prerequisites

🌟Hardware: Raspberry Pi 3, 4, or Zero W.
🌟Operating System: Raspberry Pi OS (Legacy or Bullseye).
🌟Network: Ethernet or Wi-Fi connection.

🚀 Installation & Setup
Follow these steps to get NetGuard running on your Raspberry Pi in minutes.

🌟Step 1: Clone the Repository

Open your terminal on the Raspberry Pi and run:

git clone https://github.com/AbduF/HomeNet.gitcd HomeNet

🌟Step 2: Run the Installer

The repository includes an automated script that installs all dependencies (Flask, psutil) and sets up the system service to start on boot.

bash

chmod +x install.sh
sudo ./install.sh

🌟Step 3: Access the Dashboard
Once the installation is complete, open a web browser on any device connected to the same network and navigate to:

text

http://<YOUR_PI_IP_ADDRESS>:5000

(Note: You can find your Pi's IP address by running hostname -I in the terminal.)

🌟Step 4: Login

Use the default credentials to access the dashboard. Please change the password immediately after logging in.

Username: admin
Password: 123456

🛠️ Usage

Check Status: The top card shows if the network is "Active" or "Blocked" based on the time schedule.

Block Websites: Scroll to "Manual URL Blocking", type a domain (e.g., tiktok.com), and click Block.

Change Language: Click the "English / العربية" button in the top right corner.

Manage Security: Click "Change Password" to update your admin credentials.

📂 Project Structure
text
HomeNet/
├── app.py                # Main Flask Application
├── install.sh            # Automated Installation Script
├── requirements.txt      # Python Dependencies
├── templates/
│   ├── login.html        # Login Page
│   └── dashboard.html    # Main Dashboard
├── blocklist.txt         # List of manually blocked URLs
└── credentials.json      # Secure storage for username/password

🤝 Contributing
Contributions, issues, and feature requests are welcome!

Fork the repository.
Create your feature branch (git checkout -b feature/AmazingFeature).
Commit your changes (git commit -m 'Add some AmazingFeature').
Push to the branch (git push origin feature/AmazingFeature).
Open a Pull Request.

📜 License
This project is licensed under the MIT License.

🌏 Acknowledgments

This project was designed and developed to promote digital safety and well-being within the household.

Developed with ❤️ in the United Arab Emirates
