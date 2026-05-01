
# HomeNet 🏡
**Free, Open-Source Internet Control for Families**
Proudly developed in the UAE 🇦🇪

---

## **✨ Features**
✅ **Time-Based Blocking**: Automatically block social media, gaming, and adult websites **after 10 PM**.
✅ **Bilingual UI**: Full **English/Arabic** support with RTL alignment.
✅ **Dashboard**:
   - Real-time **connected hosts** (IP, MAC, hostname, OS).
   - **Traffic monitoring** (per host, historical trends).
   - **Alerts** for new hosts, blocked attempts, and high traffic.
   - **DNS block logs** (domains, timestamps, IPs).
✅ **Lightweight**: Optimized for **Raspberry Pi 3/4** or any Linux laptop.
✅ **Secure**:
   - **Authentication** (Basic Auth).
   - **HTTPS-ready** (use with Nginx + Certbot).
   - **Input validation** (IP/MAC addresses).

---

📥 Installation (6 Steps)✨

Prerequisites


Raspberry Pi 3/4 or Linux laptop (Debian/Ubuntu).



Python 3.6+.



sudo access.

---

Step 1: Clone the Repository✅

git clone https://github.com/AbduF/HomeNet.git
cd HomeNet



Step 2: Set Up a Virtual Environment✅

python3 -m venv venv

source venv/bin/activate  
# On Windows: `venv\Scripts\activate



Step 3: Install Dependencies✅

pip install -r requirements.txt

Step 4: Install and Configure Firewall✅

To allow external access to the app, install and configure the firewall to enable port 5000:

Install ufw (Uncomplicated Firewall)

sudo apt update

sudo apt install ufw -y

Enable ufw and Allow Port 5000✅

sudo ufw enable

sudo ufw allow 5000

Verify the Rule

sudo ufw status

You should see 5000 listed as allowed.



Step 5: Run HomeNet✅

python app.py

You should see:

 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)



Step 6: Access the Dashboard from Another PC✅



Find your Raspberry Pi's IP address:

 hostname -I

 Example output: 192.168.1.100



Open a web browser on another PC (on the same network) and navigate to:✅

 http://<raspberry-pi-ip>:5000/

 Replace <raspberry-pi-ip> with the IP address from step 1 (e.g., http://192.168.1.100:5000/).



Log in using the default credentials✨:✅


Username: admin



Password: 123456 (or the password you configured in .env).


---


✨🔍 Troubleshooting Access Issues

1. Can't Connect to the App?



Check if the app is running✅
Run ps aux | grep python to confirm the Flask process is active.



Check the IP address✅
Run hostname -I on your Raspberry Pi to find its IP address.



Check the firewall✅
Ensure your firewall allows traffic on port 5000:

sudo ufw status

If port 5000 is not listed, run:

sudo ufw allow 5000



Check the network✅
Ensure your computer and Raspberry Pi are on the same network.



2. Port Already in Use?

If you see an error like:

OSError: [Errno 98] Address already in use

Run:

sudo lsof -i :5000

to find the process using port 5000, then kill it:

sudo kill <PID>

Replace <PID> with the process ID from the lsof output.



3. Alternative: Use iptables Directly

If ufw is not available, use iptables to allow port 5000:

sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT

To make the rule persistent:

sudo apt install iptables-persistent -y
sudo netfilter-persistent save

---

Email to abdalfaqeeh@gmail.com if you have any feedback and comments 