#!/usr/bin/env python3
import os
import sys
import time
import logging
import ipaddress as ipaddr
from netaddr import *
import random as ran
from pyrad.client import Client
from pyrad.dictionary import Dictionary
import pyrad.packet
from helpers import *
import helpers as hl

# Globals
debuglogger = logging.getLogger(DEBUG_LOGGER)
eventlogger = logging.getLogger(EVENT_LOGGER)
alarmlogger = logging.getLogger(ALARM_LOGGER)

DICT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dictionary")
SERVICE_TYPE = 0x999
NAS_ID = "BRCNGG01"
IMSI_NA = " Not Available "
PROXY_STATE_MAX = 9999

CALL_STATE_ALREADY_EXIST = '40685'
CALL_STATE_CREATED = '40676'

RADIUS_ATTR_ACCT_TERM_CAUSE_USER_REQ = 1
MY_MEM_DB = {}

RADIUS_ATTR_PASSWORD = "User-Password"
RADIUS_ATTR_FRAMED_IP = "Framed-IP-Address"
RADIUS_ATTR_FRAMED_NETMASK = "Framed-IP-Netmask"
RADIUS_ATTR_NAS_IP = "NAS-IP-Address"
RADIUS_ATTR_NAS_ID = "NAS-Identifier"
RADIUS_ATTR_APN = "Called-Station-Id"
RADIUS_ATTR_NSAPI = "3GPP-NSAPI"
RADIUS_ATTR_IMSI = "3GPP-IMSI"
RADIUS_ATTR_SERVICE_TYPE = "Service-Type"
RADIUS_ATTR_ACCT_SESS_ID = "Acct-Session-Id"
RADIUS_ATTR_CALLBACK_NUM = "Callback-Number"
RADIUS_ATTR_PROXY_STATE = "Proxy-State"
RADIUS_ATTR_ACCT_STS = "Acct-Status-Type"
RADIUS_ATTR_REPLY_MSG = "Reply-Message"
RADIUS_ATTR_CLASS = "Class"
RADIUS_ATTR_CLASS_HCR = "HCR"
RADIUS_ATTR_CLASS_MY_ID = "MYTerminalId"
RADIUS_ACCT_STS_STOP = "Stop"
RADIUS_ACCT_STS_START = "Start"
RADIUS_ACCT_STS_INTERIM = "Interim-Update"
RADIUS_ATTR_INPUT_OCTET = "Acct-Input-Octets"
RADIUS_ATTR_OUTPUT_OCTET = "Acct-Output-Octets"
RADIUS_ATTR_INPUT_PKT = "Acct-Input-Packets"
RADIUS_ATTR_OUTPUT_PKT = "Acct-Output-Packets"
RADIUS_ATTR_CALLING_STATION_ID = "Calling-Station-Id"
RADIUS_ATTR_ACCT_TERM_CAUSE = "Acct-Terminate-Cause"


