## -*- python -*-
##
## Created       : Mon May 14 18:10:41 IST 2012
## Last Modified : Fri Feb 08 23:38:05 PST 2019
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
## You should have a copy of the license in the base directory of PRS.  If
## not, see <http://www.gnu.org/licenses/>.

## First up we need to fix the sys.path before we can even import stuff we
## want.

import copy, httplib, logging, os, re, socket, string, sys, urllib, webbrowser
from   datetime  import datetime, date
from   threading import Thread

## Some Global Variables to get started
prs_ver = 'v0.23'

DIR_PATH    = os.path.abspath('')
EXTRA_PATHS = [os.path.join(DIR_PATH, 'src'),
               os.path.join(DIR_PATH, 'libs'),
               os.path.join(DIR_PATH, 'libs/tornado')]

sys.path = EXTRA_PATHS + sys.path

import   tornado.ioloop, tornado.web, tornado.options
import   models, config
from     models     import days    as days
from     models     import shiftns as shiftns
from     sqlalchemy import and_
from     sqlalchemy.types import Date
from     sqlalchemy.ext.serializer import loads, dumps

static_path = os.path.join(DIR_PATH, 'static')
config_file = os.path.join(DIR_PATH, 'config.json')
config      = config.Config(config_file)

settings = {'debug': True,
            'static_path': os.path.join(DIR_PATH, 'static')}

def auto_ver (resource):
    """Intended to be invoked from inside tornado templates, given a resource
    names such as /static/ctl.js this will return something like
    /static/ctl.css?v=201211010141551 to version it."""

    absname   = os.path.abspath(resource[1:])
    d         = datetime.fromtimestamp(os.path.getmtime(absname))
    timestamp = d.strftime("%Y%m%d%H%M%S")

    res = re.match('(.*\.)([a-zA-Z]*$)', resource)
    return ''.join([resource, '?v=', timestamp])


def db_env ():
    return models.db_env()

def env_name (inpdb=None):
    return models.env_name(inpdb)

def is_production (env):
    return models.is_production(env)

def is_demo (env):
    return models.is_demo(env)

def toggle_env ():
    models.toggle_env()

def session (env=None):
    return models.session(env)

class BaseHandler(tornado.web.RequestHandler):
    """Generates an error response with status_code for all requests."""

    base_kwargs = {
        'auto_ver' : auto_ver,
        'title' : config.get_title(),
        }

    ## FIXME: For reasons beyond my understanding the write_error method needs
    ## to be here as well in order to catch some 500s. Without this method
    ## here, a 404 is properly handled by the ErrorHandler class. It's quite
    ## frustrating not to understand what's really goign on, but life is short
    ## and one has to move on.
    def write_error (self, status_code, **kwargs):
        if status_code in [403, 404, 500, 503]:
            filename = '%d.html' % status_code
            self.render(filename, **self.base_kwargs)
        else:
            self.write("<html><title>%(code)d: %(message)s</title>" \
            "<body class='bodyErrorPage'>%(code)d: %(message)s</body>"\
            "</html>" % {
                "code": status_code,
                "auto_ver" : auto_ver,
                "message": httplib.responses[status_code],
            })

class ErrorHandler(tornado.web.RequestHandler):
    """Generates an error response with status_code for all requests."""
    def __init__ (self, application, request, status_code):
        tornado.web.RequestHandler.__init__(self, application, request)
        self.base_kwargs = {
            'auto_ver' : auto_ver,
            'title' : config.get_title(),
            }
        self.set_status(status_code)

    def write_error (self, status_code, **kwargs):
        if status_code in [403, 404, 500, 503]:
            filename = '%d.html' % status_code
            self.render(filename, **self.base_kwargs)
        else:
            self.write("<html><title>%(code)d: %(message)s</title>" \
            "<body class='bodyErrorPage'>%(code)d: %(message)s</body>"\
            "</html>" % {
                "code": status_code,
                "auto_ver" : auto_ver,
                "message": httplib.responses[status_code],
            })

    def prepare (self):
        raise tornado.web.HTTPError(self._status_code)

class BackupHandler(BaseHandler):
    def create (self):
        logging.info('BackupHandler:create()... Starting backup')
        basedir = self.get_argument('basedir', None)
        bupdir  = self.get_argument('bupdir',  None)
        bupdb   = self.get_argument('bupdb',   db_env())

        if not basedir:
            basedir = get_backups_basedir()
        else:
            ## FIXME: We may have to url-decode the string here
            logging.debug('BackupHandler.create(): basedir: %s', basedir)
            pass

        if not bupdir:
            bupdir = gen_backup_instance_name()
        else:
            ## FIXME: We may have to url-decode the string here
            logging.debug('BackupHandler.create(): bupdir: %s', bupdir)
            pass

        d = os.path.join(basedir, env_name(bupdb), bupdir)
        if not os.path.exists(d):
            logging.info('Backups directory %s not there. Creating...', d)
            os.makedirs(d)

        tables = models.tables()
        for table in tables:
            q = session(env=bupdb).query(table)
            serialized_data = dumps(q.all())
            fn = os.path.join(d, table.__tablename__)
            logging.debug('** Filename : %s ****************', fn)
            with open(fn, "w+b") as f:
                f.write(serialized_data)

        logging.info('BackupHandler:create()... Completed backup')

    def get (self, op=None):
        if op == 'create':
            self.create()
        elif op == 'restore':
            self.restore()

        self.render('backups.html', **self.base_kwargs)

