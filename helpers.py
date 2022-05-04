from ipaddress import ip_address
from time import sleep
from typing import Dict, List, Union, Tuple
from threading import Thread

# BROADCAST_ADDRESS = '10.255.255.255'# Address to broadcast to all ips
BROADCAST_ADDRESS = '10.0.255.255'# Address to broadcast to all ips
BROADCAST_PORT = 8080 # Used for HELLO packets

DEFAULT_TTL = 50 # Default TTL for packets

UNICAST_PORT = 8000 # Port used for unicast packets
MULTICAST_PORT = 8888 # Port used for multicast packets

class table_entry():
    ip_address: str
    ttl: int
    seq: int 
    dist: int

    def __init__(self, ip_address: str, seq: int, dist: int, ttl: int = 10):
        self.ip_address = ip_address
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
        thread = Thread(target=self.run_table)
        thread.start()


    def add_entry(self, id: int, ip: str, seq: int, dist: int):
        self.__table__[id] = table_entry(ip, seq, dist)
    
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
    
    def get_id(self, ip: int) -> Union[int, None]:
        for k, v in self.__table__.items():
            if v == ip:
                return k
        return None

    def get_size(self) -> int:
        return len(self.__table__)

    def run_table(self):

        print("Running table")

        while True:

            sleep(1)

            # Decrement ttl for all entries, remove if ttl == 0
            keys_to_delete = []
            for k, v in self.__table__.items():
                v.decrement_ttl() # Decrement ttl
                if v.ttl <= 0: # Set entry to be removed if ttl == 0
                    keys_to_delete.append(k)
            for k in keys_to_delete: # Remove entries
                self.remove_entry(k)
            
            
            

    
