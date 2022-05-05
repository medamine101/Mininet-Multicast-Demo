from ipaddress import ip_address
from time import sleep
from typing import Dict, List, Union, Tuple
from threading import Thread

DEFAULT_TTL = 50  # Default TTL for packets

DISCOVERY_PORT = 8080  # Used for HELLO packets
DATA_PORT = 8000  # Port used for data packets
CENTROID_SETUP_PORT = 8888  # Port used for setting up multicast packets

class centroid():
    is_centroid: bool
    dests: List[int]

    def __init__(self):
        self.is_centroid = False
        self.dests = []

    def set_centroid(self, dests: List[int]):
        self.is_centroid = True
        self.dests = dests
    
    def remove_centroid(self):
        self.is_centroid = False
        self.dests = []
    
    def get_dests(self):
        return self.dests


class table_entry():
    ip_address: str
    next_hop: str
    ttl: int
    seq: int
    dist: int

    def __init__(self, ip_address: str, next_hop: str, seq: int, dist: int, ttl: int = 10):
        self.ip_address = ip_address
        self.next_hop = next_hop
        self.ttl = ttl
        self.seq = seq
        self.dist = dist

    def set_ttl(self, ttl: int):
        self.ttl = ttl

    def decrement_ttl(self):
        self.ttl -= 1


class routing_table():

    __table__: Dict[int, table_entry]

    def __init__(self):
        self.__table__ = {}

        # Run thread for updating table
        Thread(target=self.run_table).start()

    def add_entry(self, id: int, ip: str, next_hop: str, seq: int, dist: int):

        if id in self.__table__:
            self.__table__[id].set_ttl(DEFAULT_TTL)

        self.__table__[id] = table_entry(
            ip_address=ip, next_hop=next_hop, seq=seq, dist=dist)

    def remove_entry(self, id: int):
        del self.__table__[id]

    def check_entry(self, id: int) -> bool:
        if id in self.__table__:
            return True
        return False

    def get_ip(self, id: int) -> str:
        if id in self.__table__:
            return self.__table__[id].ip_address
        return ''

    def get_seq(self, id: int) -> int:
        if id in self.__table__:
            return self.__table__[id].seq
        return -1

    def get_dist(self, id: int) -> int:
        if id in self.__table__:
            return self.__table__[id].dist
        return -1

    def get_next_hop(self, id: int) -> str:
        if id in self.__table__:
            return self.__table__[id].next_hop
        return ''

    def get_size(self) -> int:
        return len(self.__table__)

    def __str__(self):
        string = 'Routing Table:\n'
        string += '-----------------------------------\n'
        for id, entry in self.__table__.items():
            string += f'SRC: {id}\tIP: {entry.ip_address}\tSeq: {entry.seq}\tDist: {entry.dist}\n'
        return string

    def run_table(self):

        print("Running table")

        while True:

            sleep(1)

            # Decrement ttl for all entries, remove if ttl == 0
            keys_to_delete = []
            for k, v in self.__table__.items():
                v.decrement_ttl()  # Decrement ttl
                if v.ttl <= 0:  # Set entry to be removed if ttl == 0
                    keys_to_delete.append(k)
            for k in keys_to_delete:  # Remove entries
                self.remove_entry(k)
