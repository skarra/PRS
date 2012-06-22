##
## Created       : Mon May 14 18:10:41 IST 2012
## Last Modified : Fri Jun 22 22:03:37 IST 2012
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

import os, sys, webbrowser
from   datetime import datetime

DIR_PATH    = os.path.abspath('')
EXTRA_PATHS = [os.path.join(DIR_PATH, 'src'),
               os.path.join(DIR_PATH, 'libs'),
               os.path.join(DIR_PATH, 'libs/tornado')]

sys.path = EXTRA_PATHS + sys.path

import   tornado.ioloop, tornado.web, tornado.options
import   models, config

static_path = os.path.join(DIR_PATH, 'static')
config_file = os.path.join(DIR_PATH, 'config.json')
config      = config.Config(config_file)

settings = {'debug': True, 
            'static_path': os.path.join(DIR_PATH, 'static')}

class SearchHandler(tornado.web.RequestHandler):
    def search (self, role, field, value):
        if role == 'patient':
            model = models.Patient
            template = 'pat_srp.html'
        elif role == 'doctor':
            model = models.Doctor
            template = 'doc_srp.html'
        else:
            print 'SearchHandler:search: Invalid role: %s' % role
            return

        query = session().query(model)
        total_cnt = query.count()

        if value != 'all':
            if field == 'name':
                query = query.filter(model.name.like('%%%s%%' % value))
            elif field == 'id':
                query = query.filter(model.id == value)

        qstr = 'Field: "%6s" Value: "%s"' % (field, value)
        match_cnt = query.count()

        self.render(template, title=config.get_title(), search_query=qstr,
                    search_results=query.order_by(model.id), total_cnt=total_cnt,
                    match_cnt=match_cnt)

    def get (self, role):
        """role is one of 'patient' or 'doctor', field will be one of Name or
        ID (for now). value is the value to lookup for the field in the
        database"""

        print 'SearchHandler.get()...'

        name = self.get_argument('name', self.get_argument('named', None))
        id   = self.get_argument('id', self.get_argument('idd', None))

        if id:
            field = 'id'
            value = id
        else:
            field = 'name'
            value = name

        if role in ['patient', 'doctor']:
            return self.search(role, field, value)
        else:
            self.redirect('/')

class ViewHandler (tornado.web.RequestHandler):
    """once search is done, this handler will serve up a page with all the
    details."""

    def view_doctor (self, field, value):
        q = session().query(models.Doctor)
        if field == 'name':
            rec = q.filter_by(name = value).first()
        elif field == 'id':
            rec = q.filter_by(id = value).first()
        else:
            logging.error('ViewHandler:view_doctor: Unknown field type (%s)',
                          field)
            self.redirect('/')

        self.render('doctor.html', title=config.get_title(), name="Goofy",
                    rec=rec)

    def view_patient (self, field, value):
        q = session().query(models.Patient)
        if field == 'name':
            rec = q.filter_by(name = value).first()
        elif field == 'id':
            rec = q.filter_by(id = value).first()
        else:
            logging.error('ViewHandler:view_patient: Unknown field type (%s)',
                          field)
            self.redirect('/')

        self.render('patient.html', title=config.get_title(), name="Goofy",
                    rec=rec, d=session().query(models.Doctor))

    def get (self, role, field, value):
        """role is one of 'patient' or 'doctor', field will be one of Name or
        ID (for now). value is the value to lookup for the field in the database"""

        if role == 'patient':
            return self.view_patient(field, value)
        elif role == 'doctor':
            return self.view_doctor(field, value)
        else:
            self.redirect('/')

class NewPatientHandler(tornado.web.RequestHandler):
    def post (self):
        print 'Got the post, buddy.'

        ga = self.get_argument
        gender = ga('new_gender', 'Male')
        title  = 'Mr.' if gender == 'Male' else 'Ms.'
        session().add(models.Patient(name=ga("new_name", ''),
                                     title=title, gender=gender,
                                     age=ga("new_age", 0),
                                     regdate=ga("new_regdate", datetime.now()),
                                     phone=ga('new_phone', ''),
                                     address=ga('new_addr', ''),
                                     occupation=ga('new_occup', ''),
                                     relative=ga('new_relname', ''),
                                     relative_relation=ga('new_relrel', ''),
                                     relative_phone=ga('new_relph', ''),
                                     reg_fee=ga('new_rfee', 0)
                                     ))
        session().commit()
        self.redirect('/')

    def get (self):
        self.render('new-patient.html', title=config.get_title())

class MainHandler(tornado.web.RequestHandler):
    def get (self):
        self.render('index.html', title=config.get_title())

def engine (val=None):
    global _engine
    if val:
        _engine = val
    else:
        return _engine

def session (val=None):
    global _session
    if val:
        _session = val
    else:
        return _session

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/newpatient", NewPatientHandler),
    (r"/view/(.*)/(.*)/(.*)", ViewHandler),
    (r"/search/(.*)", SearchHandler),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': static_path})
], debug=True, template_path=os.path.join(DIR_PATH, 'templates'))

if __name__ == "__main__":
    tornado.options.parse_command_line()

    eng, sess= models.setup_tables('db/sample.db')
    engine(eng)
    session(sess)
    
    application.listen(8888)
    ##    webbrowser.open('localhost:8888', new=2)
    tornado.ioloop.IOLoop.instance().start()
