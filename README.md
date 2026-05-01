HomeNet 🏡

Free, Open-Source Internet Control for Families
Proudly developed in the UAE 



✨ Features

✅ Time-Based Blocking: Automatically block social media, gaming, and adult websites after 10 PM.
✅ Bilingual UI: Full English/Arabic support with RTL alignment.
✅ Dashboard:





Real-time connected hosts (IP, MAC, hostname, OS).



Traffic monitoring (per host, historical trends).



Alerts for new hosts, blocked attempts, and high traffic.



DNS block logs (domains, timestamps, IPs).
✅ Lightweight: Optimized for Raspberry Pi 3/4 or any Linux laptop.
✅ Secure:



Authentication (Basic Auth).



HTTPS-ready (use with Nginx + Certbot).



Input validation (IP/MAC addresses).
✅ Works with Existing Router: No need to disable router DHCP. Uses DNS blocking and firewall rules to manage the network.



📥 Installation (5 Steps)

Prerequisites





Raspberry Pi 3/4 or Linux laptop (Debian/Ubuntu).



Python 3.6+.



**sudo access**.



Static IP for your Raspberry Pi (recommended).



Step 1: Clone the Repository

git clone https://github.com/AbduF/HomeNet.git
cd HomeNet



Step 2: Set Up a Virtual Environment

python3 -m venv venv
source venv/bin/activate  # On Windows: `venv\Scripts\activate`



Step 3: Install Dependencies

pip install -r requirements.txt



Step 4: Install and Configure Firewall

To allow external access to the app, install and configure the firewall to enable port 5000:

Install ufw (Uncomplicated Firewall)

sudo apt update
sudo apt install ufw -y

Enable ufw and Allow Port 5000

sudo ufw enable
sudo ufw allow 5000

Verify the Rule

sudo ufw status

You should see 5000 listed as allowed.



Step 5: Configure Router to Use Raspberry Pi as DNS Server

To ensure all devices on your network use HomeNet for DNS blocking, configure your router to use your Raspberry Pi as the DNS server:





Find your Raspberry Pi's IP address:

 hostname -I

 Example output: 192.168.1.100



Log in to your router's admin panel (usually http://192.168.1.1).



Find the DNS settings (usually under LAN, DHCP, or Internet).



Set the primary DNS server to your Raspberry Pi's IP (e.g., 192.168.1.100).



Save and restart the router.



⚠️ Note: If your router does not allow changing DNS settings, you can manually configure each device to use your Raspberry Pi as its DNS server.



Step 6: Run HomeNet

python app.py

You should see:

 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)



Step 7: Set Up DNS Blocking and Firewall

Trigger the setup via the API:

curl -X POST -u admin:123456 http://localhost:5000/api/setup

This will:





Configure dnsmasq for DNS blocking.



Set up firewall rules (time-based blocking after 10 PM).



Step 8: Scan for Connected Hosts

To populate the Hosts section of the dashboard, run:

curl -X POST -u admin:123456 http://localhost:5000/api/scan_hosts

This will scan your network for connected devices and add them to the database.



Step 9: Access the Dashboard from Another PC





Open a web browser on another PC (on the same network) and navigate to:

 http://<raspberry-pi-ip>:5000/

 Replace <raspberry-pi-ip> with the IP address of your Raspberry Pi (e.g., http://192.168.1.100:5000/).



Log in using the default credentials:





Username: admin



Password: 123456 (or the password you configured in .env).





🔍 Troubleshooting

1. Can't Connect to the App?





Check if the app is running:
Run ps aux | grep python to confirm the Flask process is active.



Check the IP address:
Run hostname -I on your Raspberry Pi to find its IP address.



Check the firewall:
Ensure your firewall allows traffic on port 5000:

sudo ufw statusIf port `5000` is not listed, run:

sudo ufw allow 5000



Check the network:
Ensure your computer and Raspberry Pi are on the same network.



2. Port Already in Use?

If you see an error like:

OSError: [Errno 98] Address already in use

Run:

sudo lsof -i :5000

to find the process using port 5000, then kill it:

sudo kill <PID>

Replace <PID> with the process ID from the lsof output.



3. DNS Blocking Not Working?





Test DNS blocking:
Try accessing a blocked domain (e.g., facebook.com) from a connected device. If it loads, DNS blocking is not working.



Check dnsmasq configuration:

sudo cat /etc/dnsmasq.confEnsure the `address=/{domain}/0.0.0.0` lines are present for blocked domains.



Check dnsmasq logs:

sudo tail -f /var/log/dnsmasq.log



**Restart dnsmasq**:

sudo systemctl restart dnsmasq



Verify router DNS settings:
Ensure your router is using your Raspberry Pi's IP as the DNS server.



4. Hosts Not Appearing in Dashboard?





Manually scan for hosts:
Run:

curl -X POST -u admin:123456 http://localhost:5000/api/scan_hosts



**Check arp-scan**:
Ensure arp-scan is installed:

sudo apt install arp-scan -y



Run arp-scan manually:

sudo arp-scan --localnetIf this works, the issue may be with permissions in the `get_connected_hosts()` function.



5. Firewall Rules Not Working?





Check iptables rules:

sudo iptables -L -n -v



Test time-based blocking:
Wait until 10 PM and try accessing a website. It should be blocked.



Check firewall logs:

sudo dmesg | grep "HOMENET BLOCKED"



6. Alternative: Use iptables Directly

If ufw is not available, use iptables to allow port 5000:

sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT

To make the rule persistent:

sudo apt install iptables-persistent -y
sudo netfilter-persistent save





📌 Summary







Step



Action



Command/URL





1



Clone the repository



git clone https://github.com/AbduF/HomeNet.git





2



Set up virtual environment



python3 -m venv venv and source venv/bin/activate





3



Install dependencies



pip install -r requirements.txt





4



Install and enable firewall



sudo apt install ufw -y, sudo ufw enable, sudo ufw allow 5000





5



Configure router DNS



Set Raspberry Pi IP as DNS server in router settings





6



Run HomeNet



python app.py





7



Set up DNS and firewall



curl -X POST -u admin:123456 http://localhost:5000/api/setup





8



Scan for hosts



curl -X POST -u admin:123456 http://localhost:5000/api/scan_hosts





9



Access the dashboard



http://<raspberry-pi-ip>:5000/





10



Log in



Username: admin, Password: 123456





🛡 Security Recommendations





Change Default Credentials:

Update the .env file with a strong password:



Use HTTPS:

Set up Nginx + Certbot for HTTPS access. Follow a guide like Certbot's instructions.



Static IP for Raspberry Pi:

Configure a static IP for your Raspberry Pi to prevent it from changing after a reboot.



Backup Configurations:

Backup your dnsmasq.conf and iptables rules:





🔹 How It Works Without DHCP





DNS Blocking:





dnsmasq runs on your Raspberry Pi and blocks unwanted domains (e.g., social media, gaming, adult sites).



Your router is configured to use your Raspberry Pi as the DNS server, so all devices on the network use dnsmasq for DNS resolution.



Firewall Rules:





iptables blocks all internet traffic after 10 PM until 12 AM.



Local network traffic (e.g., between devices on your LAN) is still allowed.



Host Detection:





The app uses arp-scan to detect connected devices on your network and displays them in the dashboard.



Hosts are stored in the SQLite database for tracking and monitoring.





Would you like me to provide a script to automate the setup (e.g., a setup.sh file) or help with any other part? For example, I can create a script to:





Install dependencies (ufw, dnsmasq, arp-scan).



Configure the router DNS settings automatically (if supported).



Set up the firewall and dnsmasq with a single command.

