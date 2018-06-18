#!/usr/bin/env python3
import csv
import glob
import os
import ormsql
from helpers import *
from collections import defaultdict
import shutil


# CSV file path
INQ_FTOM_CSV_FILE_PATH = "/opt/gx/inqueue/ftom/"
INQ_MTOF_CSV_FILE_PATH = "/opt/gx/inqueue/mtof/"

PROC_FTOM_CSV_FILE_PATH = "/opt/gx/processed/ftom/"
PROC_MTOF_CSV_FILE_PATH = "/opt/gx/processed/mtof/"

INSERT_CLAUSE = "INSERT INTO {tb} ({c1}, {c2}, {c3}) VALUES ('{v1}', {v2}, {v3}) ON DUPLICATE KEY UPDATE {c2}=VALUES({c2}) + {v2}, {c3}=VALUES({c3}) + {v3};"


# Find oldest file
def get_oldest_csv_file(dirpath):
	""" (str) -> str
	
	Find oldest file by comparing timestamp from a given directory.
	
	"""
	list_of_files = glob.glob(dirpath + '*')  # You may use iglob in Python3

	if not list_of_files:
		return None
    
	oldest_file = min(list_of_files, key=os.path.getctime)
    
	return oldest_file
	

# Read and parse csv file
def get_acct_data_from_csv(csvfile, ip_col_name):
	""" (str) ->
	
	Parse accounting data from csv file.
	
	"""
	# Open csv file for processing
	with open(csvfile) as f:
		reader = csv.DictReader(f, delimiter=CHAR_COMMA)
		
		pkt_cnt = defaultdict(int)
		byte_cnt = defaultdict(int)

		# Sum up all packet and byte counters
		for row in reader:
			pkt_cnt[row[ip_col_name]] += int(row[PKT_COL])
			byte_cnt[row[ip_col_name]] += int(row[BYTE_COL])
	
		merge = defaultdict(list)
		
		# Merge the dictionaries based on unique IP address value
		for d in (pkt_cnt, byte_cnt):
			for key, value in d.items():
				merge[key].append(value)
		
		return (merge)
		

# Insert the data in call_stats table of database
def insert_data_into_db(acct_data, pkt_col, byte_col):
	""" (defaultdict) ->
	
	Insert accounting data in to the call_stats database table.
	
	"""
	gxdb = ormsql.GxDatabase()
	
	for ip, counters in acct_data.items():
		sql = INSERT_CLAUSE.format(tb=DB_CALL_STAT_TABLE, c1=IP_ADDR_COL, c2=pkt_col, c3=byte_col, \
										v1=ip, v2=counters[0], v3=counters[1])
	
		result = gxdb.execute_query(sql)
    

# Move file to processed directory
def move_csv_from_inqueue(srcfilepath, destpath):
	""" (str, str) -> NoneType
	
	Move the files to a new location.
	
	"""
	try:
		os.makedirs(destpath)
	except OSError:
		pass
	
	destfilepath = os.path.join(destpath, os.path.basename(srcfilepath))
	shutil.move(srcfilepath, destfilepath)


# Main code
if __name__ == "__main__":

	csvftom = get_oldest_csv_file(INQ_FTOM_CSV_FILE_PATH)	
	ftom_acct_data = get_acct_data_from_csv(get_oldest_csv_file(csvftom), IP_SRC_COL)
	insert_data_into_db(ftom_acct_data, IN_PKT_COL, IN_BYTES_COL)
	
	#move_csv_from_inqueue(csvftom, PROC_FTOM_CSV_FILE_PATH)
	

	