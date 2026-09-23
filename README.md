# mac_address_scanner

![ci](https://github.com/pinsql/mac_address_scanner/actions/workflows/ci.yml/badge.svg)

who's on the wire? sweeps your local network with `arp-scan` and lists every device's IP, MAC and vendor. macOS and Linux.

## install

```bash
brew install arp-scan          # macOS
sudo apt install arp-scan      # Debian / Ubuntu / Kali
```

no python dependencies, stdlib only.

## use

```bash
./mac_scanner.py               # auto-detects your interface
./mac_scanner.py -i wlan0      # pick one
./mac_scanner.py --json | jq -r '.[] | "\(.ip) \(.vendor)"'
```

it calls `sudo arp-scan` for you, so expect a password prompt.

| flag | what it does |
|---|---|
| `-i`, `--iface` | interface to scan (default: Wi-Fi on macOS, default-route interface on Linux) |
| `--json` | JSON output on stdout, the progress banner goes to stderr |

```text
==========================================
💻 Wi-Fi Network MAC Scanner
🕶️  Written by: pinsql
🕒 Time: 2026-09-24 02:14:07 EAT
==========================================

📡 Devices Found: 3

 [1] 📍 IP: 192.168.1.1     🧬 MAC: aa:bb:cc:dd:ee:ff  🏷️  TP-LINK TECHNOLOGIES CO.,LTD.
 [2] 📍 IP: 192.168.1.20    🧬 MAC: 11:22:33:44:55:66  🏷️  Apple, Inc.
 [3] 📍 IP: 192.168.1.33    🧬 MAC: 02:42:ac:11:00:02  🏷️  (Unknown: locally administered)

✅ Done scanning. Stay stealthy. 😎
==========================================
```

## security notes

- no shell anywhere: every command runs from an argument list.
- `--iface` only accepts real-looking interface names, so it can't be used to inject commands or extra `arp-scan` options.

## tests

```bash
pip install pytest && pytest -q
```

`arp-scan` and `sudo` are mocked, so the tests run anywhere.

## legal

only scan networks you own or have written permission to test. no scope, no scan.
