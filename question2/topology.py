from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch, OVSController
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel
import time
import os

# Clean up any previous Mininet setup
os.system('mn -c')

class LoopTopo(Topo):
    def build(self):
        # Add switches
        s1 = self.addSwitch('s1', stp=True)
        s2 = self.addSwitch('s2', stp=True)
        s3 = self.addSwitch('s3', stp=True)
        s4 = self.addSwitch('s4', stp=True)

        # Add NAT gateway host H9
        h9 = self.addHost('h9')  # NAT router without initial IP
        
        # Add H1 and H2, connected to H9 instead of s1
        h1 = self.addHost('h1', ip='10.1.1.2/24')
        h2 = self.addHost('h2', ip='10.1.1.3/24')
        
        # Add other hosts
        h3 = self.addHost('h3', ip='10.0.0.4/24')
        h4 = self.addHost('h4', ip='10.0.0.5/24')
        h5 = self.addHost('h5', ip='10.0.0.6/24')
        h6 = self.addHost('h6', ip='10.0.0.7/24')
        h7 = self.addHost('h7', ip='10.0.0.8/24')
        h8 = self.addHost('h8', ip='10.0.0.9/24')

        # Internal links to NAT (h9)
        self.addLink(h1, h9, cls=TCLink, delay='5ms')
        self.addLink(h2, h9, cls=TCLink, delay='5ms')
        
        # External connectivity
        self.addLink(h9, s1, cls=TCLink, delay='5ms')  # h9 external side
        
        # Link remaining hosts to respective switches with 5ms delay
        self.addLink(h3, s2, cls=TCLink, delay='5ms')
        self.addLink(h4, s2, cls=TCLink, delay='5ms')
        self.addLink(h5, s3, cls=TCLink, delay='5ms')
        self.addLink(h6, s3, cls=TCLink, delay='5ms')
        self.addLink(h7, s4, cls=TCLink, delay='5ms')
        self.addLink(h8, s4, cls=TCLink, delay='5ms')

        # Add switch-switch links with 7ms latency
        self.addLink(s1, s2, cls=TCLink, delay='7ms')
        self.addLink(s2, s3, cls=TCLink, delay='7ms')
        self.addLink(s3, s4, cls=TCLink, delay='7ms')
        self.addLink(s4, s1, cls=TCLink, delay='7ms')
        self.addLink(s1, s3, cls=TCLink, delay='7ms')

def run():
    topo = LoopTopo()
    net = Mininet(topo=topo, switch=OVSSwitch, controller=OVSController, autoSetMacs=True)
    net.start()
    
    # Get host and switch objects
    h1, h2, h3, h4, h5, h6, h7, h8, h9 = net.get('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9')
    
    # Enable STP on all switches
    for sw in ['s1', 's2', 's3', 's4']:
        sw_obj = net.get(sw)
        sw_obj.cmd('ovs-vsctl set Bridge {} stp_enable=true'.format(sw))
    
    # Clear any existing IPs on h9
    h9.cmd("ip addr flush dev h9-eth0")
    h9.cmd("ip addr flush dev h9-eth1")
    h9.cmd("ip addr flush dev h9-eth2")
    
    # Create a bridge on h9 to join internal interfaces
    h9.cmd('ip link add name br0 type bridge')
    h9.cmd('ip link set br0 up')
    h9.cmd('ip link set h9-eth0 master br0')  # link to h1
    h9.cmd('ip link set h9-eth1 master br0')  # link to h2
    h9.cmd('ip addr add 10.1.1.1/24 dev br0')  # internal gateway IP
    
    # Set external IP
    h9.setIP('10.0.0.1/24', intf='h9-eth2')
    h9.cmd('ip addr add 172.16.10.10/24 dev h9-eth2')
    
    # Set default routes for internal hosts
    h1.cmd('ip route add default via 10.1.1.1')
    h2.cmd('ip route add default via 10.1.1.1')
    
    # Set default route on external hosts
    h3.cmd('ip route add default via 10.0.0.1')
    h4.cmd('ip route add default via 10.0.0.1')
    h5.cmd('ip route add default via 10.0.0.1')
    h6.cmd('ip route add default via 10.0.0.1')
    h7.cmd('ip route add default via 10.0.0.1')
    h8.cmd('ip route add default via 10.0.0.1')
    
    # Enable IP forwarding on NAT
    h9.cmd('sysctl -w net.ipv4.ip_forward=1')
    
    # Setup NAT: masquerade internal traffic via h9-eth2
    h9.cmd('iptables -t nat -F')
    h9.cmd('iptables -t nat -A POSTROUTING -s 10.1.1.0/24 -o h9-eth2 -j MASQUERADE')
    
    print("Waiting 30 seconds for routes/NAT to settle...")
    time.sleep(30)
    
    # Test connectivity
    print("\nTesting basic connectivity with pingAll:")
    net.pingAll()
    
    print("\nNetwork started with NAT configured. Use CLI to interact.")
    CLI(net)
    
    net.stop()

if __name__ == '_main_':
    setLogLevel('info')
    run()
