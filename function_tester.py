import socket as Socket

socket = Socket.socket(Socket.AF_INET, Socket.SOCK_DGRAM)
socket.bind(('0.0.0.0', 8080))

while True:
    data, addr = socket.recvfrom(1024)
    print(data)
    socket.sendto(data, addr)