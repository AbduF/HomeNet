\# 🌐 HomeNet — Parental Network Controller



!\[Version](https://img.shields.io/badge/version-1.0.0-blue)

!\[Python](https://img.shields.io/badge/Python-3.8%2B-green)

!\[License](https://img.shields.io/badge/License-MIT-lightgrey)

!\[UAE](https://img.shields.io/badge/Made%20in-UAE%20🇦🇪-red)



\*\*Proudly developed in UAE 🇦🇪\*\*



HomeNet is a powerful parental network control application that gives you full visibility and control over your home network. Monitor all connected devices, block unwanted content, set time-based internet restrictions, and receive real-time alerts — all from a modern bilingual (Arabic/English) interface.



\---



\## ✨ Features



| Feature | Description |

|---------|-------------|

| 🕐 \*\*Time Blocking\*\* | Block internet access during specific hours (e.g., 11 PM – 12 PM) |

| 📊 \*\*Traffic Monitoring\*\* | Real-time traffic utilization, volume per host |

| 🎮 \*\*Content Blocking\*\* | Block gaming, social media, and streaming categories |

| ️ \*\*Host Discovery\*\* | Auto-detect all devices with OS \& hardware details |

| 🔔 \*\*System Alerts\*\* | Notifications for new hosts and high traffic |

| 🌍 \*\*Bilingual UI\*\* | Full Arabic \& English support with RTL layout |

| 📡 \*\*Speed Test\*\* | Built-in internet speed test \& connection check |

|  \*\*Admin Panel\*\* | Change credentials, add recovery email, reset password |

|  \*\*CLI + GUI\*\* | Command-line interface AND modern graphical interface |

|  \*\*Multi-Platform\*\* | Works on PC, Laptop, and Raspberry Pi 3 |



\---

\## ️ Network Diagram



┌───────────┐ ┌──────────────────────────┐ ┌──────────────┐

│ │ │ HomeNet Controller │ │ │

│ Internet │─────►│ (Firewall + Monitoring) │◄────►│ LAN Devices │

│ (WAN) │ │ 🛡️ Network Security │ │ 💻🖥️📺 │

│ │ └──────────────────────────┘ └──────────────┘

└───────────┘ │

▼

┌────────────────┐

│ Managed Switch │

│ 🔌🔌 │

└────────────────┘





⚡ 5-Minute Installation Guide

For Raspberry Pi 3 / Linux PC

Steps

1 git clone https://github.com/AbduF/HomeNet.git \&\& cd HomeNet

2 sudo bash setup.sh

3 sudo systemctl start homenetservice

4 homenet-gui or homenet-cli

5 Login: admin / 123456 → Change password immediately!

🎯 Key Features Summary

Feature

CLI Command

GUI Location

Network Scan

scan

Hosts → Scan Network

View Hosts

hosts

Hosts page

Block Host

block 192.168.1.x

Hosts → Block button

Block Gaming

block gaming

Blocking → Gaming toggle

Block Social

block social

Blocking → Social toggle

Block Streaming

block streaming

Blocking → Streaming toggle

Time Blocking

timerules set 23:00 00:00

Time Rules page

Speed Test

speedtest

Speed Test page

Traffic Monitor

monitor start

Traffic → Start Monitoring

Alerts

alerts

Alerts page

Change Password

system change password

System → Admin Settings

Set Email

settings email x@y.com

System → Recovery Email

🔒 Security Notes

Change default password (123456) immediately after first login

Set up a recovery email for password reset

Run the service as root (required for iptables/firewall)

Keep the Raspberry Pi in a secure location

Regularly update via git pull
