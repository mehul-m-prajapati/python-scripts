#!/usr/bin/env python

import os
import glob

path = 'data'
os.chdir(path)
files = sorted(os.listdir(os.getcwd()), key=os.path.getmtime)

oldest = files[0]
newest = files[-1]

print "Oldest:", oldest
print "Newest:", newest
print "All by modified oldest to newest:", files

# Method 2
def get_latest_file(path, *paths):
    """
    Returns the name of the latest (most recent) file of the joined path(s)
    
    """
    fullpath = os.path.join(path, *paths)
    list_of_files = glob.glob(fullpath)  # You may use iglob in Python3
    
    if not list_of_files:                # I prefer using the negation
        return None                      # because it behaves like a shortcut
        
    latest_file = max(list_of_files, key=os.path.getctime)
    _, filename = os.path.split(latest_file)
    
    return filename
