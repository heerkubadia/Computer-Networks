#!/usr/bin/env python3
"""
tcp_connection_analyzer.py

Analyzes TCP connection durations from network captures with focus on
detecting the impact of SYN flood attacks. This tool parses packet data,
reconstructs connection timelines, and visualizes the impact of network
attacks on connection performance.
"""

import argparse
import subprocess
import sys
import pickle
import os
import matplotlib.pyplot as plt
from tqdm import tqdm
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('tcp_analyzer')

# Packet fields for extraction


class PacketExtractor:
    """Extracts TCP packet data from PCAP files"""
    
    @staticmethod
    def extract_packets(capture_file):
        """Extract TCP packet data using tshark"""
        logger.info(f"Extracting TCP packets from {capture_file}")
        
        # Build tshark command
        command = ["tshark", "-r", capture_file, "-Y", "tcp", "-T", "fields", "-e", "frame.time_epoch", "-e", "ip.src", "-e", "ip.dst", "-e", "tcp.srcport", "-e", "tcp.dstport", "-e", "tcp.flags.syn", "-e", "tcp.flags.ack", "-e", "tcp.flags.fin", "-e", "tcp.flags.reset"]
        
        try:
            # Execute command
            raw_output = subprocess.check_output(command, universal_newlines=True)
        except subprocess.CalledProcessError as error:
            logger.error(f"tshark extraction failed: {error}")
            sys.exit(1)
        
        # Process output into packet objects
        packet_list = []
        for line_num, line in enumerate(raw_output.strip().splitlines()):
            fields = line.split("\t")
            if len(fields) < 9:
                continue
                
            try:
                packet = {
                    "timestamp": float(fields[0]),
                    "source_ip": fields[1],
                    "dest_ip": fields[2],
                    "source_port": fields[3],
                    "dest_port": fields[4],
                    "is_syn": fields[5].lower() in ("1", "true"),
                    "is_ack": fields[6].lower() in ("1", "true"),
                    "is_fin": fields[7].lower() in ("1", "true"),
                    "is_rst": fields[8].lower() in ("1", "true")
                }
                packet_list.append(packet)
            except (ValueError, IndexError):
                logger.warning(f"Could not parse packet at line {line_num+1}")
                continue
                
        logger.info(f"Extracted {len(packet_list)} valid TCP packets")
        return packet_list


class ConnectionTracker:
    """Tracks and analyzes TCP connection lifecycles"""
    
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = str(server_port)
        self.connections = {}
        
    def analyze_packets(self, packets):
        """Analyze packet stream to detect connection durations"""
        logger.info("Analyzing TCP connections")
        
        for packet in tqdm(packets, desc="Processing packets"):
            # Determine packet direction and connection ID
            connection_id, direction = self._identify_connection(packet)
            if not connection_id:
                continue
                
            # Handle connection start (SYN from client)
            if packet["is_syn"] and not packet["is_ack"] and direction == "client_to_server":
                self._record_connection_start(connection_id, packet["timestamp"])
                    
            # Handle existing connections
            elif connection_id in self.connections and self.connections[connection_id]["end_time"] is None:
                # Handle reset
                if packet["is_rst"]:
                    self.connections[connection_id]["end_time"] = packet["timestamp"]
                    self.connections[connection_id]["end_reason"] = "reset"
                    
                # Handle FIN
                elif packet["is_fin"]:
                    self.connections[connection_id]["last_fin"] = {
                        "time": packet["timestamp"],
                        "direction": direction
                    }
                    
                    if packet["is_ack"]:
                        self.connections[connection_id]["fin_ack_seen"] = True
                        
                # Handle ACK after FIN
                elif (packet["is_ack"] and 
                      self.connections[connection_id].get("fin_ack_seen") and
                      self.connections[connection_id].get("last_fin")):
                      
                    last_fin = self.connections[connection_id]["last_fin"]
                    if last_fin["direction"] != direction and packet["timestamp"] > last_fin["time"]:
                        self.connections[connection_id]["end_time"] = packet["timestamp"]
                        self.connections[connection_id]["end_reason"] = "normal"
        
        logger.info(f"Identified {len(self.connections)} unique TCP connections")
        return self.connections
    
    def _identify_connection(self, packet):
        """Identify connection ID and direction"""
        # Check if packet is to/from server
        is_to_server = (packet["dest_ip"] == self.server_ip and 
                        packet["dest_port"] == self.server_port)
        is_from_server = (packet["source_ip"] == self.server_ip and 
                          packet["source_port"] == self.server_port)
        
        # Skip packets not related to the server
        if not is_to_server and not is_from_server:
            return None, None
            
        # Create connection ID with client always first
        if is_to_server:
            # Client to server
            connection_id = (
                packet["source_ip"],
                packet["source_port"],
                packet["dest_ip"],
                packet["dest_port"]
            )
            direction = "client_to_server"
        else:
            # Server to client
            connection_id = (
                packet["dest_ip"],
                packet["dest_port"],
                packet["source_ip"],
                packet["source_port"]
            )
            direction = "server_to_client"
            
        return connection_id, direction
    
    def _record_connection_start(self, connection_id, timestamp):
        """Record or update connection start time"""
        if connection_id not in self.connections:
            self.connections[connection_id] = {
                "start_time": timestamp,
                "end_time": None,
                "fin_ack_seen": False,
                "last_fin": None,
                "end_reason": None
            }
        elif timestamp < self.connections[connection_id]["start_time"]:
            # Update if we found an earlier SYN
            self.connections[connection_id]["start_time"] = timestamp
            
    def calculate_durations(self):
        """Calculate connection durations and normalize start times"""
        start_times = []
        durations = []
        
        # Find earliest timestamp
        all_starts = [conn["start_time"] for conn in self.connections.values()]
        if not all_starts:
            return [], []
            
        reference_time = min(all_starts)
        
        # Calculate durations
        for conn_id, details in self.connections.items():
            # Relative start time
            rel_start = details["start_time"] - reference_time
            
            # Duration (default to 100s if no end)
            if details["end_time"] is None:
                duration = 100.0
            else:
                duration = details["end_time"] - details["start_time"]
                
            start_times.append(rel_start)
            durations.append(duration)
            
        logger.info(f"Calculated {len(durations)} connection durations")
        return start_times, durations


