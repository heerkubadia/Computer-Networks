#!/bin/bash
# syn_attack_test.sh - Automated SYN flood attack and legitimate traffic simulation

# Experiment Configuration
TARGET_HOST="192.168.56.104"  # Set this to the target server IP
TARGET_PORT=8000
FLOOD_TIME=100
NORMAL_TRAFFIC_TIME_BEFORE=20
NORMAL_TRAFFIC_TIME_AFTER=20
# CAPTURE_FILE="attack_test_capture.pcap"
CAPTURE_FILE="mitigation_test_capture.pcap"

# Ensure script is executed with root privileges
if [ "$EUID" -ne 0 ]; then
  echo "Error: This script must be run as root!"
  exit 1
fi

# Install necessary dependencies
echo "Ensuring required packages are installed..."
which tcpdump >/dev/null || apt-get -y install tcpdump
which python3 >/dev/null || apt-get -y install python3
which hping3 >/dev/null || apt-get -y install hping3
pip3 list | grep scapy >/dev/null || pip3 install scapy

echo "Preparing to execute the SYN flood attack experiment."
echo "Target: $TARGET_HOST:$TARGET_PORT"

# Step 1: Begin network packet capture
echo "Starting network traffic capture..."
tcpdump -i any -w "$CAPTURE_FILE" tcp port $TARGET_PORT -v &
CAPTURE_PID=$!

# Allow capture to initialize
sleep 2

# Step 2: Generate normal traffic before attack
echo "Generating legitimate traffic..."
python3 normal_traffic_generator.py $TARGET_HOST &
TRAFFIC_PID=$!

echo "Waiting for $NORMAL_TRAFFIC_TIME_BEFORE seconds before launching attack..."
sleep $NORMAL_TRAFFIC_TIME_BEFORE

# Step 3: Initiate SYN flood attack
echo "Launching SYN flood attack..."
python3 tcp_syn_attacker.py --target_ip $TARGET_HOST --target_port $TARGET_PORT --duration $FLOOD_TIME &
ATTACK_PID=$!

# Allow attack to run for the specified duration
echo "Attack in progress for $FLOOD_TIME seconds..."
sleep $FLOOD_TIME

# Step 4: Terminate the attack
echo "Halting SYN flood attack..."
kill -SIGINT $ATTACK_PID 2>/dev/null || true
wait $ATTACK_PID 2>/dev/null || true

# Step 5: Continue normal traffic after attack
echo "Allowing normal traffic for $NORMAL_TRAFFIC_TIME_AFTER more seconds..."
sleep $NORMAL_TRAFFIC_TIME_AFTER

echo "Stopping legitimate traffic..."
kill -SIGINT $TRAFFIC_PID
wait $TRAFFIC_PID

# Step 6: Stop packet capture and finalize results
echo "Stopping packet capture..."
kill -SIGINT $CAPTURE_PID
wait $CAPTURE_PID

echo "Experiment complete!"
echo "Captured network traffic saved to: $CAPTURE_FILE"
echo "You can now analyze the traffic capture for attack impact assessment."
