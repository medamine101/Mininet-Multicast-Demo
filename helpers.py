from ipaddress import ip_address
from time import sleep
from typing import Dict, List, Union, Tuple
from threading import Thread

BROADCAST_ADDRESS = '10.255.255.255'# Address to broadcast to all ips

BROADCAST_PORT = 8080 # Used for HELLO packets

DEFAULT_PORT = 8000

class table_entry():
    ip_address: str
    TTL: int

    def __init__(self, ip_address: str, TTL: int = 10):
        self.ip_address = ip_address
        self.TTL = TTL
    
    def set_TTL(self, TTL: int):
        self.TTL = TTL

    def decrement_TTL(self):
        self.TTL -= 1

class routing_table():
    
    __table__: Dict[int, table_entry]

    def __init__(self):
        self.__table__ = {}

        # Run thread for updating table
        thread = Thread(target=self.run_table)
        thread.start()


    def add_entry(self, id: int, ip: str):
        if id in self.__table__:
            self.__table__[id].set_TTL(10)
        else:
            self.__table__[id] = table_entry(ip)
    
    def remove_entry(self, id: int):
        del self.__table__[id]

    def get_ip(self, id: int) -> str:
        return self.__table__[id].ip_address
    
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

            # Decrement TTL for all entries, remove if TTL == 0
            keys_to_delete = []
            for k, v in self.__table__.items():
                v.decrement_TTL() # Decrement TTL
                if v.TTL <= 0: # Set entry to be removed if TTL == 0
                    keys_to_delete.append(k)
            for k in keys_to_delete: # Remove entries
                self.remove_entry(k)
            
            
            

    
