from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch, OVSController
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel
import time
import os

class LoopTopo(Topo):
    def build(self):
        # Add switches with STP enabled
        s1 = self.addSwitch('s1', stp=True)
        s2 = self.addSwitch('s2', stp=True)
        s3 = self.addSwitch('s3', stp=True)
        s4 = self.addSwitch('s4', stp=True)

        # Add NAT gateway host
        h9 = self.addHost('h9')  # Acts as NAT router

        # Add internal hosts connected to NAT
        h1 = self.addHost('h1', ip='10.1.1.2/24')
        h2 = self.addHost('h2', ip='10.1.1.3/24')
        
        # Add external hosts
        h3 = self.addHost('h3', ip='10.0.0.4/24')
        h4 = self.addHost('h4', ip='10.0.0.5/24')
        h5 = self.addHost('h5', ip='10.0.0.6/24')
        h6 = self.addHost('h6', ip='10.0.0.7/24')
        h7 = self.addHost('h7', ip='10.0.0.8/24')
        h8 = self.addHost('h8', ip='10.0.0.9/24')

        # Connect internal hosts to NAT
        self.addLink(h1, h9, cls=TCLink, delay='5ms')
        self.addLink(h2, h9, cls=TCLink, delay='5ms')

        # Connect NAT to switch s1 for external access
        self.addLink(h9, s1, cls=TCLink, delay='5ms')

        # Connect external hosts to switches
        self.addLink(h3, s2, cls=TCLink, delay='5ms')
        self.addLink(h4, s2, cls=TCLink, delay='5ms')
        self.addLink(h5, s3, cls=TCLink, delay='5ms')
        self.addLink(h6, s3, cls=TCLink, delay='5ms')
        self.addLink(h7, s4, cls=TCLink, delay='5ms')
        self.addLink(h8, s4, cls=TCLink, delay='5ms')

        # Add inter-switch links to form a loop topology
        self.addLink(s1, s2, cls=TCLink, delay='7ms')
        self.addLink(s2, s3, cls=TCLink, delay='7ms')
        self.addLink(s3, s4, cls=TCLink, delay='7ms')
        self.addLink(s4, s1, cls=TCLink, delay='7ms')
        self.addLink(s1, s3, cls=TCLink, delay='7ms')

def run():
    topo = LoopTopo()
    net = Mininet(topo=topo, switch=OVSSwitch, controller=OVSController, autoSetMacs=True)
    net.start()
    
    # Retrieve hosts and switches
    h1, h2, h3, h4, h5, h6, h7, h8, h9 = net.get('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9')
    
    # Enable STP on all switches
    for sw in ['s1', 's2', 's3', 's4']:
        net.get(sw).cmd(f'ovs-vsctl set Bridge {sw} stp_enable=true')
    
    # Clear any existing IPs on NAT interfaces
    h9.cmd("ip addr flush dev h9-eth0")
    h9.cmd("ip addr flush dev h9-eth1")
    h9.cmd("ip addr flush dev h9-eth2")
    
    # Create bridge on NAT for internal connections
    h9.cmd('ip link add name br0 type bridge')
    h9.cmd('ip link set br0 up')
    h9.cmd('ip link set h9-eth0 master br0')  # Connect to h1
    h9.cmd('ip link set h9-eth1 master br0')  # Connect to h2
    h9.cmd('ip addr add 10.1.1.1/24 dev br0')  # Internal gateway IP
    
    # Assign external IP to NAT
    h9.setIP('10.0.0.1/24', intf='h9-eth2')
    h9.cmd('ip addr add 172.16.10.10/24 dev h9-eth2')

    # Configure default gateways for internal hosts
    h1.cmd('ip route add default via 10.1.1.1')
    h2.cmd('ip route add default via 10.1.1.1')

    # Configure default gateways for external hosts
    for h in [h3, h4, h5, h6, h7, h8]:
        h.cmd('ip route add default via 10.0.0.1')
    
    # Enable IP forwarding on NAT
    h9.cmd('sysctl -w net.ipv4.ip_forward=1')
    
    # Set up NAT rules for internal to external masquerading
    h9.cmd('iptables -t nat -F')
    h9.cmd('iptables -t nat -A POSTROUTING -s 10.1.1.0/24 -o h9-eth2 -j MASQUERADE')
    
    print("Waiting 30 seconds for network to stabilize...")
    time.sleep(30)
    
    # Test network connectivity
    print("\nTesting connectivity across the network:")
    net.pingAll()
    
    print("\nNAT network ready. Use CLI to interact with hosts.")
    CLI(net)
    
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
