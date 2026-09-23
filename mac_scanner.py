#!/usr/bin/env python3

import argparse
import platform
import re
import subprocess
from datetime import datetime
import sys

# Written by pinsql 🕶️
# Network MAC Scanner – Hack Like a Pro 💻🔥

# Interface names are short and boring. Must start with a letter/digit so
# nothing like "-e" can sneak into arp-scan as an extra option.
IFACE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,14}$")

def interface_name(value):
    if not IFACE_RE.match(value):
        raise argparse.ArgumentTypeError(f"'{value}' doesn't look like an interface name")
    return value

def get_interface():
    # Guess the interface that actually talks to the network
    is_mac = platform.system() == "Darwin"
    try:
        if is_mac:
            result = subprocess.check_output(["networksetup", "-listallhardwareports"]).decode()
            wifi_section = re.search(r"Hardware Port: Wi-Fi\nDevice: (en\d+)", result)
            if wifi_section:
                return wifi_section.group(1)
        else:
            # Linux: whatever the default route goes out of
            result = subprocess.check_output(["ip", "route", "show", "default"]).decode()
            match = re.search(r"\bdev (\S+)", result)
            if match:
                return match.group(1)
    except (OSError, subprocess.CalledProcessError):
        pass
    return "en0" if is_mac else "eth0"  # Default if detection fails

def scan_network(interface):
    print(f"\n🔥 Scanning the network on interface: {interface} 🔍")
    # Argument list, no shell: the interface name can't smuggle in extra commands
    try:
        output = subprocess.check_output(["sudo", "arp-scan", "-I", interface, "--localnet"]).decode()
        return output
    except (OSError, subprocess.CalledProcessError):
        print("⚠️ Error running arp-scan. Make sure it's installed and you have sudo privileges.")
        sys.exit(1)

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

def clear_screen():
    # ANSI clear instead of os.system("clear"): no shell, and pipes/logs stay clean
    if sys.stdout.isatty():
        print("\033[2J\033[H", end="")

def print_results(devices):
    clear_screen()
    print("==========================================")
    print("💻 Wi-Fi Network MAC Scanner")
    print("🕶️  Written by: pinsql")
    print("🕒 Time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("==========================================")
    print(f"\n📡 Devices Found: {len(devices)}\n")
    
    for i, (ip, mac) in enumerate(devices, start=1):
        print(f" [{i}] 📍 IP: {ip:<15} 🧬 MAC: {mac}")
    
    print("\n✅ Done scanning. Stay stealthy. 😎")
    print("==========================================\n")

def get_arguments(argv=None):
    parser = argparse.ArgumentParser(description="Who's on the wire? MAC + vendor sweep via arp-scan")
    parser.add_argument("-i", "--iface", type=interface_name, help="Interface to scan (default: auto-detect)")
    return parser.parse_args(argv)

def main(argv=None):
    args = get_arguments(argv)
    interface = args.iface or get_interface()
    scan_output = scan_network(interface)
    devices = parse_results(scan_output)
    print_results(devices)

if __name__ == "__main__":
    main()
