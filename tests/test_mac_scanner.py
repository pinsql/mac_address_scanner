import argparse
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import mac_scanner as ms

SAMPLE = """Interface: eth0, type: EN10MB, MAC: de:ad:be:ef:00:01, IPv4: 192.168.1.5
Starting arp-scan 1.10.0 with 256 hosts (https://github.com/royhills/arp-scan)
192.168.1.1\taa:bb:cc:dd:ee:ff\tTP-LINK TECHNOLOGIES CO.,LTD.
192.168.1.20\t11:22:33:44:55:66\tApple, Inc.
192.168.1.20\t11:22:33:44:55:66\tApple, Inc. (DUP: 2)
192.168.1.33\t02:42:ac:11:00:02\t(Unknown: locally administered)

4 packets received by filter, 0 packets dropped by kernel
Ending arp-scan 1.10.0: 256 hosts scanned in 1.9 seconds (134.74 hosts/sec). 3 responded
"""


def test_parse_results_reads_hosts_and_vendors():
    devices = ms.parse_results(SAMPLE)
    assert [d["ip"] for d in devices] == ["192.168.1.1", "192.168.1.20", "192.168.1.33"]
    assert devices[0]["vendor"] == "TP-LINK TECHNOLOGIES CO.,LTD."


def test_parse_results_drops_duplicates():
    macs = [d["mac"] for d in ms.parse_results(SAMPLE)]
    assert macs.count("11:22:33:44:55:66") == 1


def test_parse_results_handles_space_separated_output():
    devices = ms.parse_results("10.0.0.1  aa:aa:aa:aa:aa:aa\n")
    assert devices == [{"ip": "10.0.0.1", "mac": "aa:aa:aa:aa:aa:aa", "vendor": "unknown"}]


@pytest.mark.parametrize("name", ["eth0", "en0", "wlan0", "wlp2s0", "br-1a2b3c"])
def test_interface_name_accepts_real_names(name):
    assert ms.interface_name(name) == name


@pytest.mark.parametrize("name", ["eth0; id", "$(reboot)", "-e", "--localnet", "a" * 16, ""])
def test_interface_name_rejects_injection_and_options(name):
    with pytest.raises(argparse.ArgumentTypeError):
        ms.interface_name(name)


def test_scan_network_uses_argument_list_without_shell(monkeypatch):
    seen = {}

    def fake_check_output(cmd, **kwargs):
        seen["cmd"], seen["kwargs"] = cmd, kwargs
        return SAMPLE.encode()

    monkeypatch.setattr(ms.subprocess, "check_output", fake_check_output)
    assert ms.scan_network("eth0") == SAMPLE
    assert seen["cmd"] == ["sudo", "arp-scan", "-I", "eth0", "--localnet"]
    assert not seen["kwargs"].get("shell")


def test_scan_network_exits_cleanly_when_arp_scan_fails(monkeypatch):
    def boom(cmd, **kwargs):
        raise subprocess.CalledProcessError(1, cmd)

    monkeypatch.setattr(ms.subprocess, "check_output", boom)
    with pytest.raises(SystemExit):
        ms.scan_network("eth0")


def test_get_interface_linux_uses_default_route(monkeypatch):
    monkeypatch.setattr(ms.platform, "system", lambda: "Linux")
    monkeypatch.setattr(ms.subprocess, "check_output",
                        lambda cmd, **kw: b"default via 192.168.1.1 dev wlp2s0 proto dhcp metric 600\n")
    assert ms.get_interface() == "wlp2s0"


def test_get_interface_macos_finds_wifi(monkeypatch):
    monkeypatch.setattr(ms.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(ms.subprocess, "check_output",
                        lambda cmd, **kw: b"Hardware Port: Ethernet\nDevice: en0\n\nHardware Port: Wi-Fi\nDevice: en1\n")
    assert ms.get_interface() == "en1"


def test_get_interface_falls_back_when_tools_missing(monkeypatch):
    def missing(cmd, **kw):
        raise FileNotFoundError(cmd[0])

    monkeypatch.setattr(ms.subprocess, "check_output", missing)
    monkeypatch.setattr(ms.platform, "system", lambda: "Linux")
    assert ms.get_interface() == "eth0"
    monkeypatch.setattr(ms.platform, "system", lambda: "Darwin")
    assert ms.get_interface() == "en0"


def test_main_json_output_is_clean(monkeypatch, capsys):
    monkeypatch.setattr(ms, "scan_network", lambda iface: SAMPLE)
    ms.main(["-i", "eth0", "--json"])
    devices = json.loads(capsys.readouterr().out)
    assert len(devices) == 3 and devices[1]["vendor"] == "Apple, Inc."
