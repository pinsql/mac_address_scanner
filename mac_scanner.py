#!/usr/bin/env python3

import subprocess
import re
from datetime import datetime
import os

# Written by PinSteve 🕶️
# Network MAC Scanner – Hack Like a Pro 💻🔥

def get_interface():
    # Try to guess your Wi-Fi interface (common on macOS)
    try:
        result = subprocess.check_output("networksetup -listallhardwareports", shell=True).decode()
        wifi_section = re.search(r"Hardware Port: Wi-Fi\nDevice: (en\d)", result)
        if wifi_section:
            return wifi_section.group(1)
    except:
        pass
    return "en0"  # Default to en0 if detection fails

def scan_network(interface):
    print(f"\n🔥 Scanning the network on interface: {interface} 🔍")
    try:
        output = subprocess.check_output(f"sudo arp-scan -I {interface} --localnet", shell=True).decode()
        return output
    except subprocess.CalledProcessError as e:
        print("⚠️ Error running arp-scan. Make sure it's installed and you have sudo privileges.")
        exit(1)

def parse_results(scan_output):
    devices = []
    lines = scan_output.splitlines()
    for line in lines:
        # Skip irrelevant lines
        if re.match(r"^\d{1,3}(\.\d{1,3}){3}", line):
            parts = line.split()
            if len(parts) >= 2:
                ip = parts[0]
                mac = parts[1]
                devices.append((ip, mac))
    return devices

def print_results(devices):
    os.system("clear")
    print("==========================================")
    print("💻 Wi-Fi Network MAC Scanner")
    print("🕶️  Written by: pinsteve")
    print("🕒 Time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("==========================================")
    print(f"\n📡 Devices Found: {len(devices)}\n")
    
    for i, (ip, mac) in enumerate(devices, start=1):
        print(f" [{i}] 📍 IP: {ip:<15} 🧬 MAC: {mac}")
    
    print("\n✅ Done scanning. Stay stealthy. 😎")
    print("==========================================\n")

if __name__ == "__main__":
    interface = get_interface()
    scan_output = scan_network(interface)
    devices = parse_results(scan_output)
    print_results(devices)
