#!/usr/bin/env python3
import ipaddress as ipaddr


# Globals
GX_STATE_ACCESS_REQ = "Access Req Sent"
GX_STATE_ACCESS_ACPT = "Access Accept Received"
GX_STATE_ACCESS_REJ = "Access Reject Received"
GX_STATE_ACCT_START_REQ = "Accounting Start Req Sent"
GX_STATE_ACCT_START_RESP = "Accounting Start Resp Received"
GX_STATE_ACCT_STOP_REQ = "Accounting Stop Req Sent"
GX_STATE_ACCT_STOP_RESP = "Accounting Stop Resp Received"
GX_STATE_ACCT_INTRM_REQ = "Accounting Interim Req Sent"
GX_STATE_ACCT_INTRM_RESP = "Accounting Interim Resp Received"
GX_STATE_SUBNET_APPEAR = "GX Subnet appeared"
GX_STATE_SUBNET_DISAPPEAR = "GX Subnet disappeared"

# RADIUS Server config
SERVER_IP_KEY = "server"
SECRET_KEY = "secret"
USER_KEY = "user"
PASS_KEY = "pass"

# MySQL database config
DB_IN_TABLE = "acct_in"
DB_OUT_TABLE = "acct_out"
DB_CALL_STAT_TABLE = "call_stats"

# MySQL table column names
IP_ADDR_COL = "ip_addr"
IN_PKT_COL = "in_packets"
IN_BYTES_COL = "in_bytes"
OUT_PKT_COL = "out_packets"
OUT_BYTES_COL = "out_bytes"
SUBNET_COL = "subnet"
IP_DST_COL = "DST_IP"
IP_SRC_COL = "SRC_IP"
PKT_COL = "PACKETS"
BYTE_COL = "BYTES"

# RADIUS AVP column names
USER_NAME_COL = "user_name"
APN_COL = "apn"
HCR_COL = "hcr"
ACCT_SESS_ID_COL = "acct_sess_id"
GX_ID_COL = "gx_terminal_id"
NSAPI_COL = "nsapi"
CLASS_COL = "class"
PROXY_STATE_COL = "proxy_state"

# Constant values
CHAR_COMMA = ','
KEY_IDX = 0
VALUE_IDX = 1
CLASS_ATTR_DELIM = ":"
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
	

# main
if __name__ == "__main__":
    pass