class StatsHandler(BaseHandler):
    def get (self, what, by='doctor'):
        inp_from = self.get_argument('vs_from', models.MyT.today_uk())
        inp_to   = self.get_argument('vs_to',   models.MyT.today_uk())

        if what == 'visits':
            if by =='doctor':
                self.get_visits_doc(inp_from, inp_to)
            elif by == 'department':
                self.get_visits_dept(inp_from, inp_to)
            else:
                logging.error('StatsHandler:get(): Unknown "by": %s', by)
                self.get_visits_doc(inp_from, inp_to)
        else:
            logging.error('StatsHandler:get(): Unknown "what": %s', what)
            self.get_visits_doc(inp_from, inp_to)

        ## The following code is commented out and left here for future
        ## reference. It enables the filtering out of visits that pertain to a
        ## specified department or doctor. This feature may be provided in the
        ## future. For now we will only provide summary statistics by
        ## department and doctor.

        # docid  = self.get_argument('vs_doc_list',  'All')
        # deptid = self.get_argument('vs_dept_list', 'All')

        # visits = session().query(models.Consultation)
        # if docid == 'All':
        #     if deptid != 'All':
        #         visits = visits.filter_by(dept_id=deptid)
        # else:
        #     visits = visits.filter_by(doctor_id=docid)
        #     if deptid != 'All':
        #         visits = visits.filter_by(dept_id=deptid)

        # depts = models.Department.sorted_dept_names_with_id(session)
        # docs  = models.Doctor.sorted_doc_names_with_id(session)
        # self.render('visit_stats.html', title=config.get_title(),
        #             depts=depts, docs=docs, show=True, visits=visits)

    def get_visits_doc (self, inp_from, inp_to):
        from_d = models.MyT.date_from_uk(inp_from)
        to_d   = models.MyT.date_from_uk(inp_to)

        from_d = from_d.strftime("%Y-%m-%d")
        to_d   = to_d.strftime("%Y-%m-%d")

        visits = session().query(models.Consultation)
        visits = visits.filter(and_(models.Consultation.date >= from_d,
                                    models.Consultation.date <= to_d))

        docsu = {}
        for visit in visits:
            if visit.first_doc_visit:
                new_incr   = 1
                new_charge = visit.charge
                old_incr   = 0
                old_charge = 0
            else:
                new_incr   = 0
                new_charge = 0
                old_incr   = 1
                old_charge = visit.charge

            if visit.doctor_id in docsu:
                val = docsu[visit.doctor_id]
                val['patcnt_old'] += old_incr
                val['patcnt_new'] += new_incr
                val['fee_old']    += old_charge
                val['fee_new']    += new_charge
                val['fee_total']  += visit.charge
                docsu.update({visit.doctor_id : val})
            else:
                docsu.update({visit.doctor_id : {
                    'doc'  : models.Doctor.find_by_id(session,
                                                      visit.doctor_id),
                    'patcnt_old' : old_incr,
                    'fee_old'    : old_charge,
                    'fee_new'    : new_charge,
                    'patcnt_new' : new_incr,
                    'fee_total'  : visit.charge,}
                    })

        summary = {'doc'  : docsu,
                   'from' : inp_from,
                   'to'   : inp_to}

        docs  = models.Doctor.sorted_doc_names_with_id(session)
        self.render('stats_visits_doctor.html', docs=docs, by='Doctor',
                    summary=summary, **self.base_kwargs)

    def get_visits_dept (self, inp_from, inp_to):
        from_d = models.MyT.date_from_uk(inp_from)
        to_d   = models.MyT.date_from_uk(inp_to)

        from_d = from_d.strftime("%Y-%m-%d")
        to_d   = to_d.strftime("%Y-%m-%d")

        visits = session().query(models.Consultation)
        visits = visits.filter(and_(models.Consultation.date >= from_d,
                                    models.Consultation.date <= to_d))

        depsu = {}
        for visit in visits:
            if visit.first_doc_visit:
                new_incr   = 1
                new_charge = visit.charge
                old_incr   = 0
                old_charge = 0
            else:
                new_incr   = 0
                new_charge = 0
                old_incr   = 1
                old_charge = visit.charge

            try:
                dep = depsu[visit.dept_id]
                dep['patcnt_new'] += new_incr
                dep['patcnt_old'] += old_incr
                dep['fee_old']    += old_charge
                dep['fee_new']    += new_charge
                dep['fee_total']  += visit.charge
            except KeyError, e:
                # It's not there, so we are going to insert it first up.
                depsu[visit.dept_id] = {
                    'name' : models.Department.name_from_id(session,
                                                            visit.dept_id),
                    'patcnt_new' : new_incr,
                    'patcnt_old' : old_incr,
                    'fee_old'    : old_charge,
                    'fee_new'    : new_charge,
                    'fee_total'  : visit.charge,
                    }

        summary = {'dept' : depsu,
                   'from' : inp_from,
                   'to'   : inp_to}

        depts = models.Department.sorted_dept_names_with_id(session)
        self.render('stats_visits_department.html', depts=depts, by='Department',
                    summary=summary, **self.base_kwargs)

