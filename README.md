# 🛡️ DDoS Attack Simulation — Beginner's Learning Lab

> **Assignment 1 | Network Security**  
> **Tools Used:** Python · Scapy · Wireshark

---

## ⚠️ Important — Read This First

This project is **strictly for learning**. All simulations run on your **own computer only** (`127.0.0.1` = your own machine talking to itself — completely safe).

> Attacking any computer, server, or network you don't own is **illegal** and can result in criminal charges. This lab exists so you can *understand* how attacks work — not to misuse them.

---

## 🤔 Wait — What Even Is a DDoS Attack?

Don't worry if you've never heard these terms before. Let's start from zero.

### What is a "server"?
A server is just a computer that provides a service — like a website, a login page, or a game. When you open a website, your computer sends a request to a server, and the server sends back the page.

### What is a DoS attack?
**DoS = Denial of Service.**
Imagine a restaurant with 10 tables. Now imagine 1000 fake customers walk in, occupy every table, and never order food. Real customers can't get in. The restaurant is "denied" to real customers — not because it broke, but because it's overwhelmed with fake requests.

That's exactly what a DoS attack does to a computer server.

### What makes it "DDoS"?
**DDoS = *Distributed* Denial of Service.**
Instead of one attacker, imagine thousands of computers (or fake IPs) all flooding the server at once. That's "distributed" — it comes from many sources, making it harder to block.

---

## 📦 What This Project Contains

This project simulates **2 types of DDoS attacks** on your own machine so you can see exactly what happens at the network level — using Wireshark to watch every packet in real time.

```
ddos-simulation/
├── attacks/
│   ├── syn_flood.py        ← Attack 1: SYN Flood (abuses TCP handshake)
│   └── udp_flood.py        ← Attack 2: UDP Flood (blasts junk traffic)
├── capture/
│   └── capture_helper.py   ← Bonus: auto-record traffic while attacking
├── requirements.txt        ← Python libraries needed
└── README.md               ← This file
```

---

## 🧠 Understanding the Two Attacks (Plain English)

### Attack 1 — SYN Flood

**The concept — TCP handshake:**

When your browser connects to a website, it does a 3-step "handshake":

```
You          →  "Hello, I want to connect" (SYN)
Server       →  "Sure! I'm ready, confirm?" (SYN-ACK)
You          →  "Confirmed!" (ACK)
✅ Connection established
```

The server sets aside memory for each connection it's waiting to confirm. It can only hold so many at once.

**What SYN Flood does:**

```
Attacker (fake IP)  →  "Hello!" (SYN)        ← sends thousands of these
Server              →  "Sure! Confirm?"        ← server waits...
[Attacker never replies — it's a fake IP]     ← ACK never comes
[Server keeps waiting, memory fills up]
[Real users try to connect → server is full → DENIED]
```

The attacker uses **fake (spoofed) IP addresses** so the server can never reach them back.
The server is stuck holding thousands of half-open conversations.

---

### Attack 2 — UDP Flood

**The concept — UDP packets:**

UDP is a way of sending data without first asking for permission. It's like someone just throwing packages at your door non-stop, and you have to pick each one up, check if it's for you, and if not — write "return to sender."

**What UDP Flood does:**

```
Attacker  →  [1000 bytes of random junk] to random port  (x thousands)
Server    →  checks: "is anyone home on this port?"
              → No  → replies "port unreachable" (ICMP message)
              → repeat x thousands of times
[Server's bandwidth and CPU consumed just dealing with junk]
[Real traffic can't get through]
```

No handshake needed — just blast data. Simple but effective at using up bandwidth.

---

## 🔧 Step-by-Step Setup (Complete Beginner Guide)

### Step 1 — Make sure Python is installed