# User defined methods
def send_auth_pkt(route, rad_server):
    """ (str, dict) -> NoneType
    
    Prepares and sends a RADIUS authentication packet.
    
    """
    #ip_addr = get_ip_from_subnet(route)
    net = ipaddr.ip_network(route)
    ip = str(net.network_address)
	
	# Default retries = 3, timeout = 5 seconds
    srv_handle = Client(server=rad_server[ACTIVE_HHME_IP_KEY], secret=rad_server[SECRET_KEY].encode(), dict=Dictionary(DICT))

	# Set values as per config
    srv_handle.retries = int(rad_server[RETRANS_CNT_KEY])
    srv_handle.timeout = int(rad_server[TIMEOUT_KEY])
	
    # Create request for a subnet
	
     # Prepare AVPs
    req = srv_handle.CreateAuthPacket(code=pyrad.packet.AccessRequest)
    #req[RADIUS_ATTR_PASSWORD] = req.PwCrypt(rad_server[PASS_KEY])

    req[RADIUS_ATTR_SERVICE_TYPE] = SERVICE_TYPE
    req[RADIUS_ATTR_IMSI] = IMSI_NA
    req[RADIUS_ATTR_NAS_IP] = RADIUS_SERVER[NAS_IP_KEY]
    req[RADIUS_ATTR_NAS_ID] = RADIUS_SERVER[NAS_ID_KEY]
    req[RADIUS_ATTR_APN] = RADIUS_SERVER[APN_KEY]
    proxy_state = str(int(time.time())) + rad_server[NSAPI_KEY] + str(ran.randint(1000, PROXY_STATE_MAX))	# epoch (10 digits) + NSAPI (1 digit) + random number (4 digits)
    req[RADIUS_ATTR_PROXY_STATE] = proxy_state.encode()
    req[RADIUS_ATTR_FRAMED_IP] = ip
    req[RADIUS_ATTR_FRAMED_NETMASK] = str(net.netmask)
    req[RADIUS_ATTR_NSAPI] = rad_server[NSAPI_KEY]
    
    # Debug logs
    debuglogger.debug("+++++++ PREPARE RADIUS ACCESS REQUEST FOR {} +++++++\n".format(ip))
    debuglogger.debug("Sending Radius Access Request with following AVPs")
	
    for key in req.keys():
        debuglogger.debug("		{}: {}".format(key, req[key][KEY_IDX]))

    # Time Delay in msec
    rad_delay = int(RADIUS_SERVER[RADIUS_DELAY_KEY])
    if rad_delay > 0:
        time.sleep(rad_delay / 1000.0)
	
    # Send the packet
    _send_radius_access_pkt(srv_handle, req)
				
    debuglogger.debug("+++++++ PROCESSING FOR subnet {} COMPLETED +++++++\n".format(route))

	
