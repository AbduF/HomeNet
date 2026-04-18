# 🌐 HomeNet - Parental Network Controller
**Proudly Developed in UAE 🇦🇪** | Python 3 | CLI + Modern GUI | Arabic & English

## 🎯 Features
- ⏰ Time-based internet blocking (23:00-00:00)
- 📊 Real-time host discovery, traffic volume & OS/HW detection
- 🚫 Block gaming, social media, streaming via IP/DNS rules
- 🔔 Alerts for new hosts & high traffic spikes
- 🌐 Internet speed test & connectivity monitor
- 🔐 Secure auth (default: `admin`/`123456`), password reset via email
- 🌍 Bilingual: English & Arabic (RTL support)

## 🛠️ Quick Install (5 mins)
```bash
sudo apt update && sudo apt install -y python3-pip git iptables
git clone https://github.com/AbduF/HomeNet.git
cd HomeNet
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
sudo python3 src/main.py --gui