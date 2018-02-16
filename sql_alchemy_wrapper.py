#!/usr/bin/env python3
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, select
from configparser import SafeConfigParser
import os

CONF_FILE = 'conf/config.ini'
ABS_PATH = os.path.split(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE_PATH = os.path.join(ABS_PATH[0], CONF_FILE)


class MyDatabase:
    """ Select database e.g. MySQL, SQlite, PostgreSQL """

    def __init__(self):
        """
        
        Loads configuration and makes a connection to the database
        
        """
        configParser = SafeConfigParser()
        configParser.read(CONFIG_FILE_PATH)



if __name__ == "__main__":
	
    engine = create_engine("mysql+pymysql://root:tmfsr82@localhost/pmacct", echo=False) # echo=True for debugging
    conn = engine.connect()
    print(engine.table_names())

    metadata = MetaData()
    acct_in = Table('some_in', metadata, autoload=True, autoload_with=engine)

    # full meta data
    print(repr(acct_in))

    # Column names
    print(some_in.columns.keys())
    print(repr(metadata.tables['some_in']))

    # SQL Query
    result_p = conn.execute("SELECT * from some_in")
    result = result_p.fetchall()

    # Column names
    print(result[0])
    result[0].keys()
    result[0].ip_dst

    # select
    stmt = select([some_in])
    res = conn.execute(stmt).fetchall()
