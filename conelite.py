#!/usr/bin/env python

import tornado.web
import tornado.ioloop
import sys

dbfile = sys.argv[1]
if len(sys.argv)>2:
    portnumber = int(sys.argv[2])
else:
    portnumber = 80

class ConeSearchHandler(tornado.web.RequestHandler):
    def get(self):
        get_vars = self.request.arguments
        print(get_vars)
        ra = -1
        dec = -1
        radius = -1
        if 'RA' in get_vars:
            ra = float(get_vars['RA'])
        if 'DEC' in get_vars:
            dec = float(get_vars['DEC'])
        if 'SR' in get_vars:
            radius = float(get_vars['SR'])
        if min([ra,dec,radius])==-1:
            print("ERROR: Incorrect request")
            return

class App(tornado.web.Application):
    def __init__(self):
        handlers = [(r"/", ConeSearchHandler)]
        tornado.web.Application.__init__(self, handlers)

appinstance = App()
appinstance.listen(portnumber)
ioloophandle = tornado.ioloop.IOLoop.current()
ioloophandle.start()
