from socket import SO_REUSEPORT, SOL_SOCKET, socket, AF_INET, SOCK_DGRAM, SO_BROADCAST
from helpers import *
from packet import *
from threading import Thread
from router import udprouter
import netifaces as ni
from sys import argv

# Class inherits methods from udprouter


class udphost(udprouter):

    # Super init is not called as not all udprouter threads are needed
    def __init__(self, id: int, ip: str):
        """
        Constructor for udphost class
        """
        self.id = id
        self.ip = ip
        self.rt = routing_table()
        self.seq = 0

        # Start thread for broadcasting HELLO packets
        Thread(
            target=self.broadcast_hello_packet, args=(self.id, DEFAULT_TTL)).start()

        # Start thread for handling and forwarding HELLO packets
        Thread(target=self.handle_hello_packet).start()

        sleep(5)
        # Start thread for handling multicast data sending and receiving
        Thread(target=self.handle_centroid_packets).start()

    # Method to handle sending and receiving of multicast data
    def handle_centroid_packets(self):
        """
        Method to handle receiving and forwarding of centroid request/reply packets
        """

        # Loop to allow user to keep sending and receiving data
        while True:

            # Ask if user wants to send or receive from this host
            print("Would you like to send or receive data? (s/r)")
            choice = input()

            # If user wants to send
            if (choice == 's'):

                # Ask user for destination host(s)
                hosts = input("To what hosts would you like to send to?")

                # Split input into list of hosts
                hosts = hosts.split(",")
                inthosts = []
                for i in range(0, len(hosts)):
                    inthosts.append(int(hosts[i]))

                # If host is not in routing table, go back to start of loop
                for dst in inthosts:
                    if not self.rt.check_entry(dst):
                        print("Host not in routing table")
                        continue

                # If only one host, send to that host as unicast
                if len(inthosts) == 1:

                    # Set up socket
                    data_sock = socket(AF_INET, SOCK_DGRAM)
                    data_sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)

                    # Loop to send data
                    while True:

                        # Ask user for data to send
                        input_msg = input(
                            "Enter message to send to destinations: \n")

                        # IDK if this is used
                        print("Enter 'stop' to stop sending reset")

                        # Create packet
                        data_packet = create_data_packet(
                            pkttype=1, seq=self.seq, src=self.id, dst=inthosts[0], data=input_msg)

                        # Print where the packet is being sent to
                        print("Sending data packet to ",
                              self.rt.get_next_hop(inthosts[0]))

                        # Send packet
                        data_sock.sendto(
                            data_packet, (self.rt.get_next_hop(inthosts[0]), DATA_PORT))

                        # If the user wants to stop sending, break out of loop
                        if input_msg == "end_of_transmission":
                            data_packet = create_data_packet(
                                pkttype=2, seq=self.seq, src=self.id, dst=inthosts[0], data="end_of_transmission")
                            data_sock.sendto(
                                data_packet, (self.rt.get_next_hop(inthosts[0]), DATA_PORT))
                            break

                    # Close socket
                    data_sock.close()

                elif len(inthosts) >= 2:  # If multiple hosts, send to all as multicast

                    # Create packet to fit the number of destinations
                    if (len(inthosts) == 2):
                        centroid_request_packet = create_centroid_request_packet(
                            self.seq, self.id, inthosts[0], inthosts[1])
                    else:
                        centroid_request_packet = create_centroid_request_packet(
                            self.seq, self.id, inthosts[0], inthosts[1], inthosts[2])

                    # Set up socket, send, and close socket for each broadcast address
                    for addr in self.broadcast_addresses:
                        sock = socket(AF_INET, SOCK_DGRAM)
                        sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
                        sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
                        sock.bind((addr, CENTROID_SETUP_PORT))
                        print(addr)
                        sock.sendto(centroid_request_packet,
                                    (addr, CENTROID_SETUP_PORT))
                        sock.close()

                    # wait for centroid reply
                    centsock = socket(AF_INET, SOCK_DGRAM)
                    centsock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
                    centsock.bind(('0.0.0.0', CENTROID_SETUP_PORT))
                    packet, addr = centsock.recvfrom(10)

                    # decode data packet
                    centroid, dst = decode_centroid_reply_packet(packet)

                    # send data packet to centroid
                    data_sock = socket(AF_INET, SOCK_DGRAM)
                    data_sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
                    while True:
                        input_msg = input(
                            "Enter message to send to destinations: ")
                        data_packet = create_data_packet(
                            pkttype=1, seq=self.seq, src=self.id, dst=centroid, data=input_msg)

                        print("Sending data packet to ",
                              self.rt.get_next_hop(centroid))
                        # data_sock.bind((self.rt.get_next_hop(centroid), DATA_PORT))
                        data_sock.sendto(
                            data_packet, (self.rt.get_next_hop(centroid), DATA_PORT))
                        print('Sent data packet to centroid', data_packet)
                        if input_msg == 'end_of_transmission':
                            break
                    data_sock.close()

            elif choice == 'r':  # If user wants to receive

                # Set up socket
                sock = socket(AF_INET, SOCK_DGRAM)
                sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
                sock.bind(('0.0.0.0', DATA_PORT))

                # Loop to receive data
                while True:
                    data_packet, addr = sock.recvfrom(1024)
                    pkttype, seq, src, dst, data = decode_data_packet(
                        data_packet)
                    print('Received data packet from ' +
                          str(src) + ' to ' + str(dst))
                    if data != 'end_of_transmission':
                        print('Data packet data: ' + data)
                    else:  # If data is end of transmission, break out of loop
                        print('End of transmission')
                        break
            else:
                print("Invalid input")


if __name__ == '__main__':
    print("Router Started...")

    # Print all interfaces
    print(ni.interfaces())

    # Get the ip address to be used on print displays to the user
    device_ip: str = ''
    for ifstring in ni.interfaces():
        if 'eth' in ifstring:
            device_ip = ni.ifaddresses(ifstring)[ni.AF_INET][0]['addr']
            break

    # Take device ID as command line argument, must be between 1 and 254
    device_id = 0
    if (len(argv) > 1 and argv[1].isdigit() and int(argv[1]) >= 1 and int(argv[1]) <= 254):
        device_id = int(argv[1])
    else:
        print("Invalid device ID. Must be an integer between 1 and 254")
        exit(1)

    # Print the device IP and ID to the user
    print("Device IP: ", device_ip)
    print("Device ID: ", device_id)

    # Create and run router object
    udp_host = udphost(id=(device_id), ip=device_ip)