class MiscAdminHandler(BaseHandler):
    def edit_depts (self):
        depts = session().query(models.Department)
        self.render('department_edit.html', depts=depts, **self.base_kwargs)

    def process_old_depts (self):
        dirty = False
        depts = session().query(models.Department)

        for dept in depts:
            argn = 'dept_name_old_%d' % dept.id
            argv = self.get_argument(argn, None)
            if argv and dept.name != argv:
                dept.name = argv
                dirty = True

        return dirty

    def process_new_depts (self):
        dirty = False
        i = 1

        while True:
            argn = 'dept_name_new_%d' % i
            argv = self.get_argument(argn, None)

            if not argv:
                break

            if argv != '':
                d = models.Department(name=argv)
                session().add(d)
                dirty = True

            i += 1

        return dirty

    def save_depts (self):
        d1 = self.process_old_depts()
        d2 = self.process_new_depts()

        if d1 or d2:
            session().commit()

    def post (self):
        op = self.get_argument('misc_admin_s', None)
        if op == 'dept':
            self.save_depts()
            self.redirect('')
        else:
            self.redirect('/')

    def get (self):
        op = self.get_argument('misc_admin_s', None)

        if op == 'dept':
            self.edit_depts()
        elif op == 'mas_db':
            toggle_env()
            self.redirect('/')
        elif op == 'mas_exit':
            sys.exit(0)
        elif op == 'mas_vs':
            self.redirect('/stats/visits/doctor')
        elif op == 'mas_vl':
            logging.info('** Using PRS Version: %s', prs_ver)
            logging.info('** Schema Version: %s', models.schema_ver)
            logging.info('** %s', self.get_argument('misc_admin_params', 'N/A'))
            self.redirect('/logs#vl_bottom')
        elif op == 'mas_ba':
            self.redirect('/backup')
        else:
            self.redirect('/')

##
## All the classes that start with Ajax are ajax handler that return JSON
##

class AjaxFileTree(BaseHandler):
    def post (self):
        logging.info('Inside jqueryFileTree ajax call.')
        s1 = '<li class="directory collapsed"><a href="#" rel="%s/">%s</a></li>'
        s2 = '<li class="file ext_%s"><a href="#" rel="%s">%s</a></li>'
        try:
            r = ['<ul class="jqueryFileTree" style="display: none;">']
            d = urllib.unquote(self.get_argument('dir','/'))
    
            for f in os.listdir(d):
                ff = os.path.join(d, f)
                if os.path.isdir(ff):
                    r.append(s1 % (ff, f))
                else:
                    e=os.path.splitext(f)[1][1:] # get .ext and remove dot
                    r.append(s2 % (e, ff, f))
                r.append('</ul>')
        except Exception,e:
            logging.error('Could not load directory: %s', str(e))
    
        r.append('</ul>')
        self.write(''.join(r))


class AjaxAppState(BaseHandler):
    def get (self):
        self.write({'environment' : db_env(),
                    'environment_is_demo' : is_demo(db_env()),
                    'config' : config.get_config()})

class AjaxDepartmentsList(BaseHandler):
    def get (self):
        ret = models.Department.sorted_dept_names_with_id(session)
        self.write({'departments' : ret})

class AjaxDoctorsInDepartment(BaseHandler):
    """Return an array of (ID, Name) tuples of Doctors in the
    Department. Keeping in line with general good practise this is wrapped
    into a dictionary."""
    def get (self, field, value):
        ret   = []

        if value == 'All':
            q = session().query(models.Doctor)
            ## FIXME: Do we have to limit to only 'active' doctors based on
            ## some argument?
            ret = [(doc.id, doc.name) for doc in q]
        else:
            q = session().query(models.Department)
            if field == 'name':
                ret = models.Doctor.sorted_doc_names_with_id_in_dept_name(
                    session, value)
            elif field == 'id':
                ret = models.Doctor.sorted_doc_names_with_id_in_dept_id(
                    session, value)

        self.write({"doctors" : ret})

