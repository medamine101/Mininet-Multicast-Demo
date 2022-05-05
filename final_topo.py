from mininet.net import Mininet
from mininet.log import output
from mininet.cli import CLI

if __name__ == '__main__':

    net = Mininet()

    r1 = net.addHost('r1',ip='None')
    r2 = net.addHost('r2',ip='None')
    r3 = net.addHost('r3',ip='None')
    r4 = net.addHost('r4',ip='None')
    r5 = net.addHost('r5',ip='None')

    s = net.addHost('s',ip='None')

    d1 = net.addHost('d1',ip='None')
    d2 = net.addHost('d2',ip='None')
    d3 = net.addHost('d3',ip='None')

    net.addLink(s, r1, intfName1 = '%s-eth0'%s.name, intfName2 = '%s-eth0'%r1.name)
    s.intf('%s-eth0'%s.name).setIP('10.0.1.1', 24)
    r1.intf('%s-eth0'%r1.name).setIP('10.0.1.2', 24)

    net.addLink(r1, r2, intfName1 = '%s-eth1'%r1.name, intfName2 = '%s-eth0'%r2.name)
    r1.intf('%s-eth1'%r1.name).setIP('10.0.2.1', 24)
    r2.intf('%s-eth0'%r2.name).setIP('10.0.2.2', 24)
    
    net.addLink(r2, d1, intfName1 = '%s-eth1'%r2.name, intfName2 = '%s-eth0'%d1.name)
    r2.intf('%s-eth1'%r2.name).setIP('10.0.11.1', 24)
    d1.intf('%s-eth0'%d1.name).setIP('10.0.11.2', 24)

    net.addLink(r1, r3, intfName1 = '%s-eth2'%r1.name, intfName2 = '%s-eth0'%r3.name)
    r1.intf('%s-eth2'%r1.name).setIP('10.0.3.1', 24)
    r3.intf('%s-eth0'%r3.name).setIP('10.0.3.2', 24)

    net.addLink(r3, r4, intfName1 = '%s-eth1'%r3.name, intfName2 = '%s-eth0'%r4.name)
    r3.intf('%s-eth1'%r3.name).setIP('10.0.4.1', 24)
    r4.intf('%s-eth0'%r4.name).setIP('10.0.4.2', 24)

    net.addLink(r3, r5, intfName1 = '%s-eth2'%r3.name, intfName2 = '%s-eth0'%r5.name)
    r3.intf('%s-eth2'%r3.name).setIP('10.0.6.1', 24)
    r5.intf('%s-eth0'%r5.name).setIP('10.0.6.2', 24)

    net.addLink(r4, r5, intfName1 = '%s-eth1'%r4.name, intfName2 = '%s-eth1'%r5.name)
    r4.intf('%s-eth1'%r4.name).setIP('10.0.5.1', 24)
    r5.intf('%s-eth1'%r5.name).setIP('10.0.5.2', 24)

    net.addLink(r4, d2, intfName1 = '%s-eth2'%r4.name, intfName2 = '%s-eth0'%d2.name)
    r4.intf('%s-eth2'%r4.name).setIP('10.0.12.1', 24)
    d2.intf('%s-eth0'%d2.name).setIP('10.0.12.2', 24)

    net.addLink(r5, d3, intfName1 = '%s-eth2'%r5.name, intfName2 = '%s-eth0'%d3.name)
    r5.intf('%s-eth2'%r5.name).setIP('10.0.13.1', 24)
    d3.intf('%s-eth0'%d3.name).setIP('10.0.13.2', 24)

    CLI(net)

    net.stop()