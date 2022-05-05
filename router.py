from cgi import print_arguments
from socket import gethostbyname_ex, getfqdn, gethostname, gethostbyname, socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR, SO_BROADCAST, IPPROTO_UDP, getaddrinfo, SO_REUSEPORT
from threading import Thread
from turtle import forward
from packet import *
from time import sleep
import netifaces as ni
from helpers import *
from typing import Tuple, Type, Set
from sys import argv


class udprouter():

    cent: centroid
    id: int
    ip: str
    seq: int
    rt: routing_table
    broadcast_addresses: Set[str] = set()

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

    def handle_sending(self, packet, server):
        s = socket(AF_INET, SOCK_DGRAM)
        s.sendto(packet, server)
        # print('Sending To: ', server)
        s.close()
        return 0

    def broadcast_hello_packet(self, src_id: int = 100, ttl: int = DEFAULT_TTL):

        sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        # Send HELLO every 10 seconds
        while True:

            for interface in ni.interfaces():
                if (ni.ifaddresses(interface)[ni.AF_INET][0]['addr'] != '127.0.0.1'):
                    self.broadcast_addresses.add(ni.ifaddresses(interface)[
                                                    ni.AF_INET][0]['broadcast'])

            msg = create_HELLO_packet(
                seq=self.seq, ttl=ttl, src_id=src_id, src_ip=self.ip)
            self.seq += 1

            for address in self.broadcast_addresses:
                # print('Sending To: ', address)
                sock.sendto(msg, (address, DISCOVERY_PORT))

            # print("List of broadcast addresses")
            # print(self.broadcast_addresses, "\n")

            # print("ID: ", src_id)
            # print(self.rt)
            sleep(3)
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

            # if (self.rt.check_entry(src_id)):
            #     if (self.rt.get_dist(src_id) < hop_distance):
            #         continue
                

            if (src_id == self.id):
                continue
            # print("Received hello from ", src_ip, " from address ", addr, " hop distance ", hop_distance, " seq ", seq)
            forward = False
            # if the source is not in the routing table
            if not self.rt.check_entry(src_id):
                # add to routing table
                forward = True
                self.rt.add_entry(
                    id=src_id, ip=src_ip, next_hop=addr[0], seq=seq, dist=hop_distance)
            # if the source is in the routing table but the hop distance is lesser than the current one and packet is newer
            elif self.rt.get_seq(src_id) <= seq and self.rt.get_dist(src_id) >= hop_distance:
                forward = True
                # if self.rt.get_dist(src_id) > hop_distance:
                #     forward = True
                self.rt.remove_entry(src_id)  # remove old entry
                # add new entry with closer distance
                self.rt.add_entry(
                    id=src_id, ip=src_ip, next_hop=addr[0], seq=seq, dist=hop_distance)
            # # if sequence numbers are the same and hop distance 
            # elif (self.rt.get_seq(src_id) == seq) and (self.rt.get_dist(src_id) < hop_distance):
            else:
                continue

            if (ttl > 0 and forward):
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
        sock.bind(('0.0.0.0', CENTROID_SETUP_PORT))

        while True:
            data, addr = sock.recvfrom(1024)
            # decode multicast packet
            if len(data) == 2:  # handle centroid reply
                src, dst = decode_centroid_reply_packet(data)
                print("Received centoird packet from ", self.rt.get_ip(src))
                if (src == self.id):
                    continue
                sock.sendto(
                    data, (self.rt.get_next_hop(dst), CENTROID_SETUP_PORT))
            else:  # handle centroid request
                pkttype, seq, src, N, dests = decode_centroid_request_packet(
                    data)

                print("Received centoird packet from ", self.rt.get_ip(src))

                if (src == self.id): # ignore if packet is from self
                    continue
                # check if there is a bifurcation
                possible_next_hops = set()
                for dest in dests:
                    possible_next_hops.add(self.rt.get_next_hop(dest))

                if len(possible_next_hops) > 1:  # bifurcation -> reply with centroid reply
                    centroid_reply = create_centroid_reply_packet(
                        src=self.id, dst=src)
                    sock.sendto(centroid_reply, (self.rt.get_next_hop(src), CENTROID_SETUP_PORT))
                    self.cent.set_centroid(dests=dests)

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
            print("Received data packet: ", packet, "from: ", addr)
            pkttype, seq, src, dst, data = decode_data_packet(packet)
            if self.cent.is_centroid:
                print('I am the centroid')
                for dest in self.cent.get_dests():
                    # TODO reconstruct data packet with correct dest and send it
                    # new_data_packet = create_data_packet()
                    new_data_packet = create_data_packet(
                        pkttype=1, seq=seq, src=self.id, dst=dest, data=data)
                    sock.sendto(new_data_packet,
                                (self.rt.get_next_hop(dest), DATA_PORT))
                self.cent = centroid()
            else:  # forward to destination
                print('Forwarding data packet to ', self.rt.get_ip(dst))
                sock.sendto(packet, (self.rt.get_next_hop(dst), DATA_PORT))
            sleep(1)

if __name__ == '__main__':
    print("Router Started...")

    # Print all interfaces
    print(ni.interfaces())

    # Get the ip address to be used on print displays to the user
    device_ip: str = ''
    for ifstring in ni.interfaces():
        if 'eth' in ifstring:
            device_ip = ni.ifaddresses(ifstring)[ni.AF_INET][0]['addr']
            break
    
    # Take device ID as command line argument, must be between 1 and 254
    device_id = 0
    if (len(argv) > 1 and argv[1].isdigit() and int(argv[1]) >= 1 and int(argv[1]) <= 254):
        device_id = int(argv[1])
    else:
        print("Invalid device ID. Must be an integer between 1 and 254")
        exit(1)

    # Print the device IP and ID to the user
    print("Device IP: ", device_ip)
    print("Device ID: ", device_id)
    udp_router = udprouter(id=device_id, ip=device_ip)