class AjaxPatientDetails(BaseHandler):
    """Return the details of the patient as a dictionary"""

    def get (self, patid):
        ret   = {}
        q = session().query(models.Patient)
        rec = q.filter_by(id=patid).first()

        visits = []
        for visit in rec.consultations:
            visits.append({'cid'   : visit.cid,
                           'patient_id' : visit.patient_id,
                           'doctor_id'  : visit.doctor_id,
                           'dept_id'    : visit.dept_id,
                           'date'       : ('%s' % visit.date),
                           'charge'     : visit.charge,
                           'notes'      : visit.notes,
                           })

        if rec:
            ret.update({'name'              : rec.name,
                        'age'               : rec.age,
                        'gender'            : rec.gender,
                        'regdate'           : rec.regdate.isoformat(),
                        'phone'             : rec.phone,
                        'address'           : rec.address,
                        'occupation'        : rec.occupation,
                        'reg_fee'           : rec.reg_fee,
                        'relative'          : rec.relative,
                        'relative_phone'    : rec.relative_phone,
                        'relative_relation' : rec.relative_relation,
                        'visits'            : visits,
                        })

        self.write(ret)

class AjaxDoctorDetails(BaseHandler):
    """Return the details of the doctor as a dictionary"""

    def get (self, docid):
        ret = {}
        q = session().query(models.Doctor)
        rec = q.filter_by(id=docid).first()

        if rec:
            ret.update({'name'    : rec.name,
                        'active'  : rec.active,
                        'title'   : rec.title,
                        'quals'   : rec.quals,
                        'regdate' : rec.regdate.isoformat(),
                        'phone'   : rec.phone,
                        'fee_newp': rec.fee_newp,
                        'fee_oldp': rec.fee_oldp,
                        'email'   : rec.email,
                        'address' : rec.address,
                        'avail'   : rec.get_availability(),
                        'depts'   : [d.name for d in rec.depts],
                        })

        self.write(ret)

class AjaxDocAvailability(BaseHandler):
    """FIXME: Insert complete documentation.

    Returns details of all available doctors for a given set of constraints
    including department, day and shift. Inactive doctors are not considered
    while checking availability.
    """

    def get (self):
        ret   = {}
        dept_name = self.get_argument('dept', None)
        if not dept_name:
            ## FIXME: handle error
            return
        dept_id = models.Department.id_from_name(session(), dept_name)

        pat_id = self.get_argument('patid', None)
        if not pat_id:
            ## FIXME: handle error
            return

        day    = self.get_argument('day', '-- Any --')
        shiftn = self.get_argument('shift', '-- Any --')

        dq = session().query(models.Doctor, models.Slot)
        dq = dq.filter(models.Doctor.active == True)
        dq = dq.filter(models.Doctor.depts.any(name=dept_name))
        dq = dq.filter(models.Doctor.id == models.Slot.doctor_id)
        if day != '-- Any --':
            dq = dq.filter(models.Slot.day  == day)
        if shiftn != '-- Any --':
            dq = dq.filter(models.Slot.shift == shiftn)

        ## FIXME: There is some amount of duplication with the
        ## Doctor.get_availablity() method. That method should be refactored
        ## to return what is requested.
        docs = dq.all()
        for doc, slot in docs:
            if not doc.name in ret:
                pat = models.Patient.find_by_id(session(), pat_id)
                if pat.is_first_doc_in_dept_visit(doc.id, dept_id):
                    charge = doc.fee_newp
                else:
                    charge = doc.fee_oldp

                ret[doc.name] = {
                    'id'    : doc.id,
                    'quals' : doc.quals,
                    'fee_newp' : doc.fee_newp,
                    'fee_oldp' : doc.fee_oldp,
                    'charge' : charge,
                    }
            slots = ret[doc.name]
            if not slot.day in slots:
                slots[slot.day] = {
                    'Morning'   : [],
                    'Afternoon' : [],
                    }
            slots[slot.day][slot.shift].append('%s-%s' % (slot.start_time,
                                                          slot.end_time))

        self.write({"doctors" : ret, "count" : len(ret)})

##
## Regular UI request handlers
##

class SearchHandler(BaseHandler):
    def search_dept (self, name):
        model     = models.Department
        template  = 'doc_srp.html'
        query     = session().query(model)
        total_cnt = query.count()
        query     = query.filter_by(name=name).first()
        results   = query.doctors if query else []

        qstr      = 'Field: "Dept" Value: "%s"' % name
        match_cnt = len(results)

        self.render(template, search_query=qstr, search_results=results,
                    total_cnt=total_cnt, match_cnt=match_cnt, **self.base_kwargs)

    def search (self, role, field, value):
        if role == 'patient':
            model = models.Patient
            template = 'pat_srp.html'
        elif role == 'doctor':
            if field == 'dept':
                ## This will we handle differently from the rest - jus for
                ## now. FIXME: for the ugliness quotient...
                self.search_dept(value)
                return
            else:
                model = models.Doctor
                template = 'doc_srp.html'
        else:
            logging.info('SearchHandler:search: Invalid role: %s', role)
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

        self.render(template, search_query=qstr,
                    search_results=query.order_by(model.id), total_cnt=total_cnt,
                    match_cnt=match_cnt, **self.base_kwargs)

    def get (self, role):
        """role is one of 'patient' or 'doctor', field will be one of Name or
        ID (for now). value is the value to lookup for the field in the
        database"""

        name = self.get_argument('name', self.get_argument('named', None))
        id   = self.get_argument('id', self.get_argument('idd', None))
        dept = self.get_argument('name', self.get_argument('deptd', None))

        if name:
            field = 'name'
            value = name
        elif id:
            field = 'id'
            value = id
        else:
            field = 'dept'
            value = dept

        if role in ['patient', 'doctor']:
            return self.search(role, field, value)
        else:
            self.redirect('/')

