import sys
from mininet.cli import CLI
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.log import setLogLevel
from mininet.node import Node
# from custom_topo import


def main():
    
    net = custom_topo()

    net.start()


    # Enter CLI
    CLI(net)
    # CLI(net, sys.stdin, script='./script.txt')

    # Stop the network
    net.stop()











if __name__ == "__main__":
    main()