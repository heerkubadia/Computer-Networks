# Sniffer Usage Guide

This repository provides a simple network sniffer and traffic replay tool. Follow the instructions below to use the sniffer and analyze captured packets.

## Steps to Use the Sniffer

### 1. Clone the Repository
First, clone this repository to your local machine using the following command:

```bash
git clone https://github.com/heerkubadia/Computer-Networks.git
cd Computer-Networks
2. Open Two Terminals
You will need two terminals open to run the traffic replay and sniffer simultaneously.

Terminal 1: Replay Network Traffic

In the first terminal, run the following command to replay the network traffic from a .pcap file:

sudo tcpreplay --intf1=en0 --pps=1000 4.pcap
en0 is the network interface you want to use. Replace it with the correct interface name if necessary (for example, eth0 for Ethernet, wlan0 for Wi-Fi).
4.pcap is the packet capture file you want to replay. Ensure this file is available in the repository.
Terminal 2: Compile and Run the Sniffer

In the second terminal, compile and run the sniffer:

Compile the sniffer program:
g++ snifbro.cpp -o sniffer -lpcap
Run the sniffer:
./sniffer
The sniffer will start capturing network packets in real time and print out details to the terminal.

3. Clear Network Interface Traffic (Optional)
Before starting the sniffer, you may want to clear any pre-existing traffic on the network interface you're using:

sudo ipconfig eth0 down
sudo ipconfig eth0 up
Make sure to replace eth0 with the network interface you're using (e.g., en0, wlan0).

4. Analyze Captured Packets
The sniffer captures network packets and stores them in a .pcap file. You can analyze these packets using the analysis code provided in the analysis.ipynb Jupyter notebook.

To get started with the analysis:

Open analysis.ipynb in Jupyter or any compatible notebook environment.
Run the cells to process and analyze the captured .pcap file.
Additional Tips

Ensure that you have the necessary permissions to capture packets on your network interface. You may need sudo privileges for this.
Make sure that the libpcap library is installed on your system to compile the sniffer.
