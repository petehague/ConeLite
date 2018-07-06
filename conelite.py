#!/usr/bin/env python

import tornado.web
import tornado.ioloop
import sys
import sqlite3 as sql
from astropy.table import Table
import astropy.io.votable as votable
from io import StringIO

dbfile = sys.argv[1]
if len(sys.argv)>2:
    portnumber = int(sys.argv[2])
else:
    portnumber = 80

rafield = ""
decfield = ""
raindex = -1
decindex = -1

dbconnection = sql.connect(dbfile)
curs = dbconnection.cursor()
curs.execute("select * from ucdTab")
track = 0
for row in curs:
    if row[1]=="POS_EQ_RA_MAIN":
        rafield = row[0]
        raindex = track
    if row[1]=="POS_EQ_DEC_MAIN":
        decfield = row[0]
        decindex = track
    track += 1

def conesearch(ra, dec, sr):
    global rafield, decfield, dbconnection
    query = "select * from dataTab "
    query += ("where (({0}>=({2}-{4}) and {0}<=({2}+{4})) or "
              "({0}-360>=({2}-{4}) and {0}-360<=({2}+{4}))) and "
              "{1}>=({3}-{4}) and {1}<=({3}+{4}) ").format(rafield,
                                                         decfield,
                                                         ra, dec,
                                                         sr)
    curs = dbconnection.cursor()
    curs.execute(query)
    srsq = sr*sr
    for row in curs:
        radist = ra-row[raindex]
        decdist = dec-row[decindex]
        if radist*radist+decdist*decdist<=sr:
            yield row

def newtable():
    global dbconnection
    query = "select Colname,PyType from ucdTab"
    curs = dbconnection.cursor()
    curs.execute(query)
    colnames = []
    typenames = []
    for row in curs:
        colnames.append(row[0])
        typenames.append(row[1])
    return Table(names=colnames, dtype=typenames)

class ConeSearchHandler(tornado.web.RequestHandler):
    def get(self):
        get_vars = self.request.arguments
        ra = -1
        dec = -1
        radius = -1
        if 'RA' in get_vars:
            ra = float(get_vars['RA'][0])
        if 'DEC' in get_vars:
            dec = float(get_vars['DEC'][0])
        if 'SR' in get_vars:
            radius = float(get_vars['SR'][0])
        if min([ra,dec,radius])==-1:
            print("ERROR: Incorrect request")
            return
        result = newtable()
        for row in conesearch(ra, dec, radius):
            result.add_row(row)
        vo_out = votable.from_table(result)
        # Should not have to do this! Bad API for votable!
        vo_out.to_xml("tempfile.xml")
        outstring = ""
        with open("tempfile.xml","r") as vofile:
            for line in vofile:
                outstring+=line
        self.write(outstring)

class App(tornado.web.Application):
    def __init__(self):
        handlers = [(r"/", ConeSearchHandler)]
        tornado.web.Application.__init__(self, handlers)

appinstance = App()
appinstance.listen(portnumber)
ioloophandle = tornado.ioloop.IOLoop.current()
ioloophandle.start()
