from socket import gethostname, gethostbyname, socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR, SO_BROADCAST, IPPROTO_UDP, getaddrinfo, SO_REUSEPORT
from threading import Thread
from packet import *
from time import sleep
import netifaces as ni
from helpers import *

class udprouter():

    # each router know other routers' rt
    def __init__(self, id, port):
        self.port = port
        self.id = id
        self.routing_table = routing_table()

        # thread for broadcasting hello
        thread = Thread(target=self.broadcast_hello)
        thread.start()

        # thread for handling hello
        thread = Thread(target=self.handle_hello)
        thread.start()


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

    def broadcast_hello(self):

        msg = create_HELLO_packet(seq=0, TTL=50, src_id=100)

        sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        # Send HELLO every 10 seconds
        while True:
            sock.sendto(msg, (BROADCAST_ADDRESS, BROADCAST_PORT))
            sleep(10)


    def handle_hello(self):
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        sock.bind(('', BROADCAST_ADDRESS))

        



        

        # one thread for keeping the routing table updated
        
        # on thread for handling multicast 




if __name__ == '__main__':
    print("Router Started...")
    udp_router = udprouter(id=201, port=8080)
    udp_router.broadcast_hello()
    # udp_router.handle_packets()