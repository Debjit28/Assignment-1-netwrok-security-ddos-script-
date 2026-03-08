"""
Wireshark Capture Helper
=========================
Automates packet capture using tshark (Wireshark CLI) during an attack simulation.
Saves .pcap files that can be opened in Wireshark for visual analysis.

Requirements:
    pip install scapy --break-system-packages
    sudo apt install tshark   (or wireshark on Windows/macOS)

Usage:
    sudo python capture_helper.py --attack syn --target 127.0.0.1
    sudo python capture_helper.py --attack udp --target 127.0.0.1
"""

import subprocess
import threading
import time
import os
import sys
import argparse

CAPTURE_DIR = os.path.join(os.path.dirname(__file__), "..", "capture")
os.makedirs(CAPTURE_DIR, exist_ok=True)


def start_capture(output_file: str, interface: str, duration: int):
    """Start tshark capture in background."""
    cmd = [
        "tshark",
        "-i", interface,
        "-a", f"duration:{duration}",
        "-w", output_file,
    ]
    print(f"[*] Starting tshark capture on interface '{interface}' for {duration}s")
    print(f"[*] Saving to: {output_file}\n")
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return proc


def run_attack(attack_type: str, target: str, count: int):
    """Launch the chosen attack script as a subprocess."""
    script_dir = os.path.join(os.path.dirname(__file__), "..", "attacks")
    scripts = {
        "syn": os.path.join(script_dir, "syn_flood.py"),
        "udp": os.path.join(script_dir, "udp_flood.py"),
    }
    script = scripts.get(attack_type)
    if not script:
        print(f"[!] Unknown attack type: {attack_type}")
        sys.exit(1)

    cmd = [sys.executable, script, "--target", target, "--count", str(count)]
    print(f"[*] Launching {attack_type.upper()} flood attack...\n")
    subprocess.run(cmd)


def print_analysis_tips(attack_type: str, target: str, pcap_file: str):
    tips = {
        "syn": [
            f"tcp.flags.syn == 1 && tcp.flags.ack == 0",
            f"ip.dst == {target} && tcp.flags.syn == 1",
            "tcp.analysis.retransmission",
        ],
        "udp": [
            f"udp && ip.dst == {target}",
            f"icmp.type == 3",          # Port Unreachable
            f"ip.dst == {target}",
        ],
    }

    print("\n" + "="*55)
    print("  WIRESHARK ANALYSIS GUIDE")
    print("="*55)
    print(f"  Open file: {pcap_file}")
    print(f"\n  Recommended display filters for {attack_type.upper()} flood:")
    for f in tips.get(attack_type, []):
        print(f"    → {f}")

    print("\n  Useful Wireshark menus:")
    print("    Statistics → IO Graph          (bandwidth over time)")
    print("    Statistics → Conversations     (top source IPs)")
    print("    Statistics → Protocol Hierarchy(traffic breakdown)")
    print("    Analyze    → Expert Info       (anomalies & errors)")
    print("="*55 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Capture + Attack Helper")
    parser.add_argument("--attack",    choices=["syn", "udp"], required=True)
    parser.add_argument("--target",    default="127.0.0.1")
    parser.add_argument("--count",     type=int, default=500)
    parser.add_argument("--interface", default="lo",  help="Network interface (lo, eth0, etc.)")
    parser.add_argument("--duration",  type=int, default=30, help="Capture duration in seconds")
    args = parser.parse_args()

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    pcap_file = os.path.join(CAPTURE_DIR, f"{args.attack}_flood_{timestamp}.pcap")

    # Start capture
    capture_proc = start_capture(pcap_file, args.interface, args.duration)
    time.sleep(1)  # Give tshark time to start

    # Run attack
    run_attack(args.attack, args.target, args.count)

    # Wait for capture to finish
    print("\n[*] Waiting for capture to complete...")
    capture_proc.wait()

    print(f"[✓] Capture saved: {pcap_file}")
    print_analysis_tips(args.attack, args.target, pcap_file)