Open a terminal (Command Prompt on Windows, Terminal on Mac/Linux) and type:
```bash
python --version
```
You should see something like `Python 3.10.x`. If not, download Python from [python.org](https://www.python.org/downloads/).

---

### Step 2 — Download this project

If you have Git installed:
```bash
git clone https://github.com/YOUR_USERNAME/ddos-simulation.git
cd ddos-simulation
```

Or download the ZIP from GitHub → "Code" → "Download ZIP", then unzip it.

---

### Step 3 — Install Scapy (the packet tool)

Scapy is a Python library that lets you craft and send custom network packets — the core tool for both attacks.

```bash
pip install scapy
```

If that gives an error on Linux:
```bash
pip install scapy --break-system-packages
```

---

### Step 4 — Install Wireshark

Wireshark is a free tool that lets you **see every packet** traveling through your network — like an X-ray for internet traffic. We'll use it to watch the attacks happen in real time.

**Windows / macOS:**
Download from 👉 [https://www.wireshark.org/download.html](https://www.wireshark.org/download.html)
Install with all default options.

**Ubuntu / Debian Linux:**
```bash
sudo apt update && sudo apt install wireshark tshark -y
```
When asked "Should non-superusers be able to capture packets?" → Select **Yes**.

---

### Step 5 — Open Wireshark BEFORE running attacks

1. Open Wireshark
2. In the list of interfaces, double-click **"Loopback"** (Windows) or **"lo"** (Linux/Mac)
3. You'll see a live feed of packets — leave it running
4. Now run the attacks in a separate terminal window

> **What is "Loopback"?** It's the network interface your computer uses to talk to *itself*. `127.0.0.1` is the loopback address — traffic sent here never actually goes to the internet. It's the safest possible sandbox.

---

## 🚀 Running the Attacks

Open a terminal in the project folder. On Linux/Mac, add `sudo` before commands (needed for raw packet sending).

### Run Attack 1 — SYN Flood

```bash
# Linux / Mac
sudo python attacks/syn_flood.py --target 127.0.0.1 --port 80 --count 500

# Windows (run terminal as Administrator)
python attacks/syn_flood.py --target 127.0.0.1 --port 80 --count 500
```

You'll see output like:
```
[*] Starting SYN Flood → 127.0.0.1:80
[*] Sending 500 packets | delay=0s
  [+] Sent 100/500 SYN packets...
  [+] Sent 200/500 SYN packets...
[✓] SYN Flood complete. Total packets sent: 500
```

Meanwhile — **look at Wireshark**. You'll see hundreds of packets flooding in!

---

### Run Attack 2 — UDP Flood

```bash
# Linux / Mac
sudo python attacks/udp_flood.py --target 127.0.0.1 --count 500 --size 1024

# Windows (run terminal as Administrator)
python attacks/udp_flood.py --target 127.0.0.1 --count 500 --size 1024
```

---

### Optional: Auto-Record While Attacking

This runs tshark (Wireshark's command-line version) in the background and saves a `.pcap` file you can open and study later:

```bash
sudo python capture/capture_helper.py --attack syn --target 127.0.0.1 --count 500
sudo python capture/capture_helper.py --attack udp --target 127.0.0.1 --count 500
```

Files are saved in `capture/` folder with a timestamp like `syn_flood_20250803_143022.pcap`.
Open them any time in Wireshark: **File → Open → select the .pcap file**

---

## 🔬 What to Look For in Wireshark

This is the actual learning part. Here's how to read what happened after running each attack.

### 🔵 Analyzing SYN Flood

In the Wireshark filter bar at the top, type this and press Enter:
```
tcp.flags.syn == 1 && tcp.flags.ack == 0
```
This shows ONLY the SYN packets — the attack traffic.

**What you'll see:**
- Hundreds of rows all labelled `SYN`
- The **Source IP** column changes constantly — those are the fake spoofed IPs
- The **Destination** is always `127.0.0.1` (your machine)
- You'll see `SYN-ACK` replies from the server, but **NEVER a final `ACK`** — the handshake never completes

**To see the big picture — go to:**
```
Statistics → Conversations → TCP tab
```
This shows every "conversation." You'll see dozens of unique fake source IPs, each with exactly 1 incomplete connection.

```
Statistics → IO Graph
```
Watch the massive spike in traffic — the bandwidth flood visualized as a graph.

```
Analyze → Expert Info
```
Wireshark will flag all the incomplete connections as warnings automatically.

---

### 🟠 Analyzing UDP Flood

In the filter bar:
```
udp && ip.dst == 127.0.0.1
```

**What you'll see:**
- Massive number of UDP packets arriving on random, ever-changing port numbers
- Rows labelled `ICMP` — those are your machine saying *"nothing is running on that port!"* in response to each junk packet
- Destination ports are random — the attacker is spraying everywhere

**To see traffic breakdown:**
```
Statistics → Protocol Hierarchy
```
You'll see UDP making up a huge percentage of all traffic — visually shows the flood.

```
Statistics → Conversations → UDP tab
```
See which fake source IPs sent the most data.

---

## 📊 Quick Comparison: SYN Flood vs UDP Flood

| | SYN Flood | UDP Flood |
|---|---|---|
| **What it attacks** | Server's connection memory | Network bandwidth & CPU |
| **Protocol used** | TCP | UDP |
| **Needs response from victim?** | Yes (SYN-ACK) | No |
| **Spoofed IPs?** | Yes | Yes |
| **Wireshark signature** | Tons of SYN, no ACK | Tons of UDP + ICMP replies |
| **Real-world damage** | Server stops accepting connections | Bandwidth saturated |
| **Complexity** | Medium | Simple |

---

## ❓ Frequently Asked Questions

**Q: Will this crash or damage my computer?**
No. We're sending 500 packets to localhost. Your machine handles millions of packets per day normally. Even increasing to 5000 packets is completely harmless on localhost.

**Q: Why do I need `sudo` or run as Administrator?**
Sending raw packets — crafting custom TCP/UDP packets from scratch — requires low-level network access. Only admin/root has permission for this.

**Q: What is `127.0.0.1`?**
It's your own computer's address for talking to itself, also called "localhost". Traffic sent here **never leaves your machine** — it's an isolated sandbox.

**Q: What is Scapy?**
A Python library that lets you build any network packet from scratch — choose every field manually. Used by security researchers and network engineers worldwide.

**Q: I see nothing in Wireshark — what's wrong?**
Make sure you selected the **Loopback** interface (not Wi-Fi or Ethernet) *before* the attack starts. Wireshark must be running before you launch the script.

**Q: What is a `.pcap` file?**
A packet capture file — it's a recording of network traffic. You can open it in Wireshark any time to re-analyze the traffic, share it with your lab partner, or submit it as proof for your assignment.

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| `Permission denied` error | Add `sudo` before the command (Linux/Mac) or run terminal as Administrator (Windows) |
| `ModuleNotFoundError: scapy` | Run `pip install scapy` first |
| `tshark: command not found` | Run `sudo apt install tshark` (Linux) |
| Wireshark shows nothing | Select the **Loopback / lo** interface, not Wi-Fi or Ethernet |
| Script runs but nothing happens | Try increasing `--count` to 1000 |
| Very slow packet sending | Set `--delay 0` or remove the delay flag entirely |

---

## 📚 Want to Learn More?

If this sparked your curiosity, here are good next steps:

- **Scapy Docs** — [scapy.readthedocs.io](https://scapy.readthedocs.io/) — Learn how to craft any packet imaginable
- **Wireshark Beginner Guide** — [wiki.wireshark.org](https://wiki.wireshark.org/CaptureFilters) — Filters, statistics, analysis tips
- **TCP/IP Explained (Video)** — Search "TCP 3-way handshake explained" on YouTube — great visual explanations
- **TryHackMe** — [tryhackme.com](https://tryhackme.com) — Free beginner cybersecurity labs with guided missions
- **Hack The Box Academy** — [academy.hackthebox.com](https://academy.hackthebox.com) — Structured networking and security courses

---

*Assignment 1 — Network Security | Python + Scapy + Wireshark*
*Written to be understandable even if you've never studied networking before* 🔐
