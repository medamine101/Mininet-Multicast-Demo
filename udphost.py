from socket import SO_REUSEPORT, SOL_SOCKET, socket, AF_INET, SOCK_DGRAM, SO_BROADCAST
import socket as Socket
from helpers import *
from packet import *
from threading import Thread
from typing import Tuple
from router import udprouter
import netifaces as ni

# Creates to new server


class udphost(udprouter):

    def __init__(self, id: int, ip: str):
        super().__init__(id, ip)
        sleep(5)
        self.handle_multicast_data(data="hello hello helo")

    def handle_multicast_data(self, data: str):
        choice = input('Are you sending or receiving?')
        if choice == 'unicast':
            data_packet = create_data_packet(
                pkttype=1, seq=self.seq, src=self.id, dst=231, data='hello, this is a test')
            data_sock = socket(AF_INET, SOCK_DGRAM)
            data_sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
            print("Sending data packet to ", self.rt.get_next_hop(231))
            # data_sock.bind((self.rt.get_next_hop(centroid), DATA_PORT))
            data_sock.sendto(data_packet, (self.rt.get_next_hop(231), DATA_PORT))

            

        if (choice == 'sending'):
            h7 = 171
            h8 = 231
            centroid_request_packet=create_centroid_request_packet(self.seq, self.id, h7,h8)
            for addr in self.broadcast_addresses:
                sock = socket(AF_INET, SOCK_DGRAM)
                sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
                sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
                sock.bind((addr, CENTROID_SETUP_PORT))
                print(addr)
                sock.sendto(centroid_request_packet, (addr, CENTROID_SETUP_PORT))
                sock.close()

            # wait for centroid reply
            centsock = socket(AF_INET, SOCK_DGRAM)
            centsock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
            centsock.bind(('0.0.0.0', CENTROID_SETUP_PORT))
            packet, addr = centsock.recvfrom(10)
            # decode data packet
            centroid, dst = decode_centroid_reply_packet(packet)

            print('received centroid reply from centroid {}'.format(self.rt.get_ip(centroid)))
            # send data packet to centroid
            data_packet = create_data_packet(
                pkttype=1, seq=self.seq, src=self.id, dst=centroid, data='hello, this is a test')

            data_sock = socket(AF_INET, SOCK_DGRAM)
            data_sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
            print("Sending data packet to ", self.rt.get_next_hop(centroid))
            # data_sock.bind((self.rt.get_next_hop(centroid), DATA_PORT))
            data_sock.sendto(data_packet, (self.rt.get_next_hop(centroid), DATA_PORT))
            data_sock.close()
            print('Sent data packet to centroid', data_packet)
        else:
            sock = socket(AF_INET, SOCK_DGRAM)
            sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
            sock.bind(('0.0.0.0', DATA_PORT))
            data_packet, addr = sock.recvfrom(1024)
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
    print('Device ID: ', device_id)
    print('Device IP: ', device_ip)

    udp_host = udphost(id=(device_id%255), ip=device_ip)
