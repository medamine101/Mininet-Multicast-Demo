from typing import Dict, List, Union, Tuple

BROADCAST_ADDRESS = '10.255.255.255'# Address to broadcast to all ips

BROADCAST_PORT = 8080 # Used for HELLO packets

DEFAULT_PORT = 8000



class routing_table():
    
    __table__: Dict[str, str]

    def __init__(self):
        self.__table__ = {}

    def add_entry(self, id: str, ip: str):
        self.__table__[id] = ip
    
    def remove_entry(self, id: str):
        del self.__table__[id]

    def get_ip(self, id: str) -> str:
        return self.__table__[id]
    
    def get_id(self, ip: str) -> Union[str, None]:
        for k, v in self.__table__.items():
            if v == ip:
                return k
        return None

    def get_size(self) -> int:
        return len(self.__table__)
