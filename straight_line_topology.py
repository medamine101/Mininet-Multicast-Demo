from mininet.net import Mininet
from mininet.log import output
from mininet.cli import CLI

if __name__ == '__main__':

    net = Mininet()

    num_nodes = 8 

    # from 1 to num_nodes
    for i in range(1,num_nodes+1): 
        net.addHost('h%d'%i,ip=None)

    # from 1 to num_nodes-1 because the index starts from zero
    for i in range(1,num_nodes): 

        h1 = net.hosts[i-1]
        h2 = net.hosts[i]

        net.addLink(h2, h1, intfName1 = '%s-eth0'%h2.name, intfName2 = '%s-eth1'%h1.name)
        h2.intf('%s-eth0'%h2.name).setIP('10.0.%d.1'%i, 24) 
        h1.intf('%s-eth1'%h1.name).setIP('10.0.%d.2'%i, 24) 

    net.start()

    # Ping forward and backward nodes
    for i in range(0,num_nodes):
        node = net.hosts[i]

        fwdNode, bwNode = None, None

        output('%s -> '%node.name)

        if i!=0:
            bwNode = net.hosts[i-1]
            bwIP = bwNode.IP('%s-eth1'%bwNode.name)
            result = node.cmd('ping -c1 %s'%bwIP)
            sent, received = net._parsePing(result)

            output(('%s '%bwNode.name) if received else 'X ')

        if i!=7:
            fwdNode = net.hosts[i+1]
            fwdIP = fwdNode.IP('%s-eth0'%fwdNode.name)
            result = node.cmd('ping -c1 %s'%fwdIP)
            sent, received = net._parsePing(result)

            output(('%s '%fwdNode.name) if received else 'X ')

        output('\n')

    CLI(net)

    net.stop()