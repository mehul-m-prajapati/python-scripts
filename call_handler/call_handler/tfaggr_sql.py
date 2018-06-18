#!/usr/bin/env python3
import ipaddress as ipaddr
import pymysql
import logging
from helpers import *
import os


# Globals
GX_LOG_FILE_PATH = "/opt/gx/logs/gx_debug.log"

TUP_ELEM_IDX = 0
IP_ADDR_IDX = 0
PACKETS_IDX = 1
BYTES_IDX = 2

DB_HOST = "192.168.6.183"
DB_PORT = 3306
DB_USERNAME = "root"
DB_PASSWORD = "tmfsr82"
DB_NAME = "pmacct"
DB_SUBNET_TABLE = "bgp_subnets"

TX_IN = "inbound"
TX_OUT = "outbound"

ACCT_SELECT_CLAUSE = "SELECT * from {tb} where {col}='{val}';"
ROUTE_SELECT_CLAUSE = "SELECT {col} from {tb};"
INSERT_CLAUSE = "INSERT INTO {tb} ({c1}, {c2}, {c3}) VALUES ('{v1}', {v2}, {v3}) ON DUPLICATE KEY UPDATE {c2}={v2}, {c3}={v3};"


# User defined methods
def get_routes_from_db(table, col_name):
    """ (str, str) -> list

    Fetches BGP routes from the specified table.

    """
    routes = []

    try:
        # Open database connection
        conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USERNAME, passwd=DB_PASSWORD, db=DB_NAME,
                               autocommit=True)
        cursor = conn.cursor()

        # Prepare SQL query to SELECT records from the database.
        sql = ROUTE_SELECT_CLAUSE.format(tb=table, col=col_name)

        try:
            # Execute the SQL command
            cursor.execute(sql)
            routes = [item[0] for item in cursor.fetchall()]

        except Exception as err:
            # Rollback in case there is any error
            conn.rollback()
            logging.error("Exception:", err)

        # disconnect from server
        conn.close()

    except Exception as err:
        logging.error("Exception:", err)

    return routes


def get_acct_records_from_db(table, col_name, col_val):
    """ (str, str, str) -> tuple of tuples
    
    Fetches the accounting records from the specified table.
    
    """
    results = ()

    try:
        # Open database connection
        conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USERNAME, passwd=DB_PASSWORD, db=DB_NAME,
                               autocommit=True)
        cursor = conn.cursor()

        # Prepare SQL query to SELECT records from the database.
        sql = ACCT_SELECT_CLAUSE.format(tb=table, col=col_name, val=col_val)

        try:
            # Execute the SQL command
            cursor.execute(sql)
            results = cursor.fetchall()

        except Exception as err:
            # Rollback in case there is any error
            conn.rollback()
            logging.error("Exception:", err)

        # field_names = [i[0] for i in cursor.description]
        # print (field_names)

        conn.close()

    except Exception as err:
        print("Exception :", err)

    return results


def insert_records_to_db(table, traffic_type, item):
    """	(str, str, tuple) -> NoneType
    
    Insert record into the specified table.
    
    """

    try:
        # Open database connection
        conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USERNAME, passwd=DB_PASSWORD, db=DB_NAME,
                               autocommit=True)
        cursor = conn.cursor()

        # Prepare SQL query to INSERT records into the database.
        if traffic_type == TX_IN:
            sql = INSERT_CLAUSE.format(tb=table, c1=IP_ADDR_COL, c2=IN_PKT_COL, c3=IN_BYTES_COL, v1=item[IP_ADDR_IDX],
                                       v2=item[PACKETS_IDX], v3=item[BYTES_IDX])

        elif traffic_type == TX_OUT:
            sql = INSERT_CLAUSE.format(tb=table, c1=IP_ADDR_COL, c2=OUT_PKT_COL, c3=OUT_BYTES_COL, v1=item[IP_ADDR_IDX],
                                       v2=item[PACKETS_IDX], v3=item[BYTES_IDX])

        try:
            # Execute the SQL command
            cursor.execute(sql)

        except Exception as err:
            # Rollback in case there is any error
            conn.rollback()
            logging.error("Exception:", err)

        # disconnect from server
        conn.close()

    except Exception as err:
        logging.error("Exception:", err)


# Main code 
if __name__ == "__main__":

    logging.basicConfig(filename=GX_LOG_FILE_PATH, format='[ %(asctime)s ] [ %(levelname)s ]  %(message)s ',
                        level=logging.DEBUG, datefmt='%a, %d %b %Y %H:%M:%S')

    # Get all BGP routes
    bgp_subnets = get_routes_from_db(DB_SUBNET_TABLE, SUBNET_COL)

    # Process subnets one by one
    for subnet in bgp_subnets:

        # Get all IP addresses which belong to a subnet
        ip_addr_list = get_ip_from_subnet(subnet)

        for ip in ip_addr_list:
            inbound = get_acct_records_from_db(DB_IN_TABLE, IP_DST_COL, ip)
            outbound = get_acct_records_from_db(DB_OUT_TABLE, IP_SRC_COL, ip)

            if inbound:
                insert_records_to_db(DB_CALL_STAT_TABLE, TX_IN, inbound[TUP_ELEM_IDX])

            if outbound:
                insert_records_to_db(DB_CALL_STAT_TABLE, TX_OUT, outbound[TUP_ELEM_IDX])
