from socket import socket, AF_INET, SOCK_DGRAM
import socket as Socket
from packet import *
from threading import Thread
from typing import Tuple

# Creates to new server


class udphost():

    def __init__(self, id: int, ip: str = "192.168.0.1", 
                    gateway: Tuple[str, int] = ("192.168.0.2", 8080), port: int = 8888):
        self.ip = ip
        self.id = id
        self.default_gateway = gateway
        self.port = port

        hostname = Socket.gethostname()
        self.local_ip = Socket.gethostbyname(hostname)


        # initialization phase
        self.host_initialization()

        # self.host_loop() 

    def host_initialization(self):

        # Create hello packet
        packet = create_HELLO_packet(0, 10, self.ip)

        # Send hello packet to default gateway
        send_packet(self, packet)

    def broadcast_hello(self):
        msg = create_HELLO_packet(seq=0, TTL=50, src=self.local_ip)
        with Socket.socket(Socket.AF_INET, Socket.SOCK_DGRAM, Socket.IPPROTO_UDP) as sock:
            sock.setsockopt(Socket.SOL_SOCKET, Socket.SO_BROADCAST, 1)
            sock.sendto(msg, ("255.255.255.255", 8080))
        


        # Initializes new server and sets it up to receive packets
if __name__ == '__main__':
    print("Server Start...")
    udp_host = udphost(id=102, ip='192.168.2.1',
                           gateway=('192.168.2.2', 8882), port=8883)


def test_run(target_host: udphost, c, dst):
    thread = Thread(target=ping, args=(target_host, c, dst))
    thread.start()