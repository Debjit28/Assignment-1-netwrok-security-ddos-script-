# 🛡️ DDoS Attack Simulation — Educational Lab

> **Assignment 1 | Network Security Lab**  
> **Date:** 8/3/2025 | **Tools:** Python · Scapy · Wireshark

---

## ⚠️ Disclaimer

This project is strictly for **educational and academic purposes**.  
Run these simulations **only** on your own machine (`localhost`) or an isolated lab network you own.  
Launching DDoS attacks against any system without explicit written permission is **illegal** under the IT Act and cybercrime laws.

---

## 📌 Overview

This project simulates two common DDoS (Distributed Denial of Service) attacks using Python and the Scapy packet-crafting library, and provides guidance for capturing and analyzing the traffic in Wireshark.

| Attack | Layer | Protocol | Mechanism |
|---|---|---|---|
| SYN Flood | Transport (L4) | TCP | Exhausts server connection table with half-open connections |
| UDP Flood | Transport (L4) | UDP | Overwhelms bandwidth/CPU with random high-volume UDP traffic |

---

## 📁 Project Structure

```
ddos-simulation/
├── attacks/
│   ├── syn_flood.py          # TCP SYN Flood simulation
│   └── udp_flood.py          # UDP Flood simulation
├── capture/
│   └── capture_helper.py     # Auto-capture with tshark + attack launcher
├── requirements.txt
└── README.md
```

---

## 🔧 Setup & Installation

### 1. Install Python dependencies
```bash
pip install -r requirements.txt
# or
pip install scapy --break-system-packages
```

### 2. Install Wireshark / tshark
```bash
# Ubuntu / Debian
sudo apt update && sudo apt install wireshark tshark -y

# macOS (Homebrew)
brew install wireshark

# Windows
# Download from https://www.wireshark.org/download.html
```

### 3. Allow non-root packet capture (Linux)
```bash
sudo setcap cap_net_raw=eip /usr/bin/python3
# OR simply run attack scripts with sudo
```

---

## 🚀 Running the Attacks

> All examples target `127.0.0.1` (localhost). Never target external IPs.

### Attack 1 — SYN Flood

```bash
sudo python attacks/syn_flood.py --target 127.0.0.1 --port 80 --count 500
```

**Options:**

| Flag | Default | Description |
|---|---|---|
| `--target` | `127.0.0.1` | Target IP address |
| `--port` | `80` | Target TCP port |
| `--count` | `500` | Number of SYN packets |
| `--delay` | `0` | Seconds between packets |

---

### Attack 2 — UDP Flood

```bash
sudo python attacks/udp_flood.py --target 127.0.0.1 --count 500 --size 1024
```

**Options:**

| Flag | Default | Description |
|---|---|---|
| `--target` | `127.0.0.1` | Target IP address |
| `--port` | `0` (random) | Target UDP port (0 = randomize) |
| `--count` | `500` | Number of UDP packets |
| `--size` | `1024` | Payload size in bytes |
| `--delay` | `0` | Seconds between packets |

---

### 🎯 Combined: Auto-Capture + Attack

Runs the attack AND captures a `.pcap` file simultaneously:

```bash
# SYN Flood + capture
sudo python capture/capture_helper.py --attack syn --target 127.0.0.1 --count 500

# UDP Flood + capture  
sudo python capture/capture_helper.py --attack udp --target 127.0.0.1 --count 500
```

PCAP files are saved to `capture/` with timestamps (e.g. `syn_flood_20250803_143022.pcap`).

---

## 🔬 Wireshark Analysis

### Opening the capture
```
File → Open → capture/<filename>.pcap
```

---

### SYN Flood — Analysis

#### Display Filters
```
# Show only SYN packets (no ACK) — the flood traffic
tcp.flags.syn == 1 && tcp.flags.ack == 0

# Filter by destination
ip.dst == 127.0.0.1 && tcp.flags.syn == 1

# See retransmissions (server retry)
tcp.analysis.retransmission
```

