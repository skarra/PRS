##
## Created       : Mon May 14 18:10:41 IST 2012
## Last Modified : Mon May 14 19:05:28 IST 2012
##
## Copyright (C) 2012 Sriram Karra <karra.etc@gmail.com>
##
## This file is part of PRS
##
## PRS is free software: you can redistribute it and/or modify it under
## the terms of the GNU Affero General Public License as published by the
## Free Software Foundation, version 3 of the License
##
## PRS is distributed in the hope that it will be useful, but WITHOUT
## ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
## FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
## License for more details.
##
## You should have a copy of the license in the doc/ directory of PRS.  If
## not, see <http://www.gnu.org/licenses/>.

## First up we need to fix the sys.path before we can even import stuff we
## want.

import os, sys

DIR_PATH    = os.path.abspath('')
EXTRA_PATHS = [os.path.join(DIR_PATH, 'libs'),
               os.path.join(DIR_PATH, 'libs/tornado')]
sys.path = EXTRA_PATHS + sys.path

import tornado.ioloop
import tornado.web

static_path = os.path.join(DIR_PATH, 'static')

settings = {'debug': True, 
            'static_path': os.path.join(__file__, 'static')}

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('templates/prs.html')

application = tornado.web.Application([
    (r"/", MainHandler),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': static_path})
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
