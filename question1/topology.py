from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel

class LoopTopo(Topo):
    def build(self):
        # Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        # Add hosts with IPs
        hosts = [
            ('h1', '10.0.0.2/24', s1),
            ('h2', '10.0.0.3/24', s1),
            ('h3', '10.0.0.4/24', s2),
            ('h4', '10.0.0.5/24', s2),
            ('h5', '10.0.0.6/24', s3),
            ('h6', '10.0.0.7/24', s3),
            ('h7', '10.0.0.8/24', s4),
            ('h8', '10.0.0.9/24', s4)
        ]
        for name, ip, switch in hosts:
            host = self.addHost(name, ip=ip)
            self.addLink(host, switch, cls=TCLink, delay='5ms')

        # Add switch-switch links with 7ms latency
        self.addLink(s1, s2, cls=TCLink, delay='7ms')
        self.addLink(s2, s3, cls=TCLink, delay='7ms')
        self.addLink(s3, s4, cls=TCLink, delay='7ms')
        self.addLink(s4, s1, cls=TCLink, delay='7ms')
        self.addLink(s1, s3, cls=TCLink, delay='7ms')

def run():
    topo = LoopTopo()
    net = Mininet(topo=topo, switch=OVSSwitch, controller=None, autoSetMacs=True)
    net.start()
    print("Network started. Use CLI to interact.")
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
