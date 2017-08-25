import ast
import socket
import time


def reliable_send(data, from_addr, via, address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(from_addr)
    sock.settimeout(1)
    complete_data = str((data, address))
    while True:
        print('Sending {}'.format(complete_data))
        sock.sendto(
            bytes(complete_data, 'utf-8'),
            via)
        try:
            ack = sock.recv(1024)
        except socket.timeout:
            print('Timed out. Retrying in 100ms...')
            time.sleep(0.1)
            continue
        print('Got an ACK')
        print(ack)
        print(complete_data)
        break