class LogsHandler(BaseHandler):
    def get (self):
        logf = open(get_logfile_name(), 'r')
        self.render('logs_view.html', logf=logf, **self.base_kwargs) 
        logf.close()

class ViewHandler(BaseHandler):
    """once search is done, this handler will serve up a page with all the
    details."""

    def view_doctor (self, field, value):
        q = session().query(models.Doctor)
        if field == 'name':
            rec = q.filter_by(name=value).first()
        elif field == 'id':
            rec = q.filter_by(id=value).first()
        else:
            logging.error('ViewHandler:view_doctor: Unknown field type (%s)',
                          field)
            self.redirect('/')

        self.render('doctor_view.html', rec=rec, days=days,
                    avail=rec.get_availability(), **self.base_kwargs)

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

        if len(rec.consultations) > 0:
            lvisit = rec.consultations[-1]
            ldoc = models.Doctor.find_by_id(session, lvisit.doctor_id)
            avail = ldoc.get_availability()
            visit_type = lvisit.visit_type()
        else:
            lvisit = None
            ldoc   = None
            avail  = None
            visit_type = None

        self.render('patient_view.html', rec=rec,
                    d=session().query(models.Doctor), session=session,
                    avail=avail, lvisit=lvisit, visit_type=visit_type,
                    days=days, shiftns=shiftns,
                    ldoc=ldoc, **self.base_kwargs)

    def get (self, role, field, value):
        """role is one of 'patient' or 'doctor', field will be one of Name or
        ID (for now). value is the value to lookup for the field in the
        database"""

        if role == 'patient':
            return self.view_patient(field, value)
        elif role == 'doctor':
            return self.view_doctor(field, value)
        else:
            logging.error('Invalid role (%s) for View operation', role)
            self.redirect('/')

class EditPatientHandler(BaseHandler):
    """Edit the patient details. The form is pre-loaded with the current
    personal details."""

    def post (self, field, value):
        q = session().query(models.Patient)
        rec = q.filter_by(id=value).first()

        ga = self.get_argument
        gender = ga('new_gender', 'Male')
        title  = 'Mr.' if gender == 'Male' else 'Ms.'
        da = ga('new_rdate', '')
        if da == '':
            da = datetime.now()
        else:
            res = re.search('(\d\d)-(\d\d)-(\d\d\d\d)', da)
            if not res:
                da = datetime.now()
            else:
                da = datetime(int(res.group(3)), int(res.group(2)),
                                  int(res.group(1)))

        ## WE do not know which fields really were changed; let's just fetch
        ## the whole damn thing and write to db
        rec.name              = ga("new_name")
        rec.title             = title
        rec.gender            = gender
        rec.age               = ga("new_age", 0)
        rec.regdate           = da
        rec.phone             = ga('new_ph', '')
        rec.address           = ga('new_addr', '')
        rec.occupation        = ga('new_occup', '')
        rec.relative          = ga('new_relname', '')
        rec.relative_relation = ga('new_relrel', '')
        rec.relative_phone    = ga('new_relph', '')
        rec.reg_fee           = ga('new_rfee', 0)

        try:
            session().commit()
            self.redirect('/view/patient/id/%d' % rec.id)
        except Exception, e:
            ## FIXME: Erorr handling to be performed
            logging.error('Exception while saving modifications for %s (%s)',
                          rec.name, e)

    def get (self, field, value):
        if field != 'id':
            logging.error('EditPatientHandler:get(): unknown field: %s', field)
            return
        q = session().query(models.Patient)
        rec = q.filter_by(id=value).first()
        self.render("patient_edit.html", rec=rec, today=models.MyT.today_uk(),
                    **self.base_kwargs)

