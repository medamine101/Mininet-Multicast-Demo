from socket import SO_REUSEPORT, SOL_SOCKET, socket, AF_INET, SOCK_DGRAM, SO_BROADCAST
import socket as Socket
from helpers import *
from packet import *
from threading import Thread
from typing import Tuple
from router import udprouter
import netifaces as ni
from sys import argv

# Creates to new server


class udphost(udprouter):

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

        # TODO thread that handles data packets and forward to destination
        # Thread(target=self.handle_data_packet).start()
        sleep(5)
        self.handle_multicast_data(data="hello hello helo")

    def handle_multicast_data(self, data: str):
        choice = input('Are you sending or receiving?')

        if (choice == 's'):
            hosts = input("To what hosts would you like to send to?")
            hosts = hosts.split(",")
            inthosts = []
            for i in range(0, len(hosts)):
                inthosts.append(int(hosts[i]))

            
            centroid_request_packet=create_centroid_request_packet(self.seq, self.id, inthosts[0],inthosts[1])
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
            print('Data packet data: ' + data)


if __name__ == '__main__':
    print("Router Started...")
    print(ni.interfaces())
    device_ip: str = ''
    for ifstring in ni.interfaces():
        if 'eth' in ifstring:
            device_ip = ni.ifaddresses(ifstring)[ni.AF_INET][0]['addr']
            break

    # if (device_ip == ''):
    #     device_ip = '10.10.0.200'

    # remove all .s from device_ip
    # device_id: int = int(device_ip.replace('.', '').replace('0', ''))

    # print("Device ID: ", device_id)
    # print("Device IP: ", device_ip)

    device_id = 0

    # check if argv 1 is a number between 1 and 254
    if (len(argv) > 1 and argv[1].isdigit() and int(argv[1]) >= 1 and int(argv[1]) <= 254):
        device_id = int(argv[1])
    else:
        print("Invalid device ID. Must be an integer between 1 and 254")
        exit(1)

    print("Device IP: ", device_ip)
    print("Device ID: ", device_id)

    udp_host = udphost(id=(device_id), ip=device_ip)
