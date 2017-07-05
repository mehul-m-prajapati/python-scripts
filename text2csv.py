#!/usr/bin/python
import sys
import re
import csv
import os

# Column name of csv file
csvfile = 'sample.csv'
with open(csvfile, 'a') as f:
    writer = csv.writer(f)
    writer.writerow(['Attribute Name', 'Value', 'Description'])
    f.close()

# text files
avp_file_1 = str(sys.argv[1])
avp_file_2 = str(sys.argv[2])

# AVP desc file
avp_desc_file = 'Attribute Descriptions.csv'


# Read avp-value from txt file
def read_avp(filename):
    # open txt file in read mode
    avp_file = open(filename, "r")
    # Parse the file
    for line in avp_file:
        line = line.rstrip()    # Remove \r\n
        # find the avp pattern
        pattern = re.search('=', line)

        # parse the line which matches the pattern
        if pattern:
            # Get attribute and value
            attr = line[:pattern.start()].strip(' ')
            val = line[pattern.start()+1:].strip(' ')

            # pattern found. Now ignore line with starting '(' char
            if 0 == attr.find('('):
                continue

            # Export it to csv
            with open(csvfile, 'a') as f:
                writer = csv.writer(f)      # dialect='excel'
                writer.writerow([attr, val])
                f.close()

    avp_file.close()


# Find description from csv
def find_desc(attr, descfile):
    with open(descfile, 'r') as f:
        # Read csv
        reader = csv.reader(f, delimiter=',')

        # Read every row
        for row in reader:
            if row:
                # Replace unicode to ascii
                csvAttr = row[1].replace("\xc2\xa0", " ")
                attr = attr.replace("\xc2\xa0", " ")
                # Replace special pattern
                attr = attr.replace("( ", "(")
                attr = attr.replace(" )", ")")
                # Match attribute with description
                if ((csvAttr.lower() in attr.lower()) or
                        (attr.lower() in csvAttr.lower()) or
                        (attr.lower() == csvAttr.lower())):
                    f.close()
                    # Return desc val
                    desc_val = row[2]
                    return desc_val

# Parse txt file and export to csv
read_avp(avp_file_1)
read_avp(avp_file_2)

# Add description to form final csv
with open(csvfile, 'r') as f:
    reader = csv.reader(f, delimiter=',')
    # Read the rows
    for row in reader:
        # Search
        attr_name = row[0]
        descrip = find_desc(attr_name, avp_desc_file)

        if descrip:
            descrip = descrip.replace("\xc2\xa0", " ")
            row.append(descrip)
        # Write to new csv file
        newcsvfile = 'new-avp.csv'
        with open(newcsvfile, 'a') as f:
                writer = csv.writer(f)
                writer.writerow(row)
                f.close()
    f.close()

# Rename / delete old csv
os.rename(newcsvfile, csvfile)
