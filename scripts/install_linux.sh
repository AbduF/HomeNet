#!/bin/bash
# 🌐 HomeNet Installer for Linux (Ubuntu/Debian/Raspberry Pi OS)
# Proudly Developed in UAE 🇦🇪
set -e

echo "🌐 HomeNet Linux Installer"
echo "🔧 This script requires sudo privileges for network & firewall setup."

# Check root
if [ "$EUID" -ne 0 ]; then
  echo "❌ Please run as root or with: sudo bash $0"
  exit 1
fi

echo "📦 Installing system dependencies..."
apt update && apt install -y python3 python3-pip python3-venv git iptables nmap net-tools curl python3-tk

# Navigate to project root
cd "$(dirname "$0")/.."

echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Make scripts executable
chmod +x scripts/install_linux.sh 2>/dev/null || true

echo ""
echo "✅ Installation complete!"
echo "🚀 Run GUI: sudo ./venv/bin/python3 src/main.py --gui"
echo "🖥️  Run CLI: sudo ./venv/bin/python3 src/main.py --cli"
echo "💡 Tip: Enable persistent firewall rules with: sudo apt install iptables-persistent"
echo "🇦🇪 HomeNet is ready. Enjoy secure family networking!"