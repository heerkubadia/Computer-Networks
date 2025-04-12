# CS331: Computer Networks – Assignment 3

**Team Members:**  
- **Member 1**: Your Name (Roll Number)  
- **Member 2**: Partner's Name (Roll Number)  

**Submission Deadline:** 12-Apr-2025, 11:59 PM  

---

## 📘 Assignment Overview

This assignment focuses on three core areas of computer networking:

1. **Network Loop Analysis and Resolution (Q1):**  
   You will construct a looped switch topology using Mininet and analyze the behavior of ICMP ping packets. You'll identify packet loss or routing loops, and resolve the issue using STP (Spanning Tree Protocol) — all without altering the physical topology.

2. **Host-Based NAT Configuration (Q2):**  
   You will modify the existing network by introducing NAT functionality in a host (H9), allowing private IP addresses to access external networks. You will then verify NAT translation with both ping and bandwidth tests using `iperf3`, and configure iptables rules manually.

3. **Routing Algorithm Implementation (Q3):**  
   This section requires implementing and testing classic routing algorithms like Dijkstra’s or Bellman-Ford in a simulated Mininet environment. You’ll analyze routing tables, verify path selection, and demonstrate correct behavior through test cases and visual confirmation.

Each question is supported by Python scripts for Mininet, shell scripts for NAT, and PDF reports documenting test results, analysis, screenshots, and performance metrics.

---

## 📁 Directory Structure

```
.
├── Q1_Loops/
│   ├── topology_q1.py
│   ├── q1_analysis_report.pdf
│   └── packet_captures/
├── Q2_NAT/
│   ├── topology_q2.py
│   ├── nat_rules.sh
│   ├── q2_analysis_report.pdf
│   └── iperf_results/
├── Q3_Routing/
│   ├── topology_q3.py
│   ├── routing_algo.py
│   ├── q3_analysis_report.pdf
│   └── routing_tables/
├── README.md
```

---

## 🧪 Requirements

- Mininet (>=2.3.0)  
- iperf3  
- Wireshark / tcpdump (for packet capture)  
- Python 3.x  
- Net-tools (for `ifconfig`)

---

## ⚙️ How to Run

### Q1: Network Loops

```bash
cd Q1_Loops
sudo python3 topology_q1.py
```

- Run the following pings:
  - `h3 ping h1`
  - `h5 ping h7`
  - `h8 ping h2`
- If pings fail, capture packets using `tcpdump` or Wireshark.
- Enable STP to resolve loops.
- Re-run pings and record the delay (3 times, 30 seconds apart).

---

### Q2: Host-based NAT

```bash
cd Q2_NAT
sudo python3 topology_q2.py
```

- Configure NAT on `h9`:
  ```bash
  sudo ./nat_rules.sh
  ```

- **Ping Tests:**
  - h1 → h5
  - h2 → h3
  - h8 → h1
  - h6 → h2

- **iperf3 Tests (each for 120s):**
  - h6 → h1 (server on h1)
  - h2 → h8 (server on h8)

---

### Q3: Network Routing

```bash
cd Q3_Routing
sudo python3 topology_q3.py
```

- Run the routing algorithm script:
  ```bash
  python3 routing_algo.py
  ```

- Inspect routing tables and validate correct path selection.

---

## 📄 Reports

Each subdirectory contains a corresponding PDF report:
- `q1_analysis_report.pdf`
- `q2_analysis_report.pdf`
- `q3_analysis_report.pdf`

These reports include:
- Topology diagrams
- Packet captures and NAT rules
- Routing tables and metrics
- Test results, screenshots, and analysis

---

## ✅ Notes

- All tests were run multiple times for consistency.
- Ensure Mininet is run with `sudo` to avoid permission issues.
- NAT configuration uses `iptables` to translate addresses.
- Use `xterm` or `mininet> h1 ping h5` style commands for testing.
- All iperf tests were run with `-t 120` flag for consistent throughput measurement.

---
