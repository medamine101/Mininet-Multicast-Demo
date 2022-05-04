from socket import socket, AF_INET, SOCK_DGRAM
import socket as Socket
from packet import *
from threading import Thread
from typing import Tuple

# Creates to new server


class udphost(udprouter):

    def __init__(self, id:int, port:int):
        # self.su
        pass


if __name__ == '__main__':
    print("Host Started...")
    udp_host = udphost(id=201, port=8080)
    udp_host.broadcast_hello_packet()
    # udp_router.handle_packets()
    