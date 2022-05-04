from socket import socket, AF_INET, SOCK_DGRAM
import socket as Socket
from packet import *
from threading import Thread
from typing import Tuple
from router import udprouter
from netifaces import ni

# Creates to new server


class udphost(udprouter):

    def __init__(self, id:int, ip:str):
        super().__init__(id, ip)

    def send_multicast_data(self, data:str):
        h8 = -1
        create_centroid_request_packet(self.seq, self.id, h8)
        # wait for centroid reply
        
        
    


if __name__ == '__main__':
    print("Host Started...")

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

    udp_host = udphost(id=(device_id+100), ip=device_ip)
    