def send_acct_stop_pkt(route, rad_server):
    """ (str, dict) -> NoneType
    
    Prepares and sends a RADIUS accounting Stop packet.
    
    """
    ip = str((ipaddr.ip_network(route)).network_address)
    srv_handle = Client(server=rad_server[ACTIVE_HHME_IP_KEY], secret=rad_server[SECRET_KEY].encode(), dict=Dictionary(DICT))

    # Send Accounting stop request for a subnet
    
	# Create Accounting packet
    req = srv_handle.CreateAcctPacket()
    
    # Debug logs
    debuglogger.debug("+++++++ PREPARE RADIUS ACCOUNTING STOP REQUEST FOR {} +++++++\n".format(ip))
    debuglogger.debug("Sending Radius Accounting Stop Request with following AVPs")
	
    # Parse AVPs from memory
    if ip in MY_MEM_DB:
	
        for item in MY_MEM_DB[ip]:
          
            if RADIUS_ATTR_SERVICE_TYPE in item:
                req[RADIUS_ATTR_SERVICE_TYPE] = item[RADIUS_ATTR_SERVICE_TYPE]
	
            if RADIUS_ATTR_APN in item:
                req[RADIUS_ATTR_APN] = item[RADIUS_ATTR_APN]
    
            if RADIUS_ATTR_CALLBACK_NUM in item:
                req[RADIUS_ATTR_CALLBACK_NUM] = item[RADIUS_ATTR_CALLBACK_NUM]
                req[RADIUS_ATTR_CALLING_STATION_ID] = item[RADIUS_ATTR_CALLBACK_NUM]
    
            if RADIUS_ATTR_ACCT_SESS_ID in item:
                req[RADIUS_ATTR_ACCT_SESS_ID] = item[RADIUS_ATTR_ACCT_SESS_ID]

            if RADIUS_ATTR_IMSI in item:
                req[RADIUS_ATTR_IMSI] = item[RADIUS_ATTR_IMSI]
	
            if RADIUS_ATTR_NSAPI in item:
                req[RADIUS_ATTR_NSAPI] = item[RADIUS_ATTR_NSAPI]
    
            if RADIUS_ATTR_CLASS in item:
                req[RADIUS_ATTR_CLASS] = item[RADIUS_ATTR_CLASS].encode()
    
            if RADIUS_ATTR_PROXY_STATE in item:
                req[RADIUS_ATTR_PROXY_STATE] = str(item[RADIUS_ATTR_PROXY_STATE]).encode()
    
	    # Prepare AVPs
        req[RADIUS_ATTR_FRAMED_IP] = ip
        net = ipaddr.ip_network(route)
        req[RADIUS_ATTR_FRAMED_NETMASK] = str(net.netmask)
        req[RADIUS_ATTR_ACCT_STS] = RADIUS_ACCT_STS_STOP
    
        req[RADIUS_ATTR_INPUT_OCTET] = 0
        req[RADIUS_ATTR_OUTPUT_OCTET] = 0
        req[RADIUS_ATTR_INPUT_PKT] = 0
        req[RADIUS_ATTR_OUTPUT_PKT] = 0
        req[RADIUS_ATTR_NAS_IP] = RADIUS_SERVER[NAS_IP_KEY]
        req[RADIUS_ATTR_NAS_ID] = RADIUS_SERVER[NAS_ID_KEY]
        req[RADIUS_ATTR_ACCT_TERM_CAUSE] = RADIUS_ATTR_ACCT_TERM_CAUSE_USER_REQ
    
        for key in req.keys():
            debuglogger.debug("		{}: {}".format(key, req[key][KEY_IDX]))
    
        # Send the packet
        _send_radius_acct_pkt(srv_handle, req)
	
    else:
        debuglogger.error("BGP withdraw for {subnet} received from router {rtr}. No state found for {subnet} in state table. Skipped sending Accounting Stop Request\n".format(subnet=route, rtr=RADIUS_SERVER[PEER_IP_KEY]))
        alarmlogger.error("ALARM: BGP withdraw for {subnet} received from router {rtr}. No state found for {subnet} in state table. Skipped sending Accounting Stop Request\n".format(subnet=route, rtr=RADIUS_SERVER[PEER_IP_KEY]))
    
    debuglogger.debug("+++++++ PROCESSING FOR subnet {} COMPLETED +++++++\n".format(route))
	

def send_acct_start_pkt(server, accs_pkt):
    """ (obj, obj) -> NoneType
    
    Prepares and sends a RADIUS accounting Start packet.
    
    """
    # Create Accounting packet
    req = server.CreateAcctPacket()

    # Prepare AVPs
    ip = accs_pkt[RADIUS_ATTR_FRAMED_IP][KEY_IDX]
	
    req[RADIUS_ATTR_NAS_IP] = RADIUS_SERVER[NAS_IP_KEY]
    req[RADIUS_ATTR_NAS_ID] = RADIUS_SERVER[NAS_ID_KEY]
    req[RADIUS_ATTR_FRAMED_IP] = ip
    req[RADIUS_ATTR_FRAMED_NETMASK] = accs_pkt[RADIUS_ATTR_FRAMED_NETMASK][KEY_IDX]
    req[RADIUS_ATTR_ACCT_STS] = RADIUS_ACCT_STS_START
	
	# Debug logs
    debuglogger.debug("+++++++ PREPARE RADIUS ACCOUNTING START REQUEST FOR {} +++++++\n".format(req[RADIUS_ATTR_FRAMED_IP][KEY_IDX]))
    debuglogger.debug("Sending Radius Accounting Start Request with following AVPs")
	
    # Parse AVPs from memory
    if ip in MY_MEM_DB:
	
        for item in MY_MEM_DB[ip]:
          
            if RADIUS_ATTR_SERVICE_TYPE in item:
                req[RADIUS_ATTR_SERVICE_TYPE] = item[RADIUS_ATTR_SERVICE_TYPE]
	 
            if RADIUS_ATTR_APN in item:
                req[RADIUS_ATTR_APN] = item[RADIUS_ATTR_APN]
    
            if RADIUS_ATTR_CALLBACK_NUM in item:
                req[RADIUS_ATTR_CALLBACK_NUM] = item[RADIUS_ATTR_CALLBACK_NUM]
    
            if RADIUS_ATTR_ACCT_SESS_ID in item:
                req[RADIUS_ATTR_ACCT_SESS_ID] = item[RADIUS_ATTR_ACCT_SESS_ID]

            if RADIUS_ATTR_IMSI in item:
                req[RADIUS_ATTR_IMSI] = item[RADIUS_ATTR_IMSI]				
  
            if RADIUS_ATTR_NSAPI in item:
                req[RADIUS_ATTR_NSAPI] = item[RADIUS_ATTR_NSAPI]
    
            if RADIUS_ATTR_CLASS in item:
                req[RADIUS_ATTR_CLASS] = item[RADIUS_ATTR_CLASS].encode()
    
            if RADIUS_ATTR_PROXY_STATE in item:
                req[RADIUS_ATTR_PROXY_STATE] = str(item[RADIUS_ATTR_PROXY_STATE]).encode()
	
    for key in req.keys():
        debuglogger.debug("		{}: {}".format(key, req[key][KEY_IDX]))
		
    # Send the packet
    _send_radius_acct_pkt(server, req)

	
