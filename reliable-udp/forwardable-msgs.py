import socket
import udil


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client_address = '0.0.0.0'


server_port = int(input('Type the port number you wish to send to: '))
forward_port = int(input('Enter the port to be forwarded to: '))

while True:
    message = input('Enter a string to be echoed: ')
    complete_message = (message, ('0.0.0.0', forward_port))
    udil.reliable_send(message, ('0.0.0.0', 9005), ('0.0.0.0', server_port),
                       ('0.0.0.0', forward_port))
    #sock.sendto(bytes(str(complete_message), "utf-8"), (server_ip, server_port))
    #print("sent: " + str(complete_message))
