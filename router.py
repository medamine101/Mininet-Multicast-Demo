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

    # Member variables
    cent: centroid # Specifies if this router is the centroid
    id: int # router id
    ip: str # ip address of the router displayed to the user
    seq: int # sequence number
    rt: routing_table # routing table
    broadcast_addresses: Set[str] = set() # set of broadcast addresses

    # initialize the router
    def __init__(self, id: int, ip: str):
        self.id = id
        self.ip = ip
        self.rt = routing_table()
        self.cent = centroid()
        self.seq = 0

        # Start thread for broadcasting HELLO packets
        Thread(target=self.broadcast_hello_packet,
                args=(self.id, DEFAULT_TTL)).start()

        # Start thread for handling and forwarding HELLO packets
        Thread(target=self.handle_hello_packet).start()

        # Start thread for handling multicast packets
        Thread(target=self.handle_multicast_packet).start()

        # Start thread that handles and forwards data packets to destination
        Thread(target=self.handle_data_packet).start()

    # Function that starts a loop to periodically broadcast HELLO packets
    def broadcast_hello_packet(self, src_id: int = 100, ttl: int = DEFAULT_TTL):

        # Set up socket
        sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        # Send HELLO every 3 seconds
        while True:

            # Collect all the broadcast addresses for each interface
            for interface in ni.interfaces():
                if (ni.ifaddresses(interface)[ni.AF_INET][0]['addr'] != '127.0.0.1'):
                    self.broadcast_addresses.add(ni.ifaddresses(interface)[
                                                    ni.AF_INET][0]['broadcast'])

            # Create HELLO packet
            msg = create_HELLO_packet(
                seq=self.seq, ttl=ttl, src_id=src_id, src_ip=self.ip)
            self.seq += 1

            # Send packet to all broadcast addresses
            for address in self.broadcast_addresses:
                # print('Sending To: ', address)
                sock.sendto(msg, (address, DISCOVERY_PORT))

            # print("List of broadcast addresses")
            # print(self.broadcast_addresses, "\n")
            # print("ID: ", src_id)
            # print(self.rt)
            # print(self.routing_table.__table__.items())

            # Sleep 3 seconds before sending next HELLO packet
            sleep(3)

    # Function to handle recieved HELLO packets and perform routing table updates
    def handle_hello_packet(self):

        # Set up socket
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        sock.bind(('0.0.0.0', DISCOVERY_PORT))

        # Loop to receive HELLO packets
        while True:

            # Receive packet
            data, addr = sock.recvfrom(1024)

            # Get ip address of all interfaces
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

            # Calculate the distance of the sender of the HELLO packet
            hop_distance = DEFAULT_TTL - ttl + 1                

            # If packet belongs to the self, ignore it
            if (src_id == self.id):
                continue

            # print("Received hello from ", src_ip, " from address ", addr, " hop distance ", hop_distance, " seq ", seq)

            # Var to determine if forwarding is needed
            forward = False

            # if the source is not in the routing table, add it
            if not self.rt.check_entry(src_id):
                # add to routing table
                forward = True
                self.rt.add_entry(
                    id=src_id, ip=src_ip, next_hop=addr[0], seq=seq, dist=hop_distance)
            # if the source is in the routing table but the hop distance is lesser than the current one and packet is newer, replace the routing table entry
            elif self.rt.get_seq(src_id) <= seq and self.rt.get_dist(src_id) >= hop_distance:
                forward = True
                # if self.rt.get_dist(src_id) > hop_distance:
                #     forward = True
                self.rt.remove_entry(src_id)  # remove old entry
                # add new entry with closer distance
                self.rt.add_entry(
                    id=src_id, ip=src_ip, next_hop=addr[0], seq=seq, dist=hop_distance)
            # In any other case, do not forward the packet and ignore it
            else:
                continue

            # If forwarding is needed, forward the packet
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
            print("Received data packet: ", packet, "from: ", addr)
            pkttype, seq, src, dst, data = decode_data_packet(packet)
            if self.cent.is_centroid:
                print('I am the centroid')
                for dest in self.cent.get_dests():
                    new_data_packet = create_data_packet(
                        pkttype=1, seq=seq, src=self.id, dst=dest, data=data)
                    sock.sendto(new_data_packet,
                                (self.rt.get_next_hop(dest), DATA_PORT))
                    if (data == 'end_of_transmission'):
                        self.cent = centroid()
            else:  # forward to destination
                print('Forwarding data packet to ', self.rt.get_ip(dst))
                sock.sendto(packet, (self.rt.get_next_hop(dst), DATA_PORT))
            # sleep(0.2)

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

    # Create and run router object
    udp_router = udprouter(id=device_id, ip=device_ip)
