# /usr/bin/python
# Comnetsii APIs for Packet. Rutgers ECE423/544
# Author: Sumit Maheshwari
import imp
import time
from socket import socket, AF_INET, SOCK_DGRAM
import struct
import select
import random
import asyncore
# import numpy as np
from typing import List, Union, Tuple
# from udphost import udphost
# from router import udprouter

def create_packet(pkttype, src, dst, seq, data):
    """Create a new packet based on given id"""
    # Type(1),  LEN(4), SRCID(1),  DSTID(1), SEQ(4), DATA(1000)
    pktlen = len(data)
    header = struct.pack('BLBBL', pkttype, pktlen, dst, src, seq)
    return header + bytes(data, 'utf-8')

def read_header(pkt):
    # Change the bytes to account for network encapsulations
    header = pkt[0:32]
    # pktFormat = "BLBBL"
    # pktSize = struct.calcsize(pktFormat)
    pkttype, pktlen, dst, src, seq = struct.unpack('BLBBL', header)
    return pkttype, pktlen, dst, src, seq

def read_data(pkt):
    # Change the bytes to account for network encapsulations
    data = pkt[32:]
    return data

##################################
#  Different Packet Types Below ##
##################################

# Hello packet type = 0
def create_HELLO_packet(seq: int, ttl: int, src_id: int, src_ip: str, pkttype: int = 0) -> bytes:
    # Create packet for HELLO
    # Type (1), seq (1), TTL (1), src_id (1)
    # print("IP: ", src_ip)
    packet: bytes = struct.pack(
        'BBBB', pkttype, seq, ttl, src_id) + src_ip.encode('utf-8')
    # print("Packet: ", packet)
    return packet

def decode_HELLO_packet(packet: bytes) -> Tuple[int, int, int, int, str]:
    # Decode HELLO packet
    # Type (1), seq (1), TTL (1), src_id (1)
    pkttype, seq, ttl, src_id = struct.unpack('BBBB', packet[:4])
    ip = packet[4:].decode('utf-8')
    # print(packet)
    return pkttype, seq, ttl, src_id, ip


def create_centroid_request_packet(seq: int, src: int, *dests: int) -> bytes:
    # Create packet for centroid request
    # Type (1), seq (1), src (1), N (1), dests (1)
    N = len(dests)
    pkttype = 1 # Centroid request

    if N == 1:
        packet: bytes = struct.pack('BBBBB', pkttype, seq, src, N, dests[0])
    elif N == 2:
        packet: bytes = struct.pack(
            'BBBBBB', pkttype, seq, src, N, dests[0], dests[1])
    elif N == 3:
        packet: bytes = struct.pack(
            'BBBBBBB', pkttype, seq, src, N, dests[0], dests[1], dests[2])
    else:
        print("Invalid number!")
        packet = struct.pack('BBBBB', pkttype, seq, src, N, dests[0])

    return packet


def decode_centroid_request_packet(packet: bytes) -> Tuple[int, int, int, int, List[int]]:

    packet_size = len(packet)

    if packet_size == 5:
        pkttype, seq, src, N, dest = struct.unpack('BBBBB', packet)
        dests = [dest]
    elif packet_size == 6:
        pkttype, seq, src, N, dest1, dest2 = struct.unpack('BBBBBB', packet)
        dests = [dest1, dest2]
    elif packet_size == 7:
        pkttype, seq, src, N, dest1, dest2, dest3 = struct.unpack('BBBBBBB', packet)
        dests = [dest1, dest2, dest3]
    else:
        print("Invalid packet size!")
        pkttype, seq, src, N, dests = 0, 0, 0, 0, []

    return pkttype, seq, src, N, dests


def create_centroid_reply_packet(src: int, dst:int) -> bytes:
    # Create packet for centroid reply
    # src (1), dst(1)
    packet: bytes = struct.pack('BB', src, dst)
    return packet

def decode_centroid_reply_packet(packet: bytes) -> Tuple[int,int]:
    # Decode centroid reply packet
    # src (1), dst(1)
    src, dst = struct.unpack('BB', packet)
    return src, dst


def create_data_multicast_packet(pkttype: int, seq: int, src: int, K: int, *dests: int, data: str = '') -> bytes:
    # Create packet for multicast data
    # Type (1), seq (1), src (1), K (1), dests (1 each), data (1000)

    N = len(dests)
    Len = len(data)

    if N == 1:
        packet: bytes = struct.pack(
            'BBBBBBB', pkttype, seq, src, N, K, Len, dests[0])
    elif N == 2:
        packet: bytes = struct.pack(
            'BBBBBBBB', pkttype, seq, src, N, K, Len, dests[0], dests[1])
    elif N == 3:
        packet: bytes = struct.pack(
            'BBBBBBBBB', pkttype, seq, src, N, K, Len, dests[0], dests[1], dests[2])
    else:
        print("Invalid number!")
        packet = struct.pack('BBBBB', pkttype, seq, src, N, K)

    return packet + bytes(data, 'utf-8')


def create_data_packet(pkttype: int, seq: int, src: int,  dst: int, data: str = '') -> bytes:
    # Create packet for unicast data
    # Type (1), seq (1), src (1), dst (1), data (1000)

    packet = struct.pack('BBBBB', pkttype, seq, src, dst, len(
        data)) + bytes(data, 'utf-8')  # Data length is missing in the PDF page 8

    return packet


def decode_data_packet(packet: bytes) -> Tuple[int, int, int, int, str]:
    # Decode unicast data packet
    # Type (1), seq (1), src (1), dst (1), data (1000)

    pkttype, seq, src, dst, data_len = struct.unpack('BBBBB', packet[:5])
    data = packet[5:].decode('utf-8')

    return pkttype, seq, src, dst, data

def create_data_multicast_ack(pkttype: int, seq: int, src: int, dst: int) -> bytes:
    # Create packet for multicast acknowledgement
    # Type (1), seq (1), src (1), dst (1)

    packet: bytes = struct.pack('BBBB', pkttype, seq, src, dst)
    return packet


def create_data_unicast_ack(pkttype: int, seq: int, src: int, dst: int, dstCen: int) -> bytes:
    # Create packet for unicast acknowledgement
    # Type (1), seq (1), src (1), dst (1), dstCen (1)

    packet: bytes = struct.pack('BBBBB', pkttype, seq, src, dst, dstCen)
    return packet