def _send_radius_acct_pkt(server, acct_pkt):
    """ (str, obj) -> NoneType
    
    Sends a RADIUS accounting packet.
    
    """
    # send request
    try:
        reply = server.SendPacket(acct_pkt)		
        eventlogger.info("Radius Accounting {sts} Request sent for {ip}".format(sts=acct_pkt[RADIUS_ATTR_ACCT_STS][KEY_IDX], ip=acct_pkt[RADIUS_ATTR_FRAMED_IP][KEY_IDX]))

        hl.HHME_SERVER_SWITCH = 0
		
        if reply.code == pyrad.packet.AccountingResponse:
            acct_sts = acct_pkt[RADIUS_ATTR_ACCT_STS][KEY_IDX]
            ip_addr = acct_pkt[RADIUS_ATTR_FRAMED_IP][KEY_IDX]
            debuglogger.debug("Radius Accounting {sts} response received for {ip}\n".format(sts=acct_sts, ip=ip_addr))
            eventlogger.info("Radius Accounting {sts} response received for {ip}\n".format(sts=acct_sts, ip=ip_addr))
		    
            if acct_sts == RADIUS_ACCT_STS_STOP:
			    # Remove entry from dict
                MY_MEM_DB.pop(ip_addr)
		
    except pyrad.client.Timeout:
        ip_addr = acct_pkt[RADIUS_ATTR_FRAMED_IP][KEY_IDX]
        acct_sts = acct_pkt[RADIUS_ATTR_ACCT_STS][KEY_IDX]
        hhme = RADIUS_SERVER[ACTIVE_HHME_IP_KEY]
        route_addr = str(IPNetwork(ip_addr + '/' + acct_pkt[RADIUS_ATTR_FRAMED_NETMASK][KEY_IDX]))

        debuglogger.error("BGP Announce for {subnet} from router {rtr}. No response from {h} - Max retransmission count exceeded for Accounting {sts} Request.\n".format(sts=acct_sts, subnet=route_addr, h=hhme, rtr=RADIUS_SERVER[PEER_IP_KEY]))
        alarmlogger.error("ALARM: BGP Announce for {subnet} from router {rtr}. No response from {h} - Max retransmission count exceeded for Accounting {sts} Request.\n".format(sts=acct_sts, subnet=route_addr, h=hhme, rtr=RADIUS_SERVER[PEER_IP_KEY]))

        if hl.HHME_SERVER_SWITCH == 1:
            debuglogger.error("Radius Accounting {sts} Request Timeout for {ip} on all HHME servers\n".format(sts=acct_pkt[RADIUS_ATTR_ACCT_STS][KEY_IDX], ip=ip_addr))
        else:
	        # Change to Secondaty HHME
            change_hhme_server()

            if acct_sts == RADIUS_ACCT_STS_START:
                send_acct_start_pkt(server, acct_pkt)
            elif acct_sts == RADIUS_ACCT_STS_STOP:
                send_acct_stop_pkt(route_addr, RADIUS_SERVER)
		
    except socket.error as error:
        debuglogger.error("Network error: {}. Not able to send Radius Accounting Request".format(error[1]))


