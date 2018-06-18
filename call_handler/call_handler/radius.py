#!/usr/bin/env python3
from pyrad.client import Client
from pyrad.dictionary import Dictionary
import pyrad.packet
import sys
import ipaddress as ipaddr
import logging
import random as ran
from helpers import *
import os
import ormsql

# Globals
logger = logging.getLogger(__name__)

DICT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dictionary")
NAS_IP = "10.125.66.40"
APN = "mil.test.apn.com"
SERVICE_TYPE = 0x999
NAS_ID = "BRCNGG01"
PROXY_STATE_MAX = 1000 * 1000
NSAPI_MAX = 15

RADIUS_ATTR_PASSWORD = "User-Password"
RADIUS_ATTR_FRAMED_IP = "Framed-IP-Address"
RADIUS_ATTR_FRAMED_NETMASK = "Framed-IP-Netmask"
RADIUS_ATTR_NAS_IP = "NAS-IP-Address"
RADIUS_ATTR_NAS_ID = "NAS-Identifier"
RADIUS_ATTR_APN = "Called-Station-Id"
RADIUS_ATTR_NSAPI = "3GPP-NSAPI"
RADIUS_ATTR_SERVICE_TYPE = "Service-Type"
RADIUS_ATTR_ACCT_SESS_ID = "Acct-Session-Id"
RADIUS_ATTR_CALLBACK_NUM = "Callback-Number"
RADIUS_ATTR_PROXY_STATE = "Proxy-State"
RADIUS_ATTR_ACCT_STS = "Acct-Status-Type"
RADIUS_ATTR_USER_NAME = "User-Name"
RADIUS_ATTR_CLASS = "Class"
RADIUS_ATTR_CLASS_USER_PROFILE = "USR"
RADIUS_ATTR_CLASS_HCR = "HCR"
RADIUS_ATTR_CLASS_GX_ID = "GXT"
RADIUS_ACCT_STS_STOP = "Stop"
RADIUS_ACCT_STS_START = "Start"
RADIUS_ACCT_STS_INTERIM = "Interim-Update"

INSERT_CLAUSE = "INSERT INTO {tb} ({col}) VALUES ({val});"
SELECT_CLAUSE = "SELECT * from {tb} WHERE ip_addr='{framed_ip}';"


# User defined methods
def send_auth_pkt(route, rad_server):
    """ (str, dict) -> NoneType
    
    Prepares and sends a RADIUS authentication packet.
    
    """
    ip_addr = get_ip_from_subnet(route)
    srv_handle = Client(server=rad_server[SERVER_IP_KEY], secret=rad_server[SECRET_KEY].encode(), dict=Dictionary(DICT))

    # Create request for all IP addresses that belongs to a subnet
    for ip in ip_addr:
	
        # Prepare AVPs
        req = srv_handle.CreateAuthPacket(code=pyrad.packet.AccessRequest, User_Name=rad_server[USER_KEY]) # TODO: Remove test user
        req[RADIUS_ATTR_PASSWORD] = req.PwCrypt(rad_server[PASS_KEY])

        req[RADIUS_ATTR_SERVICE_TYPE] = SERVICE_TYPE
        req[RADIUS_ATTR_NAS_IP] = NAS_IP
        req[RADIUS_ATTR_NAS_ID] = NAS_ID
        req[RADIUS_ATTR_APN] = APN
        req[RADIUS_ATTR_PROXY_STATE] = str(ran.randint(1, PROXY_STATE_MAX)).encode()
        req[RADIUS_ATTR_FRAMED_IP] = ip
        net = ipaddr.ip_network(route)
        req[RADIUS_ATTR_FRAMED_NETMASK] = str(net.netmask)
        nsapi = '{:1x}'.format(ran.randint(1, NSAPI_MAX))
        req[RADIUS_ATTR_NSAPI] = str(nsapi)

        # Send the packet
        _send_radius_access_pkt(srv_handle, req)
		

