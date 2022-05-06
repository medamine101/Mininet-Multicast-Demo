from ipaddress import ip_address
from time import sleep
from typing import Dict, List, Union, Tuple
from threading import Thread

DEFAULT_TTL = 50  # Default TTL for packets

DISCOVERY_PORT = 8080  # Used for HELLO packets
DATA_PORT = 8000  # Port used for data packets
CENTROID_SETUP_PORT = 8888  # Port used for setting up multicast packets

# Class to house information for a centroid


class centroid():
    is_centroid: bool
    dests: List[int]

    def __init__(self):
        """
        Constructor for centroid class
        """
        self.is_centroid = False
        self.dests = []

    def set_centroid(self, dests: List[int]):
        """
        Sets centroid to true and sets destinations
        """
        self.is_centroid = True
        self.dests = dests

    def remove_centroid(self):
        """
        Resets centroid to false
        """
        self.is_centroid = False
        self.dests = []

    def get_dests(self):
        """
        Returns destinations
        """
        return self.dests

# Class for routing table entry


class table_entry():
    ip_address: str
    next_hop: str
    ttl: int
    seq: int
    dist: int

    # Initialize table entry, TTL is 10 by default
    def __init__(self, ip_address: str, next_hop: str, seq: int, dist: int, ttl: int = 10):
        """
        Constructor for table_entry class
        """
        self.ip_address = ip_address
        self.next_hop = next_hop
        self.ttl = ttl
        self.seq = seq
        self.dist = dist

    # Set TTL for table entry
    def set_ttl(self, ttl: int):
        """
        Sets TTL for table entry
        """
        self.ttl = ttl

    # decrement TTL for table entry by 1
    def decrement_ttl(self):
        """
        Decrements TTL for table entry by 1
        """
        self.ttl -= 1

# Routing table class


class routing_table():

    __table__: Dict[int, table_entry]

    # Initialize routing table, creates thread to run table operations
    def __init__(self):
        """
        Constructor for routing_table class
        """
        self.__table__ = {}

        # Run thread for updating table
        Thread(target=self.run_table).start()

    # Add entry to routing table
    def add_entry(self, id: int, ip: str, next_hop: str, seq: int, dist: int):
        """
        Adds entry to routing table
        """

        if id in self.__table__:
            self.__table__[id].set_ttl(DEFAULT_TTL)

        self.__table__[id] = table_entry(
            ip_address=ip, next_hop=next_hop, seq=seq, dist=dist)

    # Remove entry from routing table
    def remove_entry(self, id: int):
        """
        Removes entry from routing table
        """
        del self.__table__[id]

    # Check if id is in routing table
    def check_entry(self, id: int) -> bool:
        """
        Checks if id is in routing table
        """
        if id in self.__table__:
            return True
        return False

    # Get ip for id in routing table
    def get_ip(self, id: int) -> str:
        """
        Gets ip for id in routing table
        """
        if id in self.__table__:
            return self.__table__[id].ip_address
        return ''

    # Get sequence number for id in routing table
    def get_seq(self, id: int) -> int:
        """
        Gets sequence number for id in routing table
        """
        if id in self.__table__:
            return self.__table__[id].seq
        return -1

    # Get distance for id in routing table
    def get_dist(self, id: int) -> int:
        """
        Gets distance for id in routing table
        """
        if id in self.__table__:
            return self.__table__[id].dist
        return -1

    # Get next hop for id in routing table
    def get_next_hop(self, id: int) -> str:
        """
        Gets next hop for id in routing table
        """
        if id in self.__table__:
            return self.__table__[id].next_hop
        return ''

    # Get size of routing table
    def get_size(self) -> int:
        """
        Gets size of routing table
        """
        return len(self.__table__)

    # Method to print routing table, called automatically by print fuctions
    def __str__(self):
        """
        Prints routing table
        """
        string = 'Routing Table:\n'
        string += '-----------------------------------\n'
        for id, entry in self.__table__.items():
            string += f'SRC: {id}\tIP: {entry.ip_address}\tSeq: {entry.seq}\tDist: {entry.dist}\n'
        return string

    # Method to run table operations
    def run_table(self):
        """
        Runs table operations
        """

        print("Running table")

        # Loop forever
        while True:

            # Wait 1 second
            sleep(1)

            # Decrement ttl for all entries, remove if ttl == 0
            keys_to_delete = []
            for k, v in self.__table__.items():
                v.decrement_ttl()  # Decrement ttl
                if v.ttl <= 0:  # Set entry to be removed if ttl == 0
                    keys_to_delete.append(k)
            for k in keys_to_delete:  # Remove entries
                self.remove_entry(k)
