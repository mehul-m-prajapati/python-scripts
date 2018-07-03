#!/usr/bin/env python3
import sys
import time
import json
import radius
import logging
from configparser import ConfigParser
from helpers import *
import helpers as hl


# Globals
DEBUG_LOG_FILE_PATH = "/opt/my-client/logs/my_debug.log"
EVENT_LOG_FILE_PATH = "/opt/my-client/logs/my_event.log"
ALARM_LOG_FILE_PATH = "/opt/my-client/logs/my_alarm.log"
GENERIC_SUBNET = "0.0.0.0/0"
NLRI_KEY = "nlri"
PEER_ADDR_KEY = "address"
IPV4_KEY = "ipv4 unicast"
ROUTE_ANNOUNCE_KEY = "announce"
ROUTE_WITHDRAW_KEY = "withdraw"


# Methods
def cfg_init():
    """ () -> NoneType
    
    Set configuration for logging.
    
    """
	# Create log directories
    dir_path = os.path.split(DEBUG_LOG_FILE_PATH)

    try:
        os.makedirs(dir_path[0])
    except Exception as err:
        pass
	
	# Debug Logs
    global debuglogger
    debuglogger = setup_logger(DEBUG_LOGGER, DEBUG_LOG_FILE_PATH, logging.DEBUG)	
	
	# Read config file
    cfg_parser = ConfigParser()
	
    try:
        cfg_parser.read(CONFIG_FILE_PATH)
    except Exception as err:
        debuglogger.error("Exception:", err, file=sys.stderr)
        sys.exit(1)
		
	# Event Logs
    global eventlogger
    isEventLog = get_config_val(cfg_parser, SECTION_RAD_SERVER, EVENT_LOG_KEY, CONFIG_VAL_TYPE_BOOL)
	
    if isEventLog == True:
        eventlogger = setup_logger(EVENT_LOGGER, EVENT_LOG_FILE_PATH, logging.INFO)
    else:
        eventlogger = setup_logger(EVENT_LOGGER, EVENT_LOG_FILE_PATH, logging.NOTSET)
	
	# Alarm Logs
    global alarmlogger
    alarmlogger = setup_logger(ALARM_LOGGER, ALARM_LOG_FILE_PATH, logging.ERROR)
	
	# Read MY configuration
    radius_secret = get_config_val(cfg_parser, SECTION_RAD_SERVER, SECRET_KEY)
    #radius_user = get_config_val(cfg_parser, SECTION_RAD_SERVER, USER_KEY)
    #radius_passwd = get_config_val(cfg_parser, SECTION_RAD_SERVER, PASS_KEY)
    
    radius_hhmea_ip = get_config_val(cfg_parser, SECTION_RAD_SERVER, HHMEA_IP_KEY)
    radius_hhmeb_ip = get_config_val(cfg_parser, SECTION_RAD_SERVER, HHMEB_IP_KEY)
    radius_nsapi = get_config_val(cfg_parser, SECTION_RAD_SERVER, NSAPI_KEY)
    radius_retrans_cnt = get_config_val(cfg_parser, SECTION_RAD_SERVER, RETRANS_CNT_KEY)
    radius_timeout = get_config_val(cfg_parser, SECTION_RAD_SERVER, TIMEOUT_KEY)
	
    radius_apn =  get_config_val(cfg_parser, SECTION_RAD_SERVER, APN_KEY)
    radius_nas_ip =  get_config_val(cfg_parser, SECTION_RAD_SERVER, NAS_IP_KEY)
    radius_nas_id =  get_config_val(cfg_parser, SECTION_RAD_SERVER, NAS_ID_KEY)
    radius_req_delay = get_config_val(cfg_parser, SECTION_RAD_SERVER, RADIUS_DELAY_KEY)
	
	# Save configuration in dict
    RADIUS_SERVER[SECRET_KEY]  = radius_secret
    #RADIUS_SERVER[USER_KEY] = radius_user
    #RADIUS_SERVER[PASS_KEY] = radius_passwd
    RADIUS_SERVER[HHMEA_IP_KEY] = radius_hhmea_ip
    RADIUS_SERVER[HHMEB_IP_KEY] = radius_hhmeb_ip
    RADIUS_SERVER[NSAPI_KEY] = radius_nsapi
    RADIUS_SERVER[RETRANS_CNT_KEY] = radius_retrans_cnt
    RADIUS_SERVER[TIMEOUT_KEY] = radius_timeout
    RADIUS_SERVER[ACTIVE_HHME_IP_KEY] = radius_hhmea_ip
	
    RADIUS_SERVER[APN_KEY] = radius_apn
    RADIUS_SERVER[NAS_IP_KEY] = radius_nas_ip
    RADIUS_SERVER[NAS_ID_KEY] = radius_nas_id
    RADIUS_SERVER[RADIUS_DELAY_KEY] = radius_req_delay
		
    debuglogger.debug("MY configuration successfully loaded")
		
    for key, val in RADIUS_SERVER.items():
        debuglogger.debug("{k} = {v}".format(k=key, v=val))
		
		
def get_config_val(cfg_handle, section, key, val_type=CONFIG_VAL_TYPE_STR):
    """ (obj, str, str, str) -> str or bool
	
	Read values from given config file.
	
    """
    if val_type == CONFIG_VAL_TYPE_STR:
        try:
	        val = cfg_handle.get(section, key)
        except Exception as err:
            debuglogger.error("Exception: {e} config: {k}".format(e=err, k=key), file=sys.stderr)
            sys.exit(1) 
			
    elif val_type == CONFIG_VAL_TYPE_BOOL:
        try:
            val = cfg_handle.getboolean(section, key)
        except Exception as err:
            debuglogger.error("Exception: {e} config: {k}".format(e=err, k=key), file=sys.stderr)
            sys.exit(1) 
			
    if val == '':
        debuglogger.error("Exception: blank value for key:", key, file=sys.stderr)
        sys.exit(1)
		
    return val
	
	
def setup_logger(logger_name, log_file, debug_level):
    """ (str, str, obj) -> logger obj
	
	Configure logger.
	
    """
    log_setup = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s | %(module)-6s | %(levelname)-6s | %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
    fileHandler = logging.FileHandler(log_file, mode='a')
    fileHandler.setFormatter(formatter)
    log_setup.setLevel(debug_level)
    log_setup.addHandler(fileHandler)
    	
    return log_setup
	
						
def find_item(obj, key):
    """ (dict, str) -> dict
    
    Find the key recursively.
    
    """
    try:
        if key in obj:
            return obj[key]
        
        for k, v in obj.items():
            if isinstance(v, dict):
                item = find_item(v, key)
                if item is not None:
                    return item
					
    except Exception as err:
	    pass

		
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

    if len(bgp_routes) > 0:
        debuglogger.debug("Announce message parsing done. BGP routes {bgp} appeared".format(bgp=bgp_routes))
        eventlogger.info("BGP routes: {bgp} appeared".format(bgp=bgp_routes))
	
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

    debuglogger.debug("Withdraw message parsing done. BGP routes {bgp} dis-appeared".format(bgp=bgp_routes))
    eventlogger.info("BGP routes {bgp} dis-appeared".format(bgp=bgp_routes))
	
    return bgp_routes


def send_radius_access_req(routes):
    """ (list) -> NoneType
    
    Send RADIUS Access Request packet.
    
    """
    for item in routes:
        debuglogger.debug("+++++++ PROCESSING FOR subnet {} STARTED +++++++\n".format(item))

        hl.HHME_SERVER_SWITCH = 0		
        radius.send_auth_pkt(item, RADIUS_SERVER)


def send_acct_stop_req(routes):
    """ (str) -> NoneType
    
    Send RADIUS Accounting Stop Req. 
    
    """
    for item in routes:
        debuglogger.debug("+++++++ PROCESSING FOR subnet {} STARTED +++++++\n".format(item))
		
        hl.HHME_SERVER_SWITCH = 0
        radius.send_acct_stop_pkt(item, RADIUS_SERVER)


def process_msg(msg):
    """ (dict) -> NoneType
    
	Parse the BGP messages.
    
    """
    peer_msg = find_item(msg, PEER_ADDR_KEY)
    peer_ip = find_item(peer_msg, PEER_IP_KEY)	
    RADIUS_SERVER[PEER_IP_KEY] = peer_ip
	
    announce_msg = find_item(msg, ROUTE_ANNOUNCE_KEY)

    if announce_msg:
        debuglogger.debug("Received announce message {msg}".format(msg=announce_msg))
        send_radius_access_req(parse_announce_msg(announce_msg))

    withdraw_msg = find_item(msg, ROUTE_WITHDRAW_KEY)

    if withdraw_msg:
        debuglogger.debug("Received withdraw message {msg}".format(msg=withdraw_msg))
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
            debuglogger.warn("Got Keyboard Interrupt. Shut down the process.")
            sys.exit(1)

        # most likely a signal during readline
        except IOError:
            debuglogger.error("Can't read from stdin.")
            sys.exit(1)
