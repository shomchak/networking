#!/usr/bin/env python3

import socket
import struct
import sys
import time


def make_icmp_packet(type, code):
    without_checksum = struct.pack('>BBHI', type, code, 0, 0)
    checksum = compute_checksum(without_checksum)
    with_checksum = struct.pack('>BBHI', type, code, checksum, 0)
    return with_checksum


def compute_checksum(without_checksum):
    checksum = 0
    for chunk in struct.unpack('>HHHH', without_checksum):
        checksum += chunk
        checksum = (checksum & 0xFFFF) + (checksum >> 16)
    checksum = checksum ^ 0xFFFF
    return checksum


def is_icmp_response(outp):
    if not outp[0] & 15 == 5:
        print('IP header wrong length.')
    elif outp[9] != 1:
        print('Not an ICMP message.')
    else:
        return True
    return False


def done(outp):
    if outp[20:22] == b'\x0b\x00':
        if outp[48:50] != b'\x08\x00':
            print('Not a response for our packet.')
            return True
        return False
    elif outp[20:22] == b'\x00\x00':
        return True
    else:
        print('Unrecognized ICMP type.')
        return True


def main():
    ip = sys.argv[1]
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    ttl = 1
    inp = make_icmp_packet(8, 0)
    while True:
        sock.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        sock.sendto(inp, (ip, 0))
        outp, addr = sock.recvfrom(1024)
        if is_icmp_response(outp):
            print(ttl, addr[0])
            if done(outp):
                return
            ttl += 1
        else:
            return


if __name__ == '__main__':
    main()