class NewPatientHandler(BaseHandler):
    def post (self):
        ga = self.get_argument
        gender = ga('new_gender', 'Male')
        title  = 'Mr.' if gender == 'Male' else 'Ms.'
        da = ga('new_rdate', '')
        if da == '':
            da = datetime.now()
        else:
            res = re.search('(\d\d)-(\d\d)-(\d\d\d\d)', da)
            if not res:
                da = datetime.now()
            else:
                da = datetime(int(res.group(3)), int(res.group(2)),
                                  int(res.group(1)))
        pat = models.Patient(name              = ga("new_name", ''),
                             title             = title, gender=gender,
                             age               = ga("new_age", 0),
                             regdate           = da,
                             phone             = ga('new_ph', ''),
                             address           = ga('new_addr', ''),
                             occupation        = ga('new_occup', ''),
                             reg_fee           = ga('new_rfee', 0),
                             relative          = ga('new_relname', ''),
                             relative_relation = ga('new_relrel', ''),
                             relative_phone    = ga('new_relph', '')
                             )
        try:
            session().add(pat)
            session().commit()
            self.redirect('/view/patient/id/%d' % pat.id)
        except Exception, e:
            msg = 'Error saving details for patient %s (Msg: %s)' % (
                pat.name, e)
            logging.error('NewPatientHandler.post(): %s', msg)

    def get (self):
        depts = models.Department.sorted_dept_names(session)
        depts.insert(0, '-- Select --')
        self.render('patient_new.html', depts=depts,
                    today=models.MyT.today_uk(), **self.base_kwargs)

class DoctorHandler(BaseHandler):
    ## FIXME: These arrays should be generated based on the actual shift
    ## timings from the 'Shift' table
    mophours=["-- Select --",
              "08:00", "08:30", "09:00", "09:30",
              "10:00", "10:30", "11:00", "11:30",
              "12:00", "12:30", "13:00", "13:30", "14:00"]
    aophours=["-- Select --",
              "14:00", "14:30", "15:00", "15:30",
              "16:00", "16:30", "17:00", "17:30", "18:00"]

    # FIXME: This should ideally go into a config file, and the template in
    # doctor_base.html should programmatically display the correct number of
    # select elements.
    max_depts = 2

    def make_doc_from_args (self, doc=None):
        """Invoked in the context of a POST handler this routine instantiates
        a new Doctor model object with values in the POST request and returns
        it. It is assumed that all the input validation is done on the UI
        side.

        req should be an instance of a subclass of tornado.web.RequestHandler"""

        ga = self.get_argument
        da = ga('new_rdate', '')
        if da == '':
            da = date.today()
        else:
            res = re.search('(\d\d)-(\d\d)-(\d\d\d\d)', da)
            if not res:
                da = date.today()
            else:
                da = date(int(res.group(3)), int(res.group(2)),
                          int(res.group(1)))

        if not doc:
            doc = models.Doctor(name    = ga("new_name", ''),
                                active  = True if ga("new_active", None) == 'active' else False,
                                title   = ga("new_title", ''),
                                regdate = da,
                                fee_newp = ga('new_rfee_n', 0),
                                fee_oldp = ga('new_rfee_o', 0),
                                quals   = ga('new_quals', ''),
                                phone   = ga('new_ph', ''),
                                address = ga('new_addr', ''),
                                email   = ga('new_em', ''))
        else:
            doc.name    = ga("new_name", '')
            doc.active  = True if ga("new_active", None) == 'active' else False
            doc.title   = ga("new_title", '')
            doc.regdate = da
            doc.fee_newp = ga('new_rfee_n', 0)
            doc.fee_oldp = ga('new_rfee_o', 0)
            doc.quals   = ga('new_quals', '')
            doc.phone   = ga('new_ph', '')
            doc.address = ga('new_addr', '')
            doc.email   = ga('new_em', '')

        return doc

    def add_depts_from_req_to_doc (self, doc):
        ga = self.get_argument
        dirty = False

        # Undo department mappings if any
        doc.depts[:] = []

        for i in range(self.max_depts):
            tag = 'newd_dept_%02d' % (i+1)
            dept = models.Department.find_by_name(session, ga(tag, None))
            if dept:
                doc.depts.append(dept)
                dirty = True

        if dirty:
            session().commit()

    def add_slots_from_req_to_doc (self, doc):
        """Invoked in the context of a POST handler this routine instantiates
        an array of Slot model objects with values in the POST request and
        returns it. It is assumed that all the input validation is done on the
        UI side."""

        ga = self.get_argument

        # First remove any Slots and departments in the doctor record already
        # present
        [session().delete(slot) for slot in doc.slots]

        for day in days:
            for shift in shiftns:
                argf = string.strip(ga('newd_%s_%s_from' % (day, shift), ''))
                argt = string.strip(ga('newd_%s_%s_to'   % (day, shift), ''))

                if argf == '' or argt == '':
                    logging.info('issues with slots; argf: %s; %s', argf, argt)
                    continue

                # For some strange reason when nothing is selected what is
                # returned is not -- Select -- but just the first strong
                if argf != '--' and argt != '--':
                    s = models.Slot(doctor_id=doc.id, day=day, shift=shift,
                                    start_time=argf, end_time=argt)
                    session().add(s)

        session().commit()