class ResultVisualizer:
    """Visualizes connection analysis results"""
    
    @staticmethod
    def create_duration_plot(start_times, durations, attack_window=None, output_file="connection_analysis.png"):
        """Generate scatter plot of connection durations"""
        if not start_times or not durations:
            logger.warning("No data available for visualization")
            return
            
        # Create figure
        plt.figure(figsize=(12, 7))
        
        # Plot connections
        plt.scatter(start_times, durations, alpha=0.7, color='blue', label='TCP Connections')
        
        # Mark attack period if provided
        if attack_window and len(attack_window) == 2:
            attack_start, attack_end = attack_window
            plt.axvline(x=attack_start, color='red', linestyle='--', 
                       linewidth=2, label='Attack Start')
            plt.axvline(x=attack_end, color='green', linestyle='--', 
                       linewidth=2, label='Attack End')
        
        # Add labels and title
        plt.xlabel('Connection Start Time (seconds from first packet)')
        plt.ylabel('Connection Duration (seconds)')
        plt.title('TCP Connection Duration Analysis')
        plt.grid(True, alpha=0.3)
        plt.legend(loc='best')
        
        # Save and display
        plt.savefig(output_file, dpi=300)
        logger.info(f"Plot saved to {output_file}")
        plt.show()


class CheckpointManager:
    """Manages data checkpoints for long-running analyses"""
    
    @staticmethod
    def save_checkpoint(data, filename):
        """Save data to checkpoint file"""
        with open(filename, 'wb') as file:
            pickle.dump(data, file)
        logger.info(f"Checkpoint saved to {filename}")
        
    @staticmethod
    def load_checkpoint(filename):
        """Load data from checkpoint file"""
        if not os.path.exists(filename):
            logger.warning(f"Checkpoint file {filename} not found")
            return None
            
        with open(filename, 'rb') as file:
            data = pickle.load(file)
        logger.info(f"Checkpoint loaded from {filename}")
        return data


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Analyze TCP connections to detect impact of SYN flood attacks"
    )
    parser.add_argument("capture_file", help="Path to the packet capture file")
    parser.add_argument("--server_ip", default="192.168.56.104",
                        help="IP address of target server")
    parser.add_argument("--server_port", type=int, default=8000,
                        help="Port of target server")
    parser.add_argument("--attack_start", type=float, default=20,
                        help="Relative time (seconds) when attack started")
    parser.add_argument("--attack_end", type=float, default=120,
                        help="Relative time (seconds) when attack ended")
    parser.add_argument("--checkpoints", action="store_true",
                        help="Enable checkpoint saving/loading")
    args = parser.parse_args()
    
    # Check if capture file exists
    if not os.path.isfile(args.capture_file):
        logger.error(f"Capture file not found: {args.capture_file}")
        sys.exit(1)
        
    # Define checkpoint files
    packets_checkpoint = "packets_checkpoint.dat"
    connections_checkpoint = "connections_checkpoint.dat"
    
    # Step 1: Extract packets
    if args.checkpoints and os.path.exists(packets_checkpoint):
        packets = CheckpointManager.load_checkpoint(packets_checkpoint)
    else:
        packets = PacketExtractor.extract_packets(args.capture_file)
        if args.checkpoints:
            CheckpointManager.save_checkpoint(packets, packets_checkpoint)
    
    # Step 2: Analyze connections
    if args.checkpoints and os.path.exists(connections_checkpoint):
        connections = CheckpointManager.load_checkpoint(connections_checkpoint)
        tracker = ConnectionTracker(args.server_ip, args.server_port)
        tracker.connections = connections
    else:
        tracker = ConnectionTracker(args.server_ip, args.server_port)
        connections = tracker.analyze_packets(packets)
        if args.checkpoints:
            CheckpointManager.save_checkpoint(connections, connections_checkpoint)
    
    # Step 3: Calculate durations
    start_times, durations = tracker.calculate_durations()
    
    # Step 4: Visualize results
    attack_window = None
    if args.attack_start is not None and args.attack_end is not None:
        attack_window = (args.attack_start, args.attack_end)
        
    ResultVisualizer.create_duration_plot(start_times, durations, attack_window)
    
    # Print statistics
    if durations:
        avg_duration = sum(durations) / len(durations)
        timeout_count = sum(1 for d in durations if d >= 99.9)  # Count default timeouts
        logger.info(f"Analysis summary:")
        logger.info(f"  - Total connections: {len(durations)}")
        logger.info(f"  - Average duration: {avg_duration:.2f} seconds")
        logger.info(f"  - Timed-out connections: {timeout_count} ({timeout_count/len(durations)*100:.1f}%)")

if __name__ == "__main__":
    main()