#!/usr/bin/env python3
import sys
import time
import json
import radius
import logging
from configparser import ConfigParser
from helpers import *


# Globals
GENERIC_SUBNET = "0.0.0.0/0"
NLRI_KEY = "nlri"
IPV4_KEY = "ipv4 unicast"
ROUTE_ANNOUNCE_KEY = "announce"
ROUTE_WITHDRAW_KEY = "withdraw"


# Methods
def cfg_init():
    """ () -> NoneType
    
    Set configuration for logging.
    
    """
    cfg_parser = ConfigParser()
	
	# Read config file
    try:
        cfg_parser.read(CONFIG_FILE_PATH)
    except Exception as err:
        print("Exception:", err, file=sys.stderr)
        sys.exit(1)

	# Read RADIUS server configuration
    radius_server_ip = get_config_val(cfg_parser, SECTION_RAD_SERVER, SERVER_IP_KEY)
    radius_secret = get_config_val(cfg_parser, SECTION_RAD_SERVER, SECRET_KEY)
    radius_user = get_config_val(cfg_parser, SECTION_RAD_SERVER, USER_KEY)
    radius_passwd = get_config_val(cfg_parser, SECTION_RAD_SERVER, PASS_KEY)
    
    radius_hhmea_ip = get_config_val(cfg_parser, SECTION_RAD_SERVER, HHMEA_IP_KEY)
    radius_hhmeb_ip = get_config_val(cfg_parser, SECTION_RAD_SERVER, HHMEB_IP_KEY)
    radius_nsapi = get_config_val(cfg_parser, SECTION_RAD_SERVER, NSAPI_KEY)
    radius_retrans_cnt = get_config_val(cfg_parser, SECTION_RAD_SERVER, RETRANS_CNT_KEY)
    radius_timeout = get_config_val(cfg_parser, SECTION_RAD_SERVER, TIMEOUT_KEY)
	
	# Save configuration in dict
    global RADIUS_SERVER
    RADIUS_SERVER = { SERVER_IP_KEY : radius_server_ip,
                      SECRET_KEY : radius_secret,
                      USER_KEY : radius_user,
                      PASS_KEY : radius_passwd,
					  HHMEA_IP_KEY : radius_hhmea_ip,
					  HHMEB_IP_KEY : radius_hhmeb_ip,
					  NSAPI_KEY : radius_nsapi,
					  RETRANS_CNT_KEY : radius_retrans_cnt,
					  TIMEOUT_KEY : radius_timeout,
					}
	
	# Read Log file configuration
    logf = get_config_val(cfg_parser, SECTION_LOG, LOG_FILE_KEY)
	
	# Debug enable / disable
    isDebug = get_config_val(cfg_parser, SECTION_LOG, DEBUG_FLAG_KEY, CONFIG_VAL_TYPE_BOOL)

    if isDebug:
        debug_level = logging.DEBUG
    else:
        debug_level = logging.INFO

    logging.basicConfig(filename=logf, format='[ %(asctime)s ] [ %(module)-8s ] [ %(levelname)-6s ] %(message)s ',
                        level=debug_level, datefmt='%a, %d %b %Y %H:%M:%S')


def get_config_val(cfg_handle, section, key, val_type=CONFIG_VAL_TYPE_STR):
    """ (obj, str, str, str) -> str or bool
	
	Read values from given config file.
	
    """
    if val_type == CONFIG_VAL_TYPE_STR:
        try:
	        val = cfg_handle.get(section, key)
        except Exception as err:
            print("Exception: {e} config: {k}".format(e=err, k=key), file=sys.stderr)
            sys.exit(1) 
			
    elif val_type == CONFIG_VAL_TYPE_BOOL:
        try:
            val = cfg_handle.getboolean(section, key)
        except Exception as err:
            print("Exception: {e} config: {k}".format(e=err, k=key), file=sys.stderr)
            sys.exit(1) 
			
    if val == '':
        print("Exception: blank value for key:", key, file=sys.stderr)
        sys.exit(1)
		
    return val
	
						
def find_item(obj, key):
    """ (dict, str) -> dict
    
    Find the key recursively.
    
    """
    if key in obj:
        return obj[key]

    for k, v in obj.items():
        if isinstance(v, dict):
            item = find_item(v, key)
            if item is not None:
                return item


def parse_announce_msg(ann_info):
    """ (dict) -> List
    
    Parses the json message and returns the list of routes.
    
    """
    bgp_routes = []

    ipv4 = find_item(ann_info, IPV4_KEY)
    for k, v in ipv4.items():
        for item in v:
            if NLRI_KEY in item:
                if item[NLRI_KEY] != GENERIC_SUBNET:
                    bgp_routes.append(item[NLRI_KEY])

    return bgp_routes


def parse_withdraw_msg(withdr_info):
    """ (dict) -> List

    Parses the json message and returns the list of routes.

    """
    bgp_routes = []

    ipv4 = find_item(withdr_info, IPV4_KEY)

    for item in ipv4:
        if NLRI_KEY in item:
            if item[NLRI_KEY] != GENERIC_SUBNET:
                bgp_routes.append(item[NLRI_KEY])

    return bgp_routes


def send_radius_access_req(routes):
    """ (list) -> NoneType
    
    Send RADIUS Access Request packet.
    
    """
    for item in routes:
        logging.info("Sending Access request for {subnet}".format(subnet=item))
        radius.send_auth_pkt(item, RADIUS_SERVER)


def send_acct_stop_req(routes):
    """ (str) -> NoneType
    
    Send RADIUS Accounting Stop Req. 
    
    """
    for item in routes:
        logging.info("Sending Accounting Stop request for {subnet}".format(subnet=item))
        radius.send_acct_stop_pkt(item, RADIUS_SERVER)


def process_msg(msg):
    """ (dict) -> NoneType
    
	Parse the BGP messages.
    
    """
    announce_msg = find_item(msg, ROUTE_ANNOUNCE_KEY)

    if announce_msg:
        send_radius_access_req(parse_announce_msg(announce_msg))

    withdraw_msg = find_item(msg, ROUTE_WITHDRAW_KEY)

    if withdraw_msg:
        send_acct_stop_req(parse_withdraw_msg(withdraw_msg))


# main
if __name__ == "__main__":

    cfg_init()

    while True:
        try:
            # Parse BGP messages
            line = sys.stdin.readline().strip()
            bgp_msg = json.loads(line)
            process_msg(bgp_msg)

            #time.sleep(1)

        except KeyboardInterrupt:
            sys.exit(1)

        # most likely a signal during readline
        except IOError:
            sys.exit(1)
