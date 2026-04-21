import subprocess

def block_traffic(start_time="23:00", end_time="00:00"):
    try:
        subprocess.run([
            "sudo", "iptables", "-A", "OUTPUT", "-p", "tcp",
            "--dport", "80", "-m", "time",
            "--timestart", start_time, "--timestop", end_time, "-j", "DROP"
        ], check=True)
        subprocess.run([
            "sudo", "iptables", "-A", "OUTPUT", "-p", "tcp",
            "--dport", "443", "-m", "time",
            "--timestart", start_time, "--timestop", end_time, "-j", "DROP"
        ], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def unblock_traffic():
    try:
        subprocess.run(["sudo", "iptables", "-F"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def list_hosts():
    try:
        result = subprocess.run(["arp", "-a"], capture_output=True, text=True, check=True)
        return result.stdout.splitlines()
    except subprocess.CalledProcessError:
        return []