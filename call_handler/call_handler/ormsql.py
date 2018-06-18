#!/usr/bin/env python3
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, select
from configparser import SafeConfigParser
import os
import sys


CONF_FILE = 'conf/gx_config.ini'
ABS_PATH = os.path.split(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE_PATH = os.path.join(ABS_PATH[0], CONF_FILE)

CHAR_PLUS = '+'
CHAR_COLON = ':'
CHAR_AT = '@'
CHAR_SLASH = '/'
STR_DELIM = ' | '
CHAR_LF = '\n'

DB_SECTION = "db"
DB_DRIVER_KEY = "db_driver"
DB_DIALECT_KEY = "db_dialect"
DB_HOST_KEY = "db_host"
DB_PORT_KEY = "db_port"
DB_USER_KEY = "db_username"
DB_PASS_KEY = "db_password"
DB_NAME_KEY = "db_name"
DB_DEBUG_KEY = "db_debug"

DB_BGP_TABLE_KEY = "db_bgp_table"
DB_SUBNET_COL_KEY = "db_subnet_col"


class GxDatabase:
    """ Select database e.g. MySQL, SQlite, PostgreSQL """

    def __init__(self):
        """ (GxDatabase) -> NoneType
        
        Loads configuration and makes a connection to the database
        
        """
        configParser = SafeConfigParser()
        configParser.read(CONFIG_FILE_PATH)
		
		# Get all the configuration
        host = configParser.get(DB_SECTION, DB_HOST_KEY)
        driver = configParser.get(DB_SECTION, DB_DRIVER_KEY)
        dialect = configParser.get(DB_SECTION, DB_DIALECT_KEY)
        user = configParser.get(DB_SECTION, DB_USER_KEY)
        passwd = configParser.get(DB_SECTION, DB_PASS_KEY)
        db_name = configParser.get(DB_SECTION, DB_NAME_KEY)
        is_debug = configParser.getboolean(DB_SECTION, DB_DEBUG_KEY)
		
		# Make a connection to database
        connector = driver + CHAR_PLUS + dialect + "://" + user + CHAR_COLON +\
                            passwd + CHAR_AT + host + CHAR_SLASH + db_name	

        self.engine = create_engine(connector, echo=is_debug)
		
		# Todo: exception handling - sys.exit ?
        try:
            self.conn = self.engine.connect()
			
        except Exception as err:
            print("ERROR: Connection to database failed")
            sys.exit(1)
			

    def __del__(self):
	    """ (GxDatabase) -> NoneType
		
		Cleanup the connection when object is destroyed.
		
        """
        #self.conn.close()
        #pass


    def __str__(self):
        """ (GxDatabase) -> str
		
		Print out meta data.
		
        """
        table_names = self.engine.table_names()
        info = ''
		
        for item in table_names:
            metadata = MetaData() # print(repr(metadata.tables['acct_in']))
            tb_data = Table(item, metadata, autoload=True, autoload_with=self.engine) # info += ''.join(repr(acct_in)) + "\n\n"
            info += item + CHAR_COLON + ' ' + STR_DELIM.join(tb_data.columns.keys()) + CHAR_LF
			           
        return(info.rstrip())
		
		
    def execute_query(self, query):
        """ (GxDatabase, str) -> str
		
        Execute SQL statement and return the results.
		
        """
        # SQL Query : TODO How many retries
        try:
            result = self.conn.execute(query)
            return result
			
        except Exception as err:
            #sys.exit(1)
            return None
            #self.conn = self.engine.connect()
            #result = self.conn.execute(query)
	
        #return result.fetchall()
        #return result
		
	
    def insert_query(self, table, **kwargs):
        """
		
		
        """
        #metadata = MetaData(self.engine)
        #tb = Table(table, metadata, autoload=True)
        #col_data = ''
		
        #for key, value in kwargs.items():
        #    col_data += key + '=' + str(value) + ','
		
        #stmt = tb.insert().values(col_data.rstrip(','))
        
        #print(stmt)
        #result = self.conn.execute(stmt)
		
        #return result
        pass

		
    def update_query(self, table, **kwargs):
        """
		
		
        """
        pass
		
		
    def delete_query(self, table, *args):
        """
		
		
        """
        pass
		

    def select_query(self, table, *args):
        """
		
		
        """
        pass
		
		
if __name__ == "__main__":
	
    gxdb = GxDatabase()
	
    print(gxdb)
	
    result = gxdb.execute_query("SELECT * from acct_in")
    print(result[0].keys(), result)

    # Column names
    #print(result[0])
    #print(result[0].keys())
    #print(result[0].ip_dst)

    # select
    #stmt = select([acct_in])
    #res = conn.execute(stmt).fetchall()
    #print(res[0])
	
	#gxdb.insert_query('acct_in', ip_dst="25.25.25.25", packets=12, bytes=123)
	
	