#### What to Look For
- **Massive volume** of TCP SYN packets from many different source IPs
- **Server replies** with SYN-ACK to spoofed/unreachable addresses (no ACK follows)
- **Half-open connections** — no complete 3-way handshake visible
- **No RST/FIN** packets — connections never close cleanly

#### Wireshark Views
```
Statistics → Conversations (TCP tab)   → see top source IPs
Statistics → IO Graph                  → bandwidth spike
Analyze    → Expert Info               → "Connection Establishment" warnings
```

---

### UDP Flood — Analysis

#### Display Filters
```
# Show all UDP to target
udp && ip.dst == 127.0.0.1

# ICMP "Port Unreachable" replies from target
icmp.type == 3 && icmp.code == 3

# Overall traffic to/from target
ip.addr == 127.0.0.1
```

#### What to Look For
- **High volume** UDP packets from many source IPs to random ports
- **ICMP Port Unreachable** responses — server rejecting packets on closed ports
- **No application data** pattern — purely random payloads
- **Bandwidth spike** visible in IO Graph

#### Wireshark Views
```
Statistics → Protocol Hierarchy        → UDP % of total traffic
Statistics → IO Graph                  → bandwidth over time
Statistics → Conversations (UDP tab)   → busiest source IPs
```

---

## 💡 How Each Attack Works

### SYN Flood — TCP 3-Way Handshake Exploitation

```
Normal TCP Handshake:
  Client  ──SYN──►  Server   (Client wants to connect)
  Client  ◄─SYN-ACK─  Server (Server confirms, waits)
  Client  ──ACK──►  Server   (Handshake complete ✓)

SYN Flood:
  Attacker ──SYN (fake IP)──►  Server  (x 10,000s)
  Attacker ◄─SYN-ACK─  Server          (Server waits... and waits...)
  [ACK never arrives — connection stays half-open]
  [Server's connection table fills up → real users blocked]
```

**Key properties of our simulation:**
- Randomized source IPs using `RandIP()` (spoofing)
- Random source ports with `RandShort()`
- Only `SYN` flag set — never completes handshake

---

### UDP Flood — Bandwidth & CPU Exhaustion

```
Attacker ──[1024B random UDP]──►  Server:port  (x 10,000s)
                         Server checks: any app listening on this port?
                              → No  → sends ICMP Port Unreachable back
                              → Yes → app overwhelmed with junk data
[Network bandwidth saturated + CPU busy processing/rejecting packets]
```

**Key properties of our simulation:**
- Random destination ports (or fixed target port)
- Random payload bytes to maximize bandwidth usage
- Spoofed source IPs to prevent easy blocking

---

## 📊 Expected Wireshark Observations

| Metric | SYN Flood | UDP Flood |
|---|---|---|
| Protocol | TCP | UDP |
| Packets/sec | Very high | Very high |
| Source IPs | Many (spoofed) | Many (spoofed) |
| Payload | None (just header) | Random bytes |
| Server response | SYN-ACK (then timeout) | ICMP Port Unreachable |
| Bandwidth impact | Moderate | High |
| CPU impact | High (state tracking) | Moderate |

---

## 🧪 Lab Setup Recommendations

For a realistic lab environment:

1. **Use VirtualBox/VMware** — run attacker and victim as separate VMs on a host-only network
2. **Run a simple web server on victim**: `python -m http.server 80`
3. **Monitor victim resources**: `watch -n1 ss -s` (connection stats) or `htop`
4. **Capture on victim side** for cleaner results

---

## 📚 References

- [Scapy Documentation](https://scapy.readthedocs.io/)
- [Wireshark Display Filters](https://wiki.wireshark.org/DisplayFilters)
- [TCP SYN Flood (RFC 4987)](https://datatracker.ietf.org/doc/html/rfc4987)
- [CERT Advisory on UDP Flooding](https://resources.sei.cmu.edu/library/asset-view.cfm?assetid=496172)

---

*Made for Assignment 1 — Network Security | Python + Wireshark Lab*
