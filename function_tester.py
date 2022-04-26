from packet import *


packet = create_data_multicast_packet(1, 1, 1, 2, 2, data ="Hello World")

print(packet)