def _send_radius_access_pkt(server, accs_pkt):
    """ (obj, dict) -> NoneType
    
    Sends a RADIUS packet to server.
    
    """
    try:
        reply = server.SendPacket(accs_pkt)
        eventlogger.info("Radius Access Request sent for {}".format(accs_pkt[RADIUS_ATTR_FRAMED_IP][KEY_IDX]))
		
        hl.HHME_SERVER_SWITCH = 0
		
        if reply.code == pyrad.packet.AccessAccept:
            debuglogger.debug("Radius Access Accept received\n")
            eventlogger.info("Radius Access Accept received\n")
						
			# Store parameters in Memory
            store_avp_in_dict(accs_pkt, reply)

            for key in reply.keys():
                debuglogger.debug("AVP returned by server: %s: %s" % (key, reply[key]))
				
            reply_msg_code = reply[RADIUS_ATTR_REPLY_MSG][KEY_IDX].split(REPLY_MSG_DELIM)[KEY_IDX]
			
            if  reply_msg_code == CALL_STATE_CREATED:
                # Send Accounting Start Req
                send_acct_start_pkt(server, accs_pkt)
				
            elif reply_msg_code == CALL_STATE_ALREADY_EXIST:
                debuglogger.debug("Radius call for {ip} already established on HHME side.".format(ip=accs_pkt[RADIUS_ATTR_FRAMED_IP][KEY_IDX]))
				
        elif reply.code == pyrad.packet.AccessReject:
            debuglogger.error("Radius Access Reject received\n")
            eventlogger.error("Radius Access Reject received\n")
          
    except pyrad.client.Timeout:
        ip_addr = accs_pkt[RADIUS_ATTR_FRAMED_IP][KEY_IDX]
        route_addr = str(IPNetwork(ip_addr + '/' + accs_pkt[RADIUS_ATTR_FRAMED_NETMASK][KEY_IDX]))
        hhme = RADIUS_SERVER[ACTIVE_HHME_IP_KEY]
		
        debuglogger.error("BGP Announce for {subnet} from router {rtr}. No response from {h} - Max retransmission count exceeded for RADIUS Access Request.\n".format(subnet=route_addr, h=hhme, rtr=RADIUS_SERVER[PEER_IP_KEY]))
        alarmlogger.error("ALARM: BGP Announce for {subnet} from router {rtr}. No response from {h} - Max retransmission count exceeded for RADIUS Access Request.\n".format(subnet=route_addr, h=hhme, rtr=RADIUS_SERVER[PEER_IP_KEY]))
		
        if hl.HHME_SERVER_SWITCH == 1:
            debuglogger.error("Radius Access Request Timeout for {ip} on all HHME servers\n".format(ip=ip_addr))
        else:
	        # Change to Secondaty HHME
            change_hhme_server()
            send_auth_pkt(route_addr, RADIUS_SERVER)
	
		# Send SNMP trap to HHME

    except socket.error as error:
        debuglogger.error("Network error: {}. Not able to send Radius Access Request".format(error[1]))
        #sys.exit(1)

		