def send_acct_stop_pkt(route, rad_server):
    """ (str, dict) -> NoneType
    
    Prepares and sends a RADIUS accounting Stop packet.
    
    """
    ip_addr = get_ip_from_subnet(route)
    srv_handle = Client(server=rad_server[SERVER_IP_KEY], secret=rad_server[SECRET_KEY].encode(), dict=Dictionary(DICT))

    # Send Accounting stop request for all IP addresses that belongs to a subnet
    for ip in ip_addr:

        # Create Accounting packet
        req = srv_handle.CreateAcctPacket()

        # Fire query to database
        gxdb = ormsql.GxDatabase()
        sql = SELECT_CLAUSE.format(tb=DB_CALL_STAT_TABLE, framed_ip=ip)
        result = gxdb.execute_query(sql)
        records = result.fetchall()

        # Parse AVPs from records
        if records:
            columns = records[KEY_IDX].keys()

            for item in columns:
                if item == USER_NAME_COL:
                    req[RADIUS_ATTR_USER_NAME] = records[KEY_IDX][columns.index(item)]

                if item == APN_COL:
                    req[RADIUS_ATTR_APN] = records[KEY_IDX][columns.index(item)]

                if item == HCR_COL:
                    req[RADIUS_ATTR_CALLBACK_NUM] = str(records[KEY_IDX][columns.index(item)])

                if item == ACCT_SESS_ID_COL:
                    req[RADIUS_ATTR_ACCT_SESS_ID] = records[KEY_IDX][columns.index(item)]

                if item == NSAPI_COL:
                    req[RADIUS_ATTR_NSAPI] = '{:1x}'.format(records[KEY_IDX][columns.index(item)])
					
                if item == CLASS_COL:
                    req[RADIUS_ATTR_CLASS] = records[KEY_IDX][columns.index(item)].encode()
					
                if item == PROXY_STATE_COL:
                    req[RADIUS_ATTR_PROXY_STATE] = str(records[KEY_IDX][columns.index(item)]).encode()
					
            # Prepare AVPs
            req[RADIUS_ATTR_FRAMED_IP] = ip
            net = ipaddr.ip_network(route)
            req[RADIUS_ATTR_FRAMED_NETMASK] = str(net.netmask)
            req[RADIUS_ATTR_ACCT_STS] = RADIUS_ACCT_STS_STOP

            # Send the packet
            _send_radius_acct_pkt(srv_handle, req)


def send_acct_start_pkt(server, accs_pkt, reply_msg):
    """ (obj, obj, dict) -> NoneType
    
    Prepares and sends a RADIUS accounting Start packet.
    
    """
    # Create Accounting packet
    req = server.CreateAcctPacket()

    # Prepare AVPs
    req[RADIUS_ATTR_SERVICE_TYPE] = reply_msg[RADIUS_ATTR_SERVICE_TYPE][KEY_IDX]
    req[RADIUS_ATTR_NAS_IP] = NAS_IP
    req[RADIUS_ATTR_NAS_ID] = NAS_ID
    req[RADIUS_ATTR_APN] = APN
    req[RADIUS_ATTR_PROXY_STATE] = reply_msg[RADIUS_ATTR_PROXY_STATE][KEY_IDX]  # OR accs_pkt[RADIUS_ATTR_PROXY_STATE][KEY_IDX]
    req[RADIUS_ATTR_FRAMED_IP] = reply_msg[RADIUS_ATTR_FRAMED_IP][KEY_IDX]
    req[RADIUS_ATTR_FRAMED_NETMASK] = reply_msg[RADIUS_ATTR_FRAMED_NETMASK][KEY_IDX]
    req[RADIUS_ATTR_CLASS] = reply_msg[RADIUS_ATTR_CLASS][KEY_IDX]
    req[RADIUS_ATTR_NSAPI] = accs_pkt[RADIUS_ATTR_NSAPI][KEY_IDX]

    # Parse class attributes

    # TODO: Get parameters from db

    class_attr = reply_msg[RADIUS_ATTR_CLASS][KEY_IDX].decode()
    elements = class_attr.split(CLASS_ATTR_DELIM)

    for item in elements:
        avp = item.split(CLASS_ATTR_VAL_DELIM)

        if avp[KEY_IDX] == RADIUS_ATTR_CLASS_USER_PROFILE:
            req[RADIUS_ATTR_USER_NAME] = avp[VALUE_IDX]

        if avp[KEY_IDX] == RADIUS_ATTR_CLASS_HCR:
            req[RADIUS_ATTR_ACCT_SESS_ID] = avp[VALUE_IDX]
            req[RADIUS_ATTR_CALLBACK_NUM] = avp[VALUE_IDX]

    req[RADIUS_ATTR_ACCT_STS] = RADIUS_ACCT_STS_START

    # Send the packet
    _send_radius_acct_pkt(server, req)


