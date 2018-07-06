#!/usr/bin/env python

'''

'''

import os
import sys
import re
import sqlite3 as sql
from astropy.table import Table

tablefile = sys.argv[1]
tabformats = {"txt": "ascii",
           "fits": "fits",
           "csv": "csv"}
data = Table.read(tablefile, format=tabformats[re.split("\.", tablefile)[-1]])

racol = ""
deccol = ""
maincol = ""

for column in data.colnames:
    if racol=="" and ("RA" in column or "ra" in column):
        racol = column
        continue
    if deccol=="" and ("DE" in column or "De" in column or "de" in column):
        deccol = column
        continue
    if maincol=="":
        maincol = column

print("Best guess for columns:")
print("Main ID: "+maincol)
print("Right Ascension: "+racol)
print("Declination: "+deccol)

if min([len(racol),len(deccol),len(maincol)])>0:
    answer = input("Accept Y/N?")
    if answer not in "Yy":
        racol=""
        deccol=""
        maincol=""

if maincol=="":
    maincol = input("Main ID column name?")

if racol=="":
    racol = input("Right Ascension column name?")

if deccol=="":
    deccol = input("Declination column name?")

'''
  Construct field names and types
'''
ucds = {}
for colname in data.colnames:
    if colname==maincol:
        ucds[colname]="ID_MAIN"
        continue
    if colname==racol:
        ucds[colname]="POS_EQ_RA_MAIN"
        continue
    if colname==deccol:
        ucds[colname]="POS_EQ_DEC_MAIN"
        continue
    ucds[colname] = ""

collist = ""
pytypes = {}
for colname in data.colnames:
    typename = data.dtype[colname].str
    pytypes[colname] = typename
    if "i" in typename:
        collist += colname+" INT, "
        continue
    if "U" in typename:
        collist += colname+" VARCHAR(200), "
        continue
    if "f" in typename:
        collist += colname+" REAL, "
collist = collist[:-2]

'''
   Build the database using SQLite
'''
dbname = tablefile[:-4]+".db"
os.remove(dbname)
print("Writing to {}...".format(dbname))
dbconnection = sql.connect(dbname)
curs = dbconnection.cursor()

curs.execute("create table if not exists ucdTab(\
              Colname varchar(50),\
              UCD varchar(50),\
              PyType varchar(50))")
for colname in ucds:
    print(colname)
    curs.execute("insert into ucdTab (Colname, UCD, PyType) \
                  values ('{}', '{}', '{}')".format(colname, ucds[colname], pytypes[colname]))
dbconnection.commit()

curs.execute("create table if not exists\
              dataTab({})".format(collist))
for row in data:
    vals = ""
    track = 0
    for colname in data.colnames:
        if 'U' in data.dtype[colname].str:
            vals += "'{}', ".format(row[colname])
        else:
            vals += "{}, ".format(row[colname])
    curs.execute("insert into dataTab values\
                  ({})".format(vals[:-2]))
dbconnection.commit()
