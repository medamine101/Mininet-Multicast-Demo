#/usr/bin/python
#Comnetsii APIs for Packet. Rutgers ECE423/544
#Author: Sumit Maheshwari
import time
from socket import socket, AF_INET, SOCK_DGRAM
import struct
import select
import random
import asyncore
import numpy as np

def create_packet(pkttype, src, dst, seq, data):
    """Create a new packet based on given id"""
    # Type(1),  LEN(4), SRCID(1),  DSTID(1), SEQ(4), DATA(1000)
    pktlen = len(data)
    header = struct.pack('BLBBL', pkttype, pktlen, dst, src, seq)
    return header + bytes(data,'utf-8')

def read_header(pkt):
    #Change the bytes to account for network encapsulations
    header = pkt[0:32]
    #pktFormat = "BLBBL"
    #pktSize = struct.calcsize(pktFormat)
    pkttype, pktlen, dst, src, seq = struct.unpack('BLBBL', header)
    return pkttype, pktlen, dst, src, seq

def read_data(pkt):
        #Change the bytes to account for network encapsulations
    data = pkt[32:]
    return data




###################################
####   Assignment Code Below   ####
###################################

#Starts a ping from current host (src) to desired destination (dst)
def ping(h, c, dst):
    seq_num, nor, rtt = 0, 0, []
    #count = 0
    for x in range(c):
        #count += 1
        # Creates and sends the request packet
        packet = create_packet(1, h.id, dst, seq=seq_num, data='This is assignment 5!')
        send_packet(h, packet)
        send_time = time.time()

        # Waits to receive a reply packet to move onto next ping
        seq_failed = receive_packet(h, packet)
        if seq_failed == -1:
            rtt.append(time.time()-send_time)
            seq_num += 1
        else:
            x -= 1
            nor += 1
            print("Retransmitting packet with seq num: ", seq_num)
    rtt = np.array(rtt)
    #print(count)
    print(c, " packets transmitted, ", nor, " packets retransmitted, ", (nor/c)*100, "% packet loss",
         "\n round-trip min/avg/max/stddev = ", np.min(rtt),"/",np.mean(rtt),"/",np.max(rtt),"/",np.std(rtt), " s" )
    return 0

# Sends a packet across UDP socket the corresponding router gateway for that host
def send_packet(h, packet):
    s = socket(AF_INET, SOCK_DGRAM)
    s.sendto(packet, h.default_gateway)
    s.close()
    print("Sending: ", packet, " To: ", h.default_gateway)
    return 0

# Receives packets across UDP socket
def receive_packet(h, sent_packet):
    s = socket(AF_INET, SOCK_DGRAM)
    s.bind((h.ip, h.port))
    seq_failed = -1

    #Waits to receive packet on h.ip/h.port
    while True:
        try:
            if sent_packet != None:
                s.settimeout(0.007)
            packet,addr = s.recvfrom(1024)
            pkttype, pktlen, dst, src, seq = read_header(packet)
        except OSError:
            pkttype, pktlen, dst, src, seq = read_header(sent_packet)
            seq_failed = seq
            break

        if(pkttype == 1 and dst == h.id):
            print("Received: ", packet, " From: ", src)

            # Creates reply packet
            packet = create_packet(2, h.id, src, 0, 'This is a reply!')
            send_packet(h, packet)

        # Checks for reply packet (Note this is not very flexable and would break the server if it receives reply packet)
        elif(pkttype == 2 and dst == h.id):
            #data = read_data(packet)
            print("Receved: ", packet, " From: ", src)
            break

    s.close()
    return  seq_failed