def insert_pkt_data_in_db(accs_pkt, reply_msg):
    """
    
    Create a call state in db.
    
    """
    # Connect to db
    gxdb = ormsql.GxDatabase()

    # Parse Access-Accept packet AVPs
    framed_ip = reply_msg[RADIUS_ATTR_FRAMED_IP][KEY_IDX]
    apn = accs_pkt[RADIUS_ATTR_APN][KEY_IDX]
    nsapi = int(accs_pkt[RADIUS_ATTR_NSAPI][KEY_IDX], 16)
    proxy_state = accs_pkt[RADIUS_ATTR_PROXY_STATE][KEY_IDX].decode()
    class_attr = reply_msg[RADIUS_ATTR_CLASS][KEY_IDX].decode()
    elements = class_attr.split(CLASS_ATTR_DELIM)
	
    for item in elements:
        avp = item.split(CLASS_ATTR_VAL_DELIM)

        if avp[KEY_IDX] == RADIUS_ATTR_CLASS_USER_PROFILE:
            username = avp[VALUE_IDX]

        if avp[KEY_IDX] == RADIUS_ATTR_CLASS_HCR:
            hcr = avp[VALUE_IDX]
            acc_sess_id = hcr

        if avp[KEY_IDX] == RADIUS_ATTR_CLASS_GX_ID:
            gx_id = avp[VALUE_IDX]

    # Construct column name string TODO: Check the presence of every AVP before inserting
    columns = IP_ADDR_COL + CHAR_COMMA + APN_COL + CHAR_COMMA + USER_NAME_COL + CHAR_COMMA + HCR_COL + CHAR_COMMA + \
              ACCT_SESS_ID_COL + CHAR_COMMA + GX_ID_COL + CHAR_COMMA + NSAPI_COL + CHAR_COMMA + CLASS_COL + \
              CHAR_COMMA + PROXY_STATE_COL

    # Construct column value string
    columns_val = CHAR_SINGLE_QUOTE + framed_ip + CHAR_SINGLE_QUOTE + CHAR_COMMA + CHAR_SINGLE_QUOTE + apn + \
                  CHAR_SINGLE_QUOTE + CHAR_COMMA + CHAR_SINGLE_QUOTE + username + CHAR_SINGLE_QUOTE + CHAR_COMMA + \
                  hcr + CHAR_COMMA + CHAR_SINGLE_QUOTE + acc_sess_id + CHAR_SINGLE_QUOTE + CHAR_COMMA + \
                  CHAR_SINGLE_QUOTE + gx_id + CHAR_SINGLE_QUOTE + CHAR_COMMA + str(nsapi) + CHAR_COMMA + \
                  CHAR_SINGLE_QUOTE + class_attr + CHAR_SINGLE_QUOTE + CHAR_COMMA + proxy_state

    # Fire SQL query
    sql = INSERT_CLAUSE.format(tb=DB_CALL_STAT_TABLE, col=columns, val=columns_val)
    gxdb.execute_query(sql)

	
def _send_radius_acct_pkt(server, acct_pkt):
    """ (str) -> NoneType
    
    Sends a RADIUS accounting packet.
    
    """
    # send request
    try:
        server.SendPacket(acct_pkt)

    except pyrad.client.Timeout:
        logger.error("Request Timeout")
        #sys.exit(1)

    except socket.error as error:
        logger.error("Network error: " + error[1])
        #sys.exit(1)


def _send_radius_access_pkt(server, accs_pkt):
    """ (obj, dict) -> NoneType
    
    Sends a RADIUS packet to server.
    
    """
    try:
        reply = server.SendPacket(accs_pkt)

        if reply.code == pyrad.packet.AccessAccept:
            logger.info("Access accepted")

            # Insert data into database
            insert_pkt_data_in_db(accs_pkt, reply)

            # Send Accounting Start Req TODO: Parse reply
            send_acct_start_pkt(server, accs_pkt, reply)

        else:
            logger.info("Access denied")

        for key in reply.keys():
            logger.debug("Attributes returned by server:")
            logger.debug("%s: %s" % (key, reply[key]))

    except pyrad.client.Timeout:
        logger.error("Request Timeout")
        #sys.exit(1)

    except socket.error as error:
        logger.error("Network error: " + error[1])
        #sys.exit(1)

# main
if __name__ == "__main__":
    rad_dict = {SERVER_IP_KEY: "192.168.6.102", SECRET_KEY: "secret",
                USER_KEY: "AGGR_CONFLICTING_RULES_01", PASS_KEY: "password"}


    send_auth_pkt("10.51.1.0/27", rad_dict)
    #send_auth_pkt("192.168.101.0/30", rad_dict)
    #send_acct_stop_pkt("192.168.101.0/30", rad_dict)
