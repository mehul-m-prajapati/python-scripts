#!/usr/bin/evn python3
from scapy.all import *

# DNS query
send(IP(dst="192.168.6.139")/UDP()/DNS(rd=1,qd=DNSQR(qname="www.oreilly.com")), count=50 )
send(IP(dst="192.168.6.139")/ICMP(), count=50 )
send(IP(dst="192.168.6.111")/UDP()/DNS(rd=1,qd=DNSQR(qname="www.oreilly.com")), count=50 )

#ICMP echo packet
send(IP(dst="192.168.6.111")/ICMP(), count=50 )

# NTP packets
send(IP(dst="192.168.6.199")/UDP()/NTP(), count=10 )
