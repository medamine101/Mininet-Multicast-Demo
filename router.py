from cgi import print_arguments
from socket import gethostbyname_ex, getfqdn, gethostname, gethostbyname, socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR, SO_BROADCAST, IPPROTO_UDP, getaddrinfo, SO_REUSEPORT
from threading import Thread
from turtle import forward
from packet import *
from time import sleep
import netifaces as ni
from helpers import *

class udprouter():

    broadcast_addresses: List[str] = []

    # each router know other routers' rt
    def __init__(self, id:int):
        self.id = id
        self.routing_table = routing_table()
        self.seq = 0

        # thread for broadcasting hello
        broadcast_thread = Thread(target=self.broadcast_hello_packet, args=(self.id, DEFAULT_TTL))
        broadcast_thread.start()

        # thread for handling hello and forwarding it
        handle_hello_packet_thread = Thread(target=self.handle_hello_packet)
        handle_hello_packet_thread.start()

        # thread for handling regular packets
        handle_regular_packet_thread = Thread(target=self.handle_unicast_packet)
        handle_regular_packet_thread.start()





    # Using the dst received in packet find the corresponding dst address
    # def search_dst_addr(self, dst):
    #     for x in range(len(self.rt['routes'])):
    #         if self.rt['routes'][x]['id'] == dst:
    #             return (self.rt['routes'][x]['ip'], self.rt['routes'][x]['port'])
    #     return ('10.0.1.1', 8882)

    # Sends packet to dst address
    def handle_sending(self, packet, server):
        s = socket(AF_INET, SOCK_DGRAM)
        s.sendto(packet, server)
        print('Sending To: ', server)
        s.close()
        return 0

    # Waits to receive a packet and if the correct type starts new thread to sent that packet
    # def handle_packets(self):
    #     s = socket(AF_INET, SOCK_DGRAM)
    #     s.bind(('0.0.0.0', self.port))
    #     while True:
    #         packet, addr = s.recvfrom(1024)
    #         print("Received From: ", addr)
    #         pkttype, pktlen, dst, src, seq = read_header(packet)
    #         if pkttype == 1 or pkttype == 2:
    #             server = self.search_dst_addr(dst)
    #             thread = Thread(target=self.handle_sending, args = (packet, server))
    #             thread.start()
    #     s.close()
    #     return 0

    def broadcast_hello_packet(self, src_id:int = 100, ttl:int = DEFAULT_TTL):

        sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        # Send HELLO every 10 seconds
        while True:

            for interface in ni.interfaces():
                if (ni.ifaddresses(interface)[ni.AF_INET][0]['addr'] != '127.0.0.1'):
                    self.broadcast_addresses.append(ni.ifaddresses(interface)[ni.AF_INET][0]['broadcast'])
                # broadcast_addresses.append(ni.ifaddresses(interface)[ni.AF_INET][0]['broadcast'])
                # print(ni.ifaddresses(interface)[ni.AF_INET][0])

            msg = create_HELLO_packet(seq=self.seq, ttl=ttl, src_id=src_id)
            self.seq += 1

            for address in self.broadcast_addresses:
                print('Sending To: ', address)
                sock.sendto(msg, (address, BROADCAST_PORT))

            sleep(10)
            # print(self.routing_table.__table__.items())


    def handle_hello_packet(self):
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        sock.bind(('0.0.0.0', BROADCAST_PORT))

        while True:
            data, addr = sock.recvfrom(4)

            # Get ip address of all interfaces from ifconfig
            addresses: List[str] = []
            for interface in ni.interfaces():
                addresses.append(ni.ifaddresses(interface)[ni.AF_INET][0]['addr'])

            # Ignore packet if sent from self
            if (addr[0] in addresses):
                continue

            print("Received From: ", addr)
            print(data)

            # Get hello packet data
            pkttype, seq, ttl, src_id = decode_HELLO_packet(data)

            hop_distance = DEFAULT_TTL - ttl
            
            # if the source is not in the routing table
            if not self.routing_table.check_entry(src_id):
                # add to routing table
                self.routing_table.add_entry(id=src_id, ip=addr[0], seq=seq, dist=hop_distance)
            # if the source is in the routing table but the hop distance is lesser than the current one
            elif self.routing_table.get_seq(src_id) < seq and self.routing_table.get_dist(src_id) < hop_distance:
                self.routing_table.remove_entry(src_id) # remove old entry
                self.routing_table.add_entry(id=src_id, ip=addr[0], seq=seq, dist=hop_distance) # add new entry with closer distance
            else:
                continue

            self.forward_packet(data)

    def forward_packet(self, data):
        sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        pkttype, seq, ttl, src_id = decode_HELLO_packet(data)
        forwarded_packet = create_HELLO_packet(seq=seq, ttl=ttl-1, src_id=src_id)

        for address in self.broadcast_addresses:
            sock.sendto(forwarded_packet, (address, BROADCAST_PORT))


    def handle_unicast_packet(self):
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        sock.bind(('0.0.0.0', UNICAST_PORT))

        while True:
            data, addr = sock.recvfrom(1024)

    





if __name__ == '__main__':
    print("Router Started...")
    print(ni.interfaces())
    device_ip:str = ''
    for ifstring in ni.interfaces():
        if (ifstring.endswith('eth0')):
            device_ip = ni.ifaddresses(ifstring)[ni.AF_INET][0]['addr']
            break

    if (device_ip == ''):
        device_ip = '10.10.0.200'

    # remove all .s from device_ip
    device_id:int = int(device_ip.replace('.', '').replace('0', ''))


    # print("Device IP: ", device_ip)
    # print("Device ID: ", device_id)

    udp_router = udprouter(id=device_id)
    # udp_router.broadcast_hello_packet()
    # udp_router.handle_packets()