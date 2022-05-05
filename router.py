from cgi import print_arguments
from socket import gethostbyname_ex, getfqdn, gethostname, gethostbyname, socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR, SO_BROADCAST, IPPROTO_UDP, getaddrinfo, SO_REUSEPORT
from threading import Thread
from turtle import forward
from packet import *
from time import sleep
import netifaces as ni
from helpers import *
from typing import Tuple, Type


class udprouter():

    cent: centroid
    id: int
    ip: str
    seq: int
    rt: routing_table
    broadcast_addresses: List[str] = []

    # each router know other routers' rt
    def __init__(self, id: int, ip: str):
        self.id = id
        self.ip = ip
        self.rt = routing_table()
        self.cent = centroid()
        self.seq = 0

        # thread for broadcasting hello
        Thread(
            target=self.broadcast_hello_packet, args=(self.id, DEFAULT_TTL)).start()

        # thread for handling hello and forwarding it
        Thread(target=self.handle_hello_packet).start()

        # thread for handling regular packets
        Thread(target=self.handle_multicast_packet).start()

        # TODO thread that handles data packets and forward to destination
        Thread(target=self.handle_data_packet).start()

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
        # print('Sending To: ', server)
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

    def broadcast_hello_packet(self, src_id: int = 100, ttl: int = DEFAULT_TTL):

        sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        # Send HELLO every 10 seconds
        while True:

            for interface in ni.interfaces():
                if (ni.ifaddresses(interface)[ni.AF_INET][0]['addr'] != '127.0.0.1'):
                    self.broadcast_addresses.append(ni.ifaddresses(interface)[
                                                    ni.AF_INET][0]['broadcast'])
                # broadcast_addresses.append(ni.ifaddresses(interface)[ni.AF_INET][0]['broadcast'])
                # print(ni.ifaddresses(interface)[ni.AF_INET][0])

            msg = create_HELLO_packet(
                seq=self.seq, ttl=ttl, src_id=src_id, src_ip=self.ip)
            self.seq += 1

            for address in self.broadcast_addresses:
                # print('Sending To: ', address)
                sock.sendto(msg, (address, DISCOVERY_PORT))

            print("ID: ", src_id)
            print(self.rt)
            sleep(10)
            # print(self.routing_table.__table__.items())

    def handle_hello_packet(self):
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        sock.bind(('0.0.0.0', DISCOVERY_PORT))

        while True:
            data, addr = sock.recvfrom(1024)

            # Get ip address of all interfaces from ifconfig
            addresses: List[str] = []
            for interface in ni.interfaces():
                addresses.append(ni.ifaddresses(interface)
                                 [ni.AF_INET][0]['addr'])

            # Ignore packet if sent from self
            if (addr[0] in addresses):
                continue

            # print("Received From: ", addr)
            # print(data)

            # Get hello packet data
            pkttype, seq, ttl, src_id, src_ip = decode_HELLO_packet(data)
            hop_distance = DEFAULT_TTL - ttl + 1

            if (src_id == self.id):
                continue

            # if the source is not in the routing table
            if not self.rt.check_entry(src_id):
                # add to routing table
                self.rt.add_entry(
                    id=src_id, ip=src_ip, next_hop=addr[0], seq=seq, dist=hop_distance)
            # if the source is in the routing table but the hop distance is lesser than the current one
            elif self.rt.get_seq(src_id) < seq and self.rt.get_dist(src_id) < hop_distance:
                self.rt.remove_entry(src_id)  # remove old entry
                # add new entry with closer distance
                self.rt.add_entry(
                    id=src_id, ip=src_ip, next_hop=addr[0], seq=seq, dist=hop_distance)
            else:
                continue

            if ttl > 0:
                self.forward_hello_packet(data)

    def forward_hello_packet(self, data):
        sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        pkttype, seq, ttl, src_id, src_ip = decode_HELLO_packet(data)
        forwarded_packet = create_HELLO_packet(
            seq=seq, ttl=ttl-1, src_id=src_id, src_ip=src_ip)
        # print("Forwarded packet: ", forwarded_packet)
        for address in self.broadcast_addresses:
            sock.sendto(forwarded_packet, (address, DISCOVERY_PORT))

    def handle_multicast_packet(self):
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        sock.bind(('0.0.0.0', CENTROID_SETUP_PORT))

        while True:
            data, addr = sock.recvfrom(1024)
            # decode multicast packet
            if len(data) == 2:  # handle centroid reply
                src, dst = decode_centroid_reply_packet(data)
                sock.sendto(
                    data, (self.rt.get_next_hop(dst), CENTROID_SETUP_PORT))
            else:  # handle centroid request
                pkttype, seq, src, N, dests = decode_centroid_request_packet(
                    data)
                # check if there is a bifurcation
                possible_next_hops = set()
                for dest in dests:
                    possible_next_hops.add(self.rt.get_next_hop(dest))

                if len(possible_next_hops) > 1:  # bifurcation -> reply with centroid reply
                    centroid_reply = create_centroid_reply_packet(
                        src=self.id, dst=src)
                    sock.sendto(centroid_reply, addr)
                    self.centroid = True

                else:  # no bifurcation -> forward the centroid request to next hop
                    for dest in possible_next_hops:
                        sock.sendto(data, (dest, CENTROID_SETUP_PORT))

    def handle_data_packet(self):
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        sock.bind(('0.0.0.0', DATA_PORT))

        while True:
            packet, addr = sock.recvfrom(1024)
            # decode data packet
            # pkttype, seq, ttl, src_id, src_ip, dest_id, dest_ip, data_type, data_content = decode_data_packet(data)
            pkttype, seq, src, dst, data = decode_data_packet(packet)
            if self.cent.is_centroid:
                for dest in self.cent.get_dests():
                    # TODO reconstruct data packet with correct dest and send it
                    # new_data_packet = create_data_packet()
                    new_data_packet = create_data_packet(
                        pkttype=1, seq=seq, src=self.id, dst=dst, data=data)
                    sock.sendto(new_data_packet,
                                (self.rt.get_next_hop(dest), DATA_PORT))
                    sock.sendto(new_data_packet, self.rt.get_next_hop(dest))
            elif pkttype == 2:  # forward to destination
                sock.sendto(packet, self.rt.get_next_hop(dst))


if __name__ == '__main__':
    print("Router Started...")
    print(ni.interfaces())
    device_ip: str = ''
    for ifstring in ni.interfaces():
        if 'eth' in ifstring:
            device_ip = ni.ifaddresses(ifstring)[ni.AF_INET][0]['addr']
            break

    if (device_ip == ''):
        device_ip = '10.10.0.200'

    # remove all .s from device_ip
    device_id: int = int(device_ip.replace('.', '').replace('0', ''))

    # print("Device IP: ", device_ip)
    # print("Device ID: ", device_id)
    udp_router = udprouter(id=device_id, ip=device_ip)
