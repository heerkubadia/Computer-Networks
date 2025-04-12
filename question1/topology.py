from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel

# Custom switch class that disables controller dependency
class StandaloneOVSSwitch(OVSSwitch):
    def start(self, controllers):
        # Override default to start without controllers
        return super().start([])

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
    net = Mininet(
        topo=topo,
        switch=StandaloneOVSSwitch,
        controller=None,
        autoSetMacs=True
    )
    net.start()

    # Enable STP on each bridge
    for sw in ['s1', 's2', 's3', 's4']:
        net.get(sw).cmd(f'ovs-vsctl set Bridge {sw} stp_enable=true')
        net.get(sw).cmd(f'ovs-vsctl set-fail-mode {sw} standalone')
        print(f'STP enabled on {sw}')

    print("Network started. Use CLI to interact.")
    CLI(net)
