cat > README.md << 'EOF'
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

## **📥 Installation (3 Steps)**

### **Prerequisites**
- **Raspberry Pi 3/4** or **Linux laptop** (Debian/Ubuntu).
- **Python 3.6+**.
- **`sudo` access**.

---

### **Step 1: Clone the Repository**
```bash
git clone https://github.com/AbduF/HomeNet.git
cd HomeNet

### **Step 2: Set Up a Virtual Environment**
python3 -m venv venv
source venv/bin/activate  # On Windows: `venv\Scripts\activate

### **Step 3:  Install Dependencies**
pip install -r requirements.txt

### **Step 4:  Run HomeNet App**
python app.py