# CS331: Computer Networks – Assignment 3

**Team Members:**  
- **Member 1**: Heer Kubadia - 22110096  
- **Member 2**: Lavanya - 22110130  

**Submission Deadline:** 12-Apr-2025, 11:59 PM  

---

## Assignment Overview

This assignment focuses on three core areas of computer networking:

1. **Network Loop Analysis and Resolution (Q1):**  
   You will construct a looped switch topology using Mininet and analyze the behavior of ICMP ping packets. You'll identify packet loss or routing loops, and resolve the issue using STP (Spanning Tree Protocol) — all without altering the physical topology.

2. **Host-Based NAT Configuration (Q2):**  
   You will modify the existing network by introducing NAT functionality in a host (H9), allowing private IP addresses to access external networks. You will then verify NAT translation with both ping and bandwidth tests using `iperf3`, and configure iptables rules manually.

3. **Routing Algorithm Implementation (Q3):**  
   This section requires implementing and testing classic routing algorithms like Bellman-Ford in a simulated Mininet environment. You’ll analyze routing tables, verify path selection, and demonstrate correct behavior through test cases and visual confirmation.

Each question is supported by Python scripts for Mininet, shell scripts for NAT, and PDF report documenting complete instructions, test results, analysis, screenshots, and performance metrics.


---

## Requirements

- Mininet (>=2.3.0)  
- iperf3  
- Wireshark / tcpdump (for packet capture)  
- Python 3.x  
- Net-tools (for `ifconfig`)

---

##  How to Run (Note - Please refer to the report for detailed instructions)

### Q1: Network Loops

```bash
cd question1
sudo python3 topology.py
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
cd question2
sudo python3 topology.py
```

- Configure NAT on `h9`

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
cd question3
sudo python3 topology_q3.py
```

- Run the routing algorithm script:
  ```bash
  python3 routing_algo.py
  ```

- Inspect routing tables and validate correct path selection.

---

## Report

35_22110096_22110130.pdf is the complete report for all the questions.
This report include:
- Complete step by step instructions for executing the codes
- Topology diagrams
- Packet captures and NAT rules
- Routing tables and metrics
- Test results, screenshots, and analysis

---

## Notes

- All tests were run multiple times for consistency.
- Ensure Mininet is run with `sudo` to avoid permission issues.
- NAT configuration uses `iptables` to translate addresses.
- Use `xterm` or `mininet> h1 ping h5` style commands for testing.
- All iperf tests were run with `-t 120` flag for consistent throughput measurement.

---
