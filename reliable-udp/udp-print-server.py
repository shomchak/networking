import ast
import socket
import sys

server_port = int(sys.argv[1])
in_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
out_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = '0.0.0.0'

server = (server_address, server_port)
in_sock.bind(server)
print("Listening on " + server_address + ":" + str(server_port))

while True:
    payload, client_address = in_sock.recvfrom(1024)
    data, return_address = ast.literal_eval(payload.decode('utf-8'))
    print(client_address, return_address)
    print("received payload: ", str(payload))
    complete_message = (data, return_address)
    out_sock.sendto(bytes(str(complete_message), 'utf-8'), client_address)

