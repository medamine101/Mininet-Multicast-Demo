# /usr/bin/python
# Comnetsii APIs for Packet. Rutgers ECE423/544
# Original Author: Sumit Maheshwari
import struct
from typing import List, Tuple

##################################
#  Different Packet Types Below ##
##################################

# Create packet for HELLO
def create_HELLO_packet(seq: int, ttl: int, src_id: int, src_ip: str, pkttype: int = 0) -> bytes:
    # Type (1), seq (1), TTL (1), src_id (1)
    packet: bytes = struct.pack(
        'BBBB', pkttype, seq, ttl, src_id) + src_ip.encode('utf-8')
    return packet

# Decode HELLO packet
def decode_HELLO_packet(packet: bytes) -> Tuple[int, int, int, int, str]:
    # Type (1), seq (1), TTL (1), src_id (1)
    pkttype, seq, ttl, src_id = struct.unpack('BBBB', packet[:4])
    ip = packet[4:].decode('utf-8')
    return pkttype, seq, ttl, src_id, ip

# Create packet for centroid request
def create_centroid_request_packet(seq: int, src: int, *dests: int) -> bytes:
    # Type (1), seq (1), src (1), N (1), dests (1)
    N = len(dests)
    pkttype = 1  # Centroid request

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

# Decode centroid request packet
def decode_centroid_request_packet(packet: bytes) -> Tuple[int, int, int, int, List[int]]:
    packet_size = len(packet)
    if packet_size == 5:
        pkttype, seq, src, N, dest = struct.unpack('BBBBB', packet)
        dests = [dest]
    elif packet_size == 6:
        pkttype, seq, src, N, dest1, dest2 = struct.unpack('BBBBBB', packet)
        dests = [dest1, dest2]
    elif packet_size == 7:
        pkttype, seq, src, N, dest1, dest2, dest3 = struct.unpack(
            'BBBBBBB', packet)
        dests = [dest1, dest2, dest3]
    else:
        print("Invalid packet size!")
        pkttype, seq, src, N, dests = 0, 0, 0, 0, []

    return pkttype, seq, src, N, dests

# Create packet for centroid reply
def create_centroid_reply_packet(src: int, dst: int) -> bytes:
    # src (1), dst(1)
    packet: bytes = struct.pack('BB', src, dst)
    return packet

# Decode centroid reply packet
def decode_centroid_reply_packet(packet: bytes) -> Tuple[int, int]:
    # src (1), dst(1)
    src, dst = struct.unpack('BB', packet)
    return src, dst

# Create packet for multicast data
def create_data_multicast_packet(pkttype: int, seq: int, src: int, K: int, *dests: int, data: str = '') -> bytes:
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

# Create packet for unicast data
def create_data_packet(pkttype: int, seq: int, src: int,  dst: int, data: str = '') -> bytes:
    # Type (1), seq (1), src (1), dst (1), data (1000)
    packet = struct.pack('BBBBB', pkttype, seq, src, dst, len(
        data)) + bytes(data, 'utf-8')  # Data length is missing in the PDF page 8
    return packet

# Decode unicast data packet
def decode_data_packet(packet: bytes) -> Tuple[int, int, int, int, str]:
    # Type (1), seq (1), src (1), dst (1), data (1000)
    pkttype, seq, src, dst, data_len = struct.unpack('BBBBB', packet[:5])
    data = packet[5:].decode('utf-8')
    return pkttype, seq, src, dst, data

# Create packet for multicast acknowledgement
def create_data_multicast_ack(pkttype: int, seq: int, src: int, dst: int) -> bytes:
    # Type (1), seq (1), src (1), dst (1)
    packet: bytes = struct.pack('BBBB', pkttype, seq, src, dst)
    return packet

# Create packet for unicast acknowledgement
def create_data_unicast_ack(pkttype: int, seq: int, src: int, dst: int, dstCen: int) -> bytes:
    # Type (1), seq (1), src (1), dst (1), dstCen (1)
    packet: bytes = struct.pack('BBBBB', pkttype, seq, src, dst, dstCen)
    return packet
