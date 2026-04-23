#!/bin/bash
#
# HomeNet Setup Script
# Parental Network Controller
# Developed in UAE, Al Ain
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "  ╔════════════════════════════════════════════╗"
echo "  ║     HomeNet - Parental Network Controller   ║"
echo "  ║         Proudly developed in UAE           ║"
echo "  ╚════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}Warning: Running as root is not recommended.${NC}"
    echo "Press Ctrl+C to cancel, or Enter to continue..."
    read
fi

# Detect OS
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
    else
        OS="unknown"
    fi
}

# Install dependencies for Debian/Ubuntu
install_debian() {
    echo -e "${GREEN}[*] Installing dependencies for Debian/Ubuntu...${NC}"

    sudo apt update
    sudo apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        iptables \
        git \
        dnsutils \
        net-tools \
        wireless-tools \
        iw \
        nmap \
        arp-scan

    echo -e "${GREEN}[+] Dependencies installed successfully!${NC}"
}

# Install dependencies for Raspberry Pi OS
install_raspbian() {
    echo -e "${GREEN}[*] Installing dependencies for Raspberry Pi OS...${NC}"

    sudo apt update
    sudo apt upgrade -y
    sudo apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        iptables \
        iptables-persistent \
        git \
        dnsutils \
        net-tools \
        wireless-tools \
        iw \
        nmap \
        arp-scan \
        vim \
        screen

    echo -e "${GREEN}[+] Raspberry Pi dependencies installed!${NC}"
}

# Install Python packages
install_python() {
    echo -e "${GREEN}[*] Installing Python packages...${NC}"

    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate

    # Upgrade pip
    pip install --upgrade pip

    # Install requirements
    pip install -r requirements.txt

    echo -e "${GREEN}[+] Python packages installed!${NC}"
}

# Setup systemd service
setup_service() {
    echo -e "${GREEN}[*] Setting up systemd service...${NC}"

    cat > HomeNet.service << 'EOF'
[Unit]
Description=HomeNet - Parental Network Controller
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/venv/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo cp HomeNet.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable HomeNet

    echo -e "${GREEN}[+] Systemd service configured!${NC}"
}

# Configure iptables permissions
setup_iptables() {
    echo -e "${GREEN}[*] Configuring iptables permissions...${NC}"

    echo "$USER ALL=(ALL) NOPASSWD: /sbin/iptables, /sbin/ip6tables" | sudo tee /etc/sudoers.d/homenet
    sudo chmod 440 /etc/sudoers.d/homenet

    echo -e "${GREEN}[+] iptables permissions configured!${NC}"
}

# Create directories
setup_directories() {
    echo -e "${GREEN}[*] Creating directories...${NC}"

    mkdir -p logs
    mkdir -p data
    mkdir -p backups

    echo -e "${GREEN}[+] Directories created!${NC}"
}

# Print next steps
print_next_steps() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║              Setup Complete!                      ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo ""
    echo "1. Activate the virtual environment:"
    echo "   ${GREEN}source venv/bin/activate${NC}"
    echo ""
    echo "2. Run HomeNet:"
    echo "   ${GREEN}python3 main.py${NC}"
    echo ""
    echo "3. Or run as a service:"
    echo "   ${GREEN}sudo systemctl start HomeNet${NC}"
    echo ""
    echo "4. Access the application:"
    echo "   ${GREEN}http://localhost:5000${NC}"
    echo ""
    echo "5. Default login:"
    echo "   ${GREEN}Username: admin${NC}"
    echo "   ${GREEN}Password: 123456${NC}"
    echo ""
    echo -e "${RED}⚠️  IMPORTANT: Change the default password after first login!${NC}"
    echo ""
    echo "For more information, see README.md"
    echo ""
}

# Main installation
main() {
    detect_os

    echo -e "${BLUE}[*] Detected OS: $OS${NC}"

    # Install dependencies based on OS
    case $OS in
        debian|ubuntu|linuxmint|pop)
            install_debian
            ;;
        raspbian|raspberrypi)
            install_raspbian
            ;;
        fedora|centos|rhel)
            echo -e "${YELLOW}[*] Red Hat-based system detected. Installing dependencies...${NC}"
            sudo dnf install -y python3 python3-pip python3-virtualenv iptables git nmap
            ;;
        arch|manjaro)
            echo -e "${YELLOW}[*] Arch-based system detected. Installing dependencies...${NC}"
            sudo pacman -S python python-pip python-virtualenv iptables git nmap
            ;;
        *)
            echo -e "${YELLOW}[*] Unknown OS. Attempting generic installation...${NC}"
            install_debian
            ;;
    esac

    # Install Python packages
    install_python

    # Setup directories
    setup_directories

    # Setup iptables permissions (if on Linux)
    if [ "$(uname)" = "Linux" ]; then
        setup_iptables
    fi

    # Ask about systemd service
    echo ""
    read -p "Setup systemd service for auto-start? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_service
    fi

    # Print next steps
    print_next_steps
}

# Run main
main "$@"
