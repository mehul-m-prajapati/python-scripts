#!/usr/bin/evn python3
from scapy.all import *

send(IP(dst="192.168.6.139")/UDP()/DNS(rd=1,qd=DNSQR(qname="www.oreilly.com")), count=50 )
send(IP(dst="192.168.6.139")/ICMP(), count=50 )

send(IP(dst="192.168.6.111")/UDP()/DNS(rd=1,qd=DNSQR(qname="www.oreilly.com")), count=50 )
send(IP(dst="192.168.6.111")/ICMP(), count=50 )