def change_hhme_server():
    """ (NoneType) -> NoneType
	
	Switching HHME Server IP address 
	
    """
    primary = RADIUS_SERVER[HHMEA_IP_KEY]
    secondary = RADIUS_SERVER[HHMEB_IP_KEY]
	
    if RADIUS_SERVER[ACTIVE_HHME_IP_KEY] == primary:
	    RADIUS_SERVER[ACTIVE_HHME_IP_KEY] = secondary
    else:
	    RADIUS_SERVER[ACTIVE_HHME_IP_KEY] = primary
	
    hl.HHME_SERVER_SWITCH = 1	
    debuglogger.error("Switching HHME Server to {}".format(RADIUS_SERVER[ACTIVE_HHME_IP_KEY]))
    alarmlogger.error("ALARM: Switching HHME Server to {}".format(RADIUS_SERVER[ACTIVE_HHME_IP_KEY]))
	
		
def store_avp_in_dict(packet_data, reply_msg):
    """ (obj, obj) -> NoneType
	
	Store all AVPs in dict
	
	"""
    list_of_avp = []
	
    rad_avp = { RADIUS_ATTR_NSAPI : packet_data[RADIUS_ATTR_NSAPI][KEY_IDX] }
    list_of_avp.append(rad_avp.copy())
	
    rad_avp = { RADIUS_ATTR_APN : packet_data[RADIUS_ATTR_APN][KEY_IDX] }
    list_of_avp.append(rad_avp.copy())
	
    rad_avp = { RADIUS_ATTR_SERVICE_TYPE : reply_msg[RADIUS_ATTR_SERVICE_TYPE][KEY_IDX] }
    list_of_avp.append(rad_avp.copy())
	
    rad_avp = { RADIUS_ATTR_PROXY_STATE : reply_msg[RADIUS_ATTR_PROXY_STATE][KEY_IDX].decode() }
    list_of_avp.append(rad_avp.copy())

	# Parse class attributes
    class_attr = reply_msg[RADIUS_ATTR_CLASS][KEY_IDX].decode()
    rad_avp = { RADIUS_ATTR_CLASS : class_attr }
    list_of_avp.append(rad_avp.copy())
    elements = class_attr.split(CLASS_ATTR_DELIM)
	
    for item in elements:

        class_avp = item.split(CLASS_ATTR_VAL_DELIM)

        if class_avp[KEY_IDX] == RADIUS_ATTR_CLASS_MY_ID:
            rad_avp = { RADIUS_ATTR_IMSI : class_avp[VALUE_IDX] }
            list_of_avp.append(rad_avp.copy())
		
        if class_avp[KEY_IDX] == RADIUS_ATTR_CLASS_HCR:
            rad_avp = { RADIUS_ATTR_ACCT_SESS_ID : class_avp[VALUE_IDX] }
            list_of_avp.append(rad_avp.copy())

            rad_avp = { RADIUS_ATTR_CALLBACK_NUM : class_avp[VALUE_IDX] }
            list_of_avp.append(rad_avp.copy())
	
    MY_MEM_DB[packet_data[RADIUS_ATTR_FRAMED_IP][KEY_IDX]] = list_of_avp

    	
# main
if __name__ == "__main__":
    #rad_dict = {SERVER_IP_KEY: "192.168.6.102", SECRET_KEY: "secret",
     #           USER_KEY: "AGGR_CONFLICTING_RULES_01", PASS_KEY: "password"}

    rad_dict = {SECRET_KEY: "testing123",
                USER_KEY: "test", PASS_KEY: "test", RETRANS_CNT_KEY: "3", 
				TIMEOUT_KEY: "5", NSAPI_KEY: "7", ACTIVE_HHME_IP_KEY: "192.168.6.183"}

    send_auth_pkt("10.51.1.0/31", rad_dict)
	
    #send_auth_pkt("10.51.1.0/27", rad_dict)
    #send_auth_pkt("192.168.101.0/30", rad_dict)
    #send_acct_stop_pkt("192.168.101.0/30", rad_dict)
