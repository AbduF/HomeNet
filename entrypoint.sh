#!/bin/bash

# HomeNet Docker Entry Point
# This script runs when the container starts

# Set up environment variables
export FLASK_APP=app.py
export FLASK_ENV=production

# Configure dnsmasq
cp /app/tmp/dnsmasq.conf /etc/dnsmasq.conf
cp /app/tmp/blocklists.conf /etc/dnsmasq.d/blocklists.conf

# Start dnsmasq
dnsmasq --no-daemon &

# Start Nginx
nginx -g "daemon off;" &

# Set up iptables rules
iptables -F
iptables -X
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -p udp --dport 53 -j ACCEPT
iptables -A OUTPUT -p tcp --dport 53 -j ACCEPT
iptables -A OUTPUT -p tcp --dport 80 -j ACCEPT
iptables -A OUTPUT -p tcp --dport 443 -j ACCEPT
iptables -A OUTPUT -p icmp -j ACCEPT
iptables -A OUTPUT -d 192.168.0.0/16 -j ACCEPT
iptables -A OUTPUT -d 10.0.0.0/8 -j ACCEPT
iptables -A OUTPUT -d 172.16.0.0/12 -j ACCEPT
iptables -A OUTPUT -m time --timestart 22:00 --timestop 00:00 -j DROP
iptables -A OUTPUT -m time --timestart 22:00 --timestop 00:00 -j LOG --log-prefix "HOMENET BLOCKED: "

# Start Flask app with Gunicorn
exec gunicorn -w 2 -b 0.0.0.0:5000 app:app