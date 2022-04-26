#!/usr/bin/python
#Topology for Assignment 5 Comnetii ECE423/544
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.cli import CLI
from mininet.node import Node
from mininet.link import Link
# from router import Router


# TODO: Create topology including routers and hosts
def custom_topo():

    #Create a Mininet Environment
    net = Mininet()

    #Create hosts and routers.
    #Also create a switch in case we would like to use it for sshd services (optional)
    info( "Creating nodes\n" )
    #Create switch to use with sshd
    #s1 = net.addSwitch ( 's1' )
    r1 = net.addHost( 'r1' , ip='192.168.1.2/24' )

    h1 = net.addHost( 'h1' , ip='192.168.1.1/24', defaultRoute= 'via 192.168.1.2')
    h2 = net.addHost( 'h2' , ip='192.168.2.1/24', defaultRoute= 'via 192.168.2.2')
    h3 = net.addHost( 'h3' , ip='192.168.3.1/24', defaultRoute= 'via 192.168.3.2')

    #Establishing the links from hosts to routers
    info( "Creating links\n" )
    net.addLink( h1, r1 )
    net.addLink( h2, r1, intfName2='r1-eth1', params2={'ip' : '192.168.2.2/24' } )
    net.addLink( h3, r1, intfName2='r1-eth2', params2={'ip' : '192.168.3.2/24' } )

    #Build the specified network
    info( "Building network\n" )
    net.build()
    return net