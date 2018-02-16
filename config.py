#!/usr/bin/env python3
# sample.ini
# [log]
# is_debug=False
# log_file=/opt/logs/debug.log
#
#
import logging
from configparser import ConfigParser

CONFIG_FILE = "sample.ini"
SECTION_LOG = "log"
LOG_FILE_KEY = log_file
DEBUG_FLAG_KEY = is_debug



def cfg_init():
    """ () -> NoneType
    
    Set configuration for logging.
    
    """
    cfg_parser = ConfigParser()
    cfg_parser.read(CONFIG_FILE)

    logf = cfg_parser.get(SECTION_LOG, LOG_FILE_KEY)
    isDebug = cfg_parser.getboolean(SECTION_LOG, DEBUG_FLAG_KEY)

    if isDebug:
        debug_level = logging.DEBUG
    else:
        debug_level = logging.INFO

    logging.basicConfig(filename=logf, format='[ %(asctime)s ] [ %(module)-8s ] [ %(levelname)-8s ]  %(message)s ',
                        level=debug_level, datefmt='%a, %d %b %Y %H:%M:%S')
