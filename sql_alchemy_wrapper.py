#!/usr/bin/env python3
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, select
from configparser import SafeConfigParser
import os

CONF_FILE = 'conf/my_config.ini'
ABS_PATH = os.path.split(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE_PATH = os.path.join(ABS_PATH[0], CONF_FILE)

DB_SECTION = "db"
DB_DRIVER_KEY = "db_driver"
DB_DIALECT_KEY = "db_dialect"
DB_HOST_KEY = "db_host"
DB_PORT_KEY = "db_port"
DB_USER_KEY = "db_username"
DB_PASS_KEY = "db_password"
DB_NAME_KEY = "db_name"
DB_DEBUG_KEY = "db_debug"

CHAR_PLUS = '+'
CHAR_COLON = ':'
CHAR_AT = '@'
CHAR_SLASH = '/'
STR_DELIM = ' | '
CHAR_LF = '\n'


class MyDatabase:
    """ Select database e.g. MySQL, SQlite, PostgreSQL """

    def __init__(self):
        """ (MyDatabase) -> NoneType
        
        Loads configuration and makes a connection to the database
        
        """
        configParser = SafeConfigParser()
        configParser.read(CONFIG_FILE_PATH)
		
        host = configParser.get(DB_SECTION, DB_HOST_KEY)
        driver = configParser.get(DB_SECTION, DB_DRIVER_KEY)
        dialect = configParser.get(DB_SECTION, DB_DIALECT_KEY)
        user = configParser.get(DB_SECTION, DB_USER_KEY)
        passwd = configParser.get(DB_SECTION, DB_PASS_KEY)
        db_name = configParser.get(DB_SECTION, DB_NAME_KEY)
        is_debug = configParser.getboolean(DB_SECTION, DB_DEBUG_KEY)
		
	# Make a connection to database
        #connector = driver + "+" + dialect + "://" + user + ":" + passwd + "@" + host + "/" + db_name	
        connector = driver + CHAR_PLUS + dialect + "://" + user + CHAR_COLON + passwd + CHAR_AT + host + CHAR_SLASH + db_name
        self.engine = create_engine(connector, echo=is_debug) # echo=True for debugging
        self.conn = self.engine.connect()

		
    def __str__(self):
        """ (MyDatabase) -> str
		
		Print out meta data.
		
        """
        table = self.engine.table_names()
        info = ''
		
        for item in table:
            metadata = MetaData() # print(repr(metadata.tables['acct_in']))
            tb_data = Table(item, metadata, autoload=True, autoload_with=self.engine) # info += ''.join(repr(acct_in)) + "\n\n"
            
            info += item + ': ' + ', '.join(tb_data.columns.keys()) + "\n\n"
			           
		
        return(info.rstrip())

            # Column names
            #return(acct_in.columns.keys())
		
		
    def __del__(self):
	    """ (GxDatabase) -> NoneType
		
		Cleanup the connection when object is destroyed.
		
        """
        #self.conn.close()
        #pass
	
	
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

		
    def execute_query(self, query):
        """ (MyDatabase, str) -> str
		
        Execute SQL statement and return the results.
		
        """
        # SQL Query
        result_obj = self.conn.execute(query)
        result = result_obj.fetchall()
	
        return result
		
		
if __name__ == "__main__":
	
	mydb = MyDatabase()
	
	#print(mydb)
	
	res = mydb.execute_query("DESCRIBE acct_in")
	print(res[0].keys(), res)
	
    #res = mydb.execute_query("DESCRIBE acct_in")
    #print(res)
    # Column names
    #print(result[0])
    #print(result[0].keys())
    #print(result[0].ip_dst)

    # select
    #stmt = select([acct_in])
    #res = conn.execute(stmt).fetchall()
    #print(res[0])
    #mydb.insert_query('acct_in', ip_dst="25.25.25.25", packets=12, bytes=123)