class NewDoctorHandler(DoctorHandler):
    def post (self):
        ga = self.get_argument
        doc  = self.make_doc_from_args()
        try:
            session().add(doc)
            session().commit()
        except Exception, e:
            msg = 'Error saving details for Doctor %s (Msg: %s)' % (
                doc.name, e)
            logging.error('NewDoctorHandler: %s', msg)
            return

        self.add_depts_from_req_to_doc(doc)

        ## Now try to add the slot information and commit the changes
        self.add_slots_from_req_to_doc(doc)

        self.redirect('/view/doctor/id/%d' % doc.id)

    def get (self):
        depts = models.Department.sorted_dept_names(session)
        depts.insert(0, '-- Select --')

        self.render('doctor_new.html', depts=depts, days=days,
                    today=models.MyT.today_uk(), mophours=self.mophours,
                    aophours=self.aophours, **self.base_kwargs)

class EditDoctorHandler(DoctorHandler):
    """Edit the patient details. The form is pre-loaded with the current
    personal details."""

    def post (self, field, value):
        if field != 'id':
            return

        q = session().query(models.Doctor)
        d = q.filter_by(id=value).first()

        rec = self.make_doc_from_args(d)
        try:
            session().commit()
        except Exception, e:
            ## FIXME: Erorr handling to be performed
            logging.error('Exception while saving modifications for %s (%s)',
                          rec.name, e)
            return

        self.add_depts_from_req_to_doc(rec)

        ## Now try to add the slot information and commit the changes
        self.add_slots_from_req_to_doc(rec)
        self.redirect('/view/doctor/id/%d' % rec.id)

    def get (self, field, value):
        if field != 'id':
            ## FIXME: Error needs to be highlighted
            return

        deptq = session().query(models.Department)
        depts = [d.name for d in deptq]
        depts.insert(0, '-- Select --')

        q = session().query(models.Doctor)
        rec = q.filter_by(id=value).first()
        self.render("doctor_edit.html", rec=rec, days=days, depts=depts,
                    mophours=self.mophours, aophours=self.aophours,
                    **self.base_kwargs)

class NewVisitHandler(BaseHandler):
    def post (self):
        dept  = self.get_argument("newv_dept_list", None)
        dat   = self.get_argument("newv_date",  None)
        docid = self.get_argument("newv_docid_hack", None)
        deptn = self.get_argument("newv_dept_list", None)
        charge = self.get_argument("newv_charge", None)
        url   = self.request.full_url()
        patid = int(re.search('patid=(\d+)', url).group(1))

        if not docid or docid == 'null':
            logging.error('NewVisitHandler.post(): Oops. JS Error checking fail')
            self.redirect('/view/patient/id/%d' % patid)
            return

        if deptn:
            deptid = models.Department.id_from_name(session, deptn)
        else:
            deptid = None

        if not dat or dat == '':
            dat = date.today()
        else:
            res = re.search('(\d\d)-(\d\d)-(\d\d\d\d)', dat)
            if not res:
                dat = date.today()
            else:
                dat = date(int(res.group(3)), int(res.group(2)),
                           int(res.group(1)))

        cid = models.Consultation.num_in_day(session(), dat) + 1
        c = models.Consultation(patient_id=patid, doctor_id=docid, cid=cid,
                                dept_id=deptid, date=dat, charge=charge)
        try:
            session().add(c)
            session().commit()
            self.redirect('/view/patient/id/%d' % patid)
        except Exception, e:
            msg = 'Error saving visit details for patient %s (Msg: %s)' % (
                patid, e)
            logging.error('NewVisitHandler.post(): %s', msg)

    def get (self):
        s = session().query(models.Shift)
        shifts = dict([(shift.name, shift) for shift in s])

        patid = self.get_argument('patid', None)
        if not patid:
            self.redirect('/')
            return

        ## Note that not passing the patient name argument (as 'patname') will
        ## make us performa db lookup, merely to display. So if the source
        ## page already has the name, said name should be passed in the GET
        ## request.

        patid = int(patid)
        patname = self.get_argument('patname', None)

        if patid:
            q = session().query(models.Patient)
            rec = q.filter_by(id=patid).first()
            patname = rec.name
        else:
            q = session().query(models.Patient)
            rec = q.filter_by(name=patname).first()
            patid = rec.id

        last_docid = self.get_argument('last_docid', None)
        last_deptn = self.get_argument('last_deptn', None)
        if not last_docid or not last_deptn:
            numc = len(rec.consultations)
            if numc > 0:
                lv = rec.consultations[numc-1]
                last_docid = lv.doctor_id
                last_deptn = models.Department.name_from_id(session, lv.dept_id)

        depts = models.Department.sorted_dept_names(session)
        depts.insert(0, '-- Select --')
        d = copy.deepcopy(days)
        d.insert(0, '-- Any --')

        date = models.MyT.today_uk()

        self.render('visit_new.html', depts=depts,
                    patid=patid, patname=patname, date=date, days=d,
                    shifts=shifts, docid=last_docid, last_deptn=last_deptn,
                    **self.base_kwargs)

