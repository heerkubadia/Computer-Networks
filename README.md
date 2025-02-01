# Sniffer Usage Guide

This repository provides a simple network sniffer and traffic replay tool. Follow the instructions below to use the sniffer and analyze captured packets.

### 1. Clone the Repository
First, clone this repository to your local machine using the following command:

```bash
git clone https://github.com/heerkubadia/Computer-Networks.git
cd Computer-Networks
```

### Part 2: Open Two Terminals

You will need two terminals open to run the traffic replay and the sniffer simultaneously.

#### Terminal 1: Replay Network Traffic
In the first terminal, use the following command to replay the network traffic from a `.pcap` file:

```bash
sudo tcpreplay --intf1= <interface> --pps=<desired speed> <pcap file>
```
```bash
sudo tcpreplay --intf1=eth0 --pps=1000 4.pcap
```

eth0: This is the network interface we used. Replace it with the correct interface name if necessary (for example, en0, wlan0 , lo, etc.).
4.pcap: This is the packet capture file we replayed. 

#### Terminal 2: Compile and Run the Sniffer

In the second terminal, compile and run the sniffer:
```bash
g++ sniffer.cpp -o sniffer -lpcap
./sniffer
```
The sniffer will start capturing network packets in real-time and print out details to the terminal.


### Part 3: Clear Network Interface Traffic (Optional)

Before starting the sniffer, you may want to clear any pre-existing traffic on the network interface you're using. Use the following commands to reset the network interface:

```bash
sudo ipconfig eth0 down
sudo ipconfig eth0 up
```

### Part 4: Analyze Captured Packets

The sniffer captures network packets and stores them in a `.pcap` file. You can analyze these packets using the analysis code provided in the `analysis.ipynb` Jupyter notebook.

To get started with the analysis:

1. Open `analysis.ipynb` in Jupyter or any compatible notebook environment.
2. Run the cells to process and analyze the captured `.pcap` file.

## Additional Tips
- Turn off the wifi to avoid capturing extra packets.
- Ensure that you have the necessary permissions to capture packets on your network interface. You may need `sudo` privileges for this.
- Make sure that the `libpcap` library is installed on your system in order to compile the sniffer.

Enjoy analyzing your network traffic with the sniffer!

