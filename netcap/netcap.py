import sys
import struct


def main():
    with open(sys.argv[1], 'rb') as f:
        all_bytes = bytes(f.read())
        no_pcap_header = strip_pcap_header(all_bytes)
        pcap_packets = split_pcap_packets(no_pcap_header)
        ip_packets = []
        for p in pcap_packets:
            ip_packet = maybe_ip_packet(p)
            if ip_packet is not None:
                ip_packets.append(ip_packet)
        ip_payloads = []
        for p in ip_packets:
            ip_payload = is_for_our_ip(p, sys.argv[2])
            if ip_payload is not None:
                ip_payloads.append(ip_payload)
        parse_tcp_segments(ip_payloads)


def strip_pcap_header(bs):
    return bytes(bs[24:])


def split_pcap_packets(bs):
    packets = []
    while len(bs) > 0:
        size = struct.unpack('<I', bs[12:16])[0]
        packet = bytes(bs[16:16 + size])
        packets.append(packet)
        bs = bytes(bs[16 + size:])
    return packets


def maybe_ip_packet(packet):
    ip_packet = None
    if not packet[12:14] == bytes('\x08\x00'):
        print 'Not an IPv4 packet!'
    else:
        ip_packet = bytes(packet[14:])
    return ip_packet


def is_for_our_ip(packet, our_ip):
    header_length = ord(packet[0]) & 7
    (length, protocol) = struct.unpack('>xxHxxxxxBxxxxxx', packet[:16])
    s1,s2,s3,s4, d1,d2,d3,d4 = struct.unpack('>BBBBBBBB', packet[12:20])
    sip = '{}.{}.{}.{}'.format(s1,s2,s3,s4)
    dip = '{}.{}.{}.{}'.format(d1,d2,d3,d4)
    if sip == our_ip:
        arrow = '-->'
    elif dip == our_ip:
        arrow = '<--'
    else:
        return None
    print arrow, sip, dip
    return (arrow, bytes(packet[header_length * 4: length]))


def parse_tcp_segments(segments):
    received = [s for (a, s) in segments if a == '<--']
    ordered = []
    for segment in received:
        segment = segment
        sp, dp, sn, an = struct.unpack('>HHII', segment[:12])
        dob, cbs = segment[12], segment[13]
        do = (ord(dob) & 240) >> 4
        ack = (ord(cbs) & 16) >> 4
        psh = (ord(cbs) & 8) >> 3
        rst = (ord(cbs) & 4) >> 2
        syn = (ord(cbs) & 2) >> 1
        fin = (ord(cbs) & 1)
        data = segment[do * 4:]
        ordered.append((sn, syn, ack, data))
        print 'SYN {} ACK {} PSH {}'.format(syn, ack, psh)
    ordered.sort(key=lambda t: t[0])

    http = bytes()
    for sn, syn, ack, data in ordered:
        if syn == 1 and ack == 1:
            old_seq = sn + 1
            old_length = 0
        if syn == 0 and ack == 1:
            if sn == old_seq + old_length:
                http = http + bytes(data)
                old_seq = sn
                old_length = len(data)

    split_at = http.find('\r\n\r\n') + 4
    jpg = bytes(http[split_at:])

    with open('out.jpg', 'wb') as of:
        of.write(jpg)


main()

