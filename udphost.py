from socket import SO_REUSEPORT, SOL_SOCKET, socket, AF_INET, SOCK_DGRAM
import socket as Socket
from helpers import DATA_PORT
from packet import *
from threading import Thread
from typing import Tuple
from router import udprouter
from netifaces import ni

# Creates to new server


class udphost(udprouter):

    def __init__(self, id: int, ip: str):
        super().__init__(id, ip)

    def handle_multicast_data(self, data: str):
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        sock.bind(('0.0.0.0', DATA_PORT))
        choice = input('Are you sending or receiving?')
        if (choice == 'sending'):
            h7 = -1
            h8 = -1
            create_centroid_request_packet(self.seq, self.id, h7, h8)
            # wait for centroid reply
            packet, addr = sock.recvfrom(10)
            # decode data packet
            centroid, dst = decode_centroid_reply_packet(packet)
            # send data packet to centroid
            data_packet = create_data_packet(
                pkttype=1, seq=self.seq, src=self.id, dst=centroid, data='hello, this is a test')
            sock.sendto(
                data_packet, (self.rt.get_next_hop(centroid), DATA_PORT))
        else:
            data_packet = sock.recvfrom(1024)
            pkttype, seq, src, dst, data = decode_data_packet(data_packet)
            print('Received data packet from ' + str(src) + ' to ' + str(dst))


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
