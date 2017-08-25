import ast
import random
import socket
import sys
import traceback

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = '0.0.0.0'
server_port = int(input("Type the port number you desire for this socket: "))
reliability = float(input("Type the fraction of datagrams that should be dropped: "))
corruption_rate = float(input("Type the fraction of datagrams that should be corrupted: "))

client = (server_address, server_port)
sock.bind(client)
print("This socket identified by: " + server_address + ":" + str(server_port))

while True:
    payload, client_address = sock.recvfrom(1024)
    print("\n===New Packet===")
    if random.random() < reliability:
        print("  Dropped packet: {}".format(payload))
        continue

    try:
        data, forwarding_address = ast.literal_eval(payload.decode('utf-8'))
        print("  Received payload: ", str(payload))
        print("  Forwarding data to " + str(forwarding_address))

        if random.random() < corruption_rate:
            corruption_index = random.randint(0, len(data) - 1)
            corruption_bit_index = random.randint(0, len(data[corruption_index]) - 1)
            new_character = chr(ord(data[corruption_index]) ^ (1 << corruption_bit_index))
            corrupted_data = data[:corruption_index] + new_character + data[corruption_index+1:]
            print("  Corruption event: {} became {}".format(data, corrupted_data))
            data = corrupted_data

        data = (data, client_address)
        sent = sock.sendto(bytes(str(data), 'utf-8'), forwarding_address)
    except:
        print("  Failed to handle: {}".format(payload))
        traceback.print_exc()