class MainHandler(BaseHandler):
    def get (self):
        self.render('index.html', **self.base_kwargs)

def engine (val=None):
    global _engine
    if val:
        _engine = val
    else:
        return _engine

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/new/patient", NewPatientHandler),
    (r"/new/doctor", NewDoctorHandler),
    (r"/new/visit", NewVisitHandler),

    (r"/edit/patient/(.*)/(.*)", EditPatientHandler),
    (r"/edit/doctor/(.*)/(.*)", EditDoctorHandler),
    (r"/view/(.*)/(.*)/(.*)", ViewHandler),
    (r"/search/(.*)", SearchHandler),

    (r"/ajax/doctors/department/(.*)/(.*)", AjaxDoctorsInDepartment),
    (r"/ajax/patient/id/(.*)", AjaxPatientDetails),
    (r"/ajax/doctor/id/(.*)", AjaxDoctorDetails),
    (r"/ajax/docavailability", AjaxDocAvailability),
    (r"/ajax/departments", AjaxDepartmentsList),
    (r"/ajax/appstate", AjaxAppState),
    (r"/ajax/jqueryFileTree", AjaxFileTree),

    (r"/miscadmin/", MiscAdminHandler),
    (r"/backup", BackupHandler),
    (r"/backup/(.*)", BackupHandler),
    (r"/stats/(.*)/(.*)", StatsHandler),
    (r"/logs", LogsHandler),

    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': static_path})
], debug=True, template_path=os.path.join(DIR_PATH, 'templates'))

## override the tornado.web.ErrorHandler with our default ErrorHandler
tornado.web.ErrorHandler = ErrorHandler

def get_demo_db_name ():
    ## FIXME: We should really be returning an absolute path
    return os.path.join('db', 'sample.db')

def get_pdn_dir ():
    """Return the path of the directory containing some of the production
    datbase, log files, backups etc. If the directory is not present it is
    first created and the name of the directory is returned. The full
    absolute path is returned"""

    ## TODO: Make this a config variable part of config.json and read
    ## in via config.py
    d = os.path.abspath(os.path.join('..', 'PRS-Production'))

    if not os.path.exists(d):
        logging.info('Creating production database directory (%s)..', d)
        os.makedirs(d)

    return d

def get_pdn_db_name (abspath=True):
    """Returns the full qualified name of the database file."""

    f = 'prs.db'
    return os.path.join(get_pdn_dir(), f) if abspath else f

def get_backups_basedir ():
    """Returns an absolute path of a directory where all backups are stored by
    default. Default is the directory containing the database itself."""

    return os.path.join(get_pdn_dir(), 'backups')

def gen_backup_instance_name ():
    """Return a unique name for a directory that will contain new backup
    files. For now it will just the time stamp in yyyy-mm-dd-hh-mm-ss
    format."""

    return datetime.now().strftime('%Y-%m-%d-%H%M%S')

def start_browser ():
    port = config.get_http_port()
    webbrowser.open('http://localhost:%d' % port, new=2)

## FIXME: This should all be in config.json and be configurable there.
SIZE = 0
TIME = 1
LOG_ROTATION_TYPE = SIZE
DAYS_PER_LOGFILE = 30
MAX_LOGSIZE  = 1024*1024*20                # 20 MB
MAX_LOGFILES = 5

def get_logfile_name ():
    return os.path.join(get_pdn_dir(), 'prs.log')

def setup_logging ():
    f = get_logfile_name()

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if LOG_ROTATION_TYPE == SIZE:
        ch = logging.handlers.RotatingFileHandler(f, maxBytes=MAX_LOGSIZE,
                                                  backupCount=MAX_LOGFILES)
    else:
        ch = logging.handlers.TimedRotatingFileHandler(f, when='d',
                                                       interval=DAYS_PER_LOGFILE,
                                                       backupCount=MAX_LOGFILES)
    fo = logging.Formatter('%(asctime)s - [%(levelname)8s]: %(message)s')
    ch.setFormatter(fo)
    logger.addHandler(ch)


def main ():
    setup_logging()
    logging.info('Well, well. Just opened the log file. Hurrah!')

    tornado.options.parse_command_line()

    models.eng_s, models.sess_s = models.setup_tables(get_demo_db_name())
    models.eng_p, models.sess_p = models.setup_tables(get_pdn_db_name())

    try:
        application.listen(config.get_http_port())
    except socket.error, e:
        # This happens if an instance is already running on the said port.
        logging.info('Program already running. Just starting a browser session.')
        start_browser()
        sys.exit(0)

    logging.info('** On Startup: Using PRS Version: %s', prs_ver)
    logging.info('** On Startup: Schema Version: %s', models.schema_ver)

    start_browser()
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
