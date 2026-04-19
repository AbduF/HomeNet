#!/bin/bash
# HomeNet Installer for Raspberry Pi 3 - Fixed Version
set -e

echo "🔧 Installing system dependencies..."
sudo apt update && sudo apt install -y nmap python3-pip python3-venv libatlas-base-dev

echo "📦 Cloning HomeNet..."
git clone https://github.com/AbduF/HomeNet.git
cd HomeNet

echo "🐍 Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🔐 Setting Python capabilities for nmap (non-root scan)..."
sudo setcap cap_net_raw,cap_net_admin=eip $(which python3)

echo "✅ Installation complete! Run with: python3 main.py"
echo "🇦🇪 Proudly developed in UAE / Al Ain"