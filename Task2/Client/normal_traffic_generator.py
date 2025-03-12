#!/usr/bin/env python3
# normal_traffic_generator.py - Generates regular TCP traffic for baseline comparison

import socket
import time
import random
import sys
import signal
import argparse
import logging
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('traffic_generator')

class TrafficGenerator:
    """Generates normal TCP traffic to a target server"""
    
    def __init__(self, target_host, target_port=8000, interval=0.75):
        self.target_host = target_host
        self.target_port = target_port
        self.interval = interval
        self.running = False
        self.successful = 0
        self.failed = 0
        self.last_stats_time = time.time()
        self.stats_interval = 10  # Show stats every 10 seconds
        
    def initialize(self):
        """Set up signal handlers and initialize generator"""
        # Register signal handlers
        signal.signal(signal.SIGINT, self._handle_interrupt)
        signal.signal(signal.SIGTERM, self._handle_interrupt)
        
        logger.info(f"Traffic generator initialized for {self.target_host}:{self.target_port}")
        logger.info(f"Request interval: {self.interval} seconds")
        logger.info("Press Ctrl+C to stop")
        
    def _handle_interrupt(self, signum, frame):
        """Handle interrupt signals gracefully"""
        self.running = False
        logger.info("Shutting down traffic generator...")
        self._show_final_stats()
        sys.exit(0)
        
    def make_request(self):
        """Send a single TCP request to the target"""
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # conn.settimeout(5.0)  # 5 second timeout
        
        start_time = time.time()
        success = False
        error_message = None
        
        try:
            # Open connection
            conn.connect((self.target_host, self.target_port))
            
            # Send request data
            request_data = f"Hello from traffic generator at {datetime.now()}\n"
            conn.sendall(request_data.encode())
            
            # Receive response
            response = conn.recv(1024)
            
            # Process successful request
            elapsed = time.time() - start_time
            success = True
            response_text = response.decode('utf-8', errors='replace').strip()
            logger.info(f"Response in {elapsed:.4f}s: {response_text[:50]}")
            
        except socket.timeout:
            elapsed = time.time() - start_time
            error_message = f"Connection timed out after {elapsed:.2f}s"
            
        except ConnectionRefusedError:
            elapsed = time.time() - start_time
            error_message = f"Connection refused after {elapsed:.2f}s"
            
        except Exception as e:
            elapsed = time.time() - start_time
            error_message = f"Error after {elapsed:.2f}s: {str(e)}"
            
        finally:
            # Clean up
            conn.close()
            
            # Update statistics
            if success:
                self.successful += 1
            else:
                self.failed += 1
                if error_message:
                    logger.warning(error_message)
                    
            return success
            
    def _show_stats(self):
        """Show current statistics"""
        total = self.successful + self.failed
        success_rate = (self.successful / total * 100) if total > 0 else 0
        
        logger.info(f"Stats: {self.successful} successful ({success_rate:.1f}%), "
                   f"{self.failed} failed, {total} total requests")
                   
    def _show_final_stats(self):
        """Show final statistics summary"""
        total = self.successful + self.failed
        duration = time.time() - self.start_time
        
        if total == 0:
            logger.info("No requests were made")
            return
            
        success_rate = (self.successful / total * 100)
        requests_per_second = total / duration
        
        logger.info("=== Traffic Generator Summary ===")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Successful requests: {self.successful}")
        logger.info(f"Failed requests: {self.failed}")
        logger.info(f"Success rate: {success_rate:.2f}%")
        logger.info(f"Average rate: {requests_per_second:.2f} requests/second")
        
    def run(self, duration=None):
        """Run the traffic generator"""
        self.running = True
        self.start_time = time.time()
        end_time = self.start_time + duration if duration else None
        
        logger.info(f"Starting traffic generation at {datetime.now().strftime('%H:%M:%S')}")
        if end_time:
            end_datetime = datetime.now() + timedelta(seconds=duration)
            logger.info(f"Will run until {end_datetime.strftime('%H:%M:%S')} ({duration} seconds)")
        
        try:
            while self.running:
                # Check if duration has elapsed
                if end_time and time.time() >= end_time:
                    logger.info("Configured duration reached, stopping")
                    break
                    
                # Send request
                self.make_request()
                
                # Show stats periodically
                current_time = time.time()
                if current_time - self.last_stats_time >= self.stats_interval:
                    self._show_stats()
                    self.last_stats_time = current_time
                
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        
        # Show final statistics
        self._show_final_stats()


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate normal TCP traffic to a target server')
    parser.add_argument('host', nargs='?', default='192.168.56.104',
                        help='Target server IP address')
    parser.add_argument('--port', '-p', type=int, default=8000,
                        help='Target server port')
    parser.add_argument('--interval', '-i', type=float, default=0.8,
                        help='Time between requests in seconds')
    args = parser.parse_args()
    
    # Create and run traffic generator
    generator = TrafficGenerator(args.host, args.port, args.interval)
    generator.initialize()
    generator.run(1000) # Run for 1000 seconds

if __name__ == "__main__":
    main()