#!/usr/bin/env python3
import ipaddress as ipaddr
import os
from pysnmp.hlapi import *

# Globals
RADIUS_SERVER = {}
HHME_SERVER_SWITCH = 0
PEER_IP_KEY = "peer"

# MY logging
DEBUG_LOGGER = "my_debug_log"
EVENT_LOGGER = "my_event_log"
ALARM_LOGGER = "my_alarm_log"

# MY config
CONFIG_FILE_PATH = '/opt/my-client/conf/radius.conf'

CONFIG_VAL_TYPE_STR = "string"
CONFIG_VAL_TYPE_BOOL = "bool"

# MY config section
SECTION_RAD_SERVER = "radius"
SECRET_KEY = "secret"
HHMEA_IP_KEY = "hhmeaip"
HHMEB_IP_KEY = "hhmebip"
ACTIVE_HHME_IP_KEY = "active_hhme"
NSAPI_KEY = "nsapi"
RETRANS_CNT_KEY = "retrans_count"
TIMEOUT_KEY = "timeout_interval_in_sec"
APN_KEY = "apn"
NAS_IP_KEY = "nas_ip"
NAS_ID_KEY = "nas_id"
EVENT_LOG_KEY = "event_debug"
RADIUS_DELAY_KEY = "rad_delay"

# SNMP TRAP
ENTERPRISE = "1.3.6.1.4.1.6276.1.0.35033"
VAR_BINDING = "1 6 0 .1.3.6.1.4.1.6276.1.0.35033 s"

# Constant values
CHAR_COMMA = ','
KEY_IDX = 0
VALUE_IDX = 1
CLASS_ATTR_DELIM = ":"
REPLY_MSG_DELIM = "-"
CLASS_ATTR_VAL_DELIM = "="
CHAR_SINGLE_QUOTE = "\'"


# User defined methods
def get_ip_from_subnet(subnet):
    """ (str) -> list
    
    Returns a list of IP addresses which belongs to a subnet.
    
    """
    ipv4 = []

    net = ipaddr.ip_network(subnet)

    for x in net.hosts():
        ipv4.append(str(x))

    return ipv4
	
	
def send_snmp_trap(msg):
    """ 
	
    """
    next(
        sendNotification(
            SnmpEngine(),
            CommunityData('public', mpModel=0),
            UdpTransportTarget(('192.168.6.199', 162)),
            ContextData(),
            'trap',
            NotificationType(
                ObjectIdentity('1.3.6.1.4.1.6276.1.0.35033')
            ).addVarBinds(
                ('1.3.6.1.6.3.18.1.3.0', '192.168.6.183'),
                ('1.3.6.1.4.1.6276.1.0.35033', OctetString(msg))
            )
        )
    ) 

    
	
# main
if __name__ == "__main__":
    pass
