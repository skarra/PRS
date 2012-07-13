## -*- python -*-
##
## Created       : Mon May 14 18:10:41 IST 2012
## Last Modified : Fri Jul 13 08:13:14 IST 2012
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

import copy, httplib, os, re, string, sys, webbrowser
from   datetime import datetime, date

DIR_PATH    = os.path.abspath('')
EXTRA_PATHS = [os.path.join(DIR_PATH, 'src'),
               os.path.join(DIR_PATH, 'libs'),
               os.path.join(DIR_PATH, 'libs/tornado')]

sys.path = EXTRA_PATHS + sys.path

import   tornado.ioloop, tornado.web, tornado.options
import   models, config
from     sqlalchemy import and_

static_path = os.path.join(DIR_PATH, 'static')
config_file = os.path.join(DIR_PATH, 'config.json')
config      = config.Config(config_file)

days   = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday',
          'Friday', 'Saturday']
shiftns = ['Morning', 'Afternoon']

settings = {'debug': True,
            'static_path': os.path.join(DIR_PATH, 'static')}

production = 0
sample     = 1
db = sample

def db_env ():
    return db

def is_production (env):
    return env == production

def is_demo (env):
    return env == sample

def toggle_env ():
    global db
    if is_production(db_env()):
        db = sample
    else:
        db = production

class ErrorHandler(tornado.web.RequestHandler):
    """Generates an error response with status_code for all requests."""
    def __init__ (self, application, request, status_code):
        tornado.web.RequestHandler.__init__(self, application, request)
        self.set_status(status_code)

    def write_error (self, status_code, **kwargs):
        if status_code in [403, 404, 500, 503]:
            filename = '%d.html' % status_code
            self.render(filename, title=config.get_title())
        else:
            self.write("<html><title>%(code)d: %(message)s</title>" \
            "<body class='bodyErrorPage'>%(code)d: %(message)s</body>"\
            "</html>" % {
                "code": status_code,
                "message": httplib.responses[status_code],
            })

    def prepare (self):
        raise tornado.web.HTTPError(self._status_code)

class BaseHandler(tornado.web.RequestHandler):
    """Generates an error response with status_code for all requests."""

    def write_error (self, status_code, **kwargs):
        if status_code in [403, 404, 500, 503]:
            filename = '%d.html' % status_code
            self.render(filename, title=config.get_title())
        else:
            self.write("<html><title>%(code)d: %(message)s</title>" \
            "<body class='bodyErrorPage'>%(code)d: %(message)s</body>"\
            "</html>" % {
                "code": status_code,
                "message": httplib.responses[status_code],
                })

class MiscAdminHandler(BaseHandler):
    def edit_depts (self):
        depts = session().query(models.Department)
        self.render('department_edit.html', title=config.get_title(),
                    depts=depts)

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
        else:
            self.redirect('/')

##
## All the classes that start with Ajax are ajax handler that return JSON
##

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
    """Return an array of doctor ID and Names as 'id - name' strings. Keeping
    in line with general good practise this is wrapped into a dictionary."""

    def get (self, field, value):
        ret   = []
        q = session().query(models.Department)
        if field == 'name':
            rec = q.filter_by(name=value).first()
        elif field == 'id':
            rec = q.filter_by(id=value).first()
        else:
            rec = None

        if rec:
            docs = rec.doctors
            for doc in docs:
                ret.append('%3d - %s' % (doc.id, doc.name))

        self.write({"doctors" : ret})

class AjaxPatientDetails(BaseHandler):
    """Return the details of the patient as a dictionary"""

    def get (self, patid):
        ret   = {}
        q = session().query(models.Patient)
        rec = q.filter_by(id=patid).first()

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
                        })

        self.write(ret)

class AjaxDoctorDetails(BaseHandler):
    """Return the details of the doctor as a dictionary"""

    def get (self, docid):
        ret = {}
        q = session().query(models.Doctor)
        rec = q.filter_by(id=docid).first()

        avail = {}

        # FIXME: The code block below is repeated more or less verbatim in
        # another routine... Can be refactored.
        for slot in rec.slots:
            h = '%s-%s' % (slot.start_time, slot.end_time)
            if slot.day in avail:
                if slot.shift in avail[slot.day]:
                    oldh = avail[slot.day][slot.shift] + ', '
                else:
                    oldh = ''

                avail[slot.day].update({slot.shift : (oldh + h)})
            else:
                avail.update({slot.day : {
                    slot.shift : h
                    }})

        if rec:
            ret.update({'name'    : rec.name,
                        'title'   : rec.title,
                        'quals'   : rec.quals,
                        'regdate' : rec.regdate.isoformat(),
                        'phone'   : rec.phone,
                        'fee'     : rec.fee,
                        'email'   : rec.email,
                        'address' : rec.address,
                        'avail'   : avail,
                        'depts'   : [d.name for d in rec.depts],
                        })

        self.write(ret)

class AjaxDocAvailability(BaseHandler):
    """Return the details of the patient as a dictionary"""

    def get (self):
        ret   = {}
        dept_name = self.get_argument('dept', None)
        if not dept_name:
            ## FIXME: handle error
            return

        day    = self.get_argument('day', '-- Any --')
        shiftn = self.get_argument('shift', '-- Any --')

        dq = session().query(models.Doctor, models.Slot)
        dq = dq.filter(models.Doctor.depts.any(name=dept_name))
        dq = dq.filter(models.Doctor.id == models.Slot.doctor_id)
        if day != '-- Any --':
            dq = dq.filter(models.Slot.day  == day)
        if shiftn != '-- Any --':
            dq = dq.filter(models.Slot.shift == shiftn)

        docs = dq.all()
        for doc, slot in docs:
            if not doc.name in ret:
                ret[doc.name] = {
                    'id'    : doc.id,
                    'quals' : doc.quals,
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

        self.render(template, title=config.get_title(),
                    search_query=qstr, search_results=results,
                    total_cnt=total_cnt, match_cnt=match_cnt)

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

        print 'Field: ', field
        print 'value: ', value
        if role in ['patient', 'doctor']:
            return self.search(role, field, value)
        else:
            self.redirect('/')

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

        avail = {}
        for day in days:
            avail.update({day : {
                'Morning Hours' : '-',
                'Afternoon Hours' : '-',
                }})

        for slot in rec.slots:
            shift = '%s Hours' % slot.shift
            times = '%s-%s' % (slot.start_time, slot.end_time)

            if avail[slot.day][shift] != '-':
                times = avail[slot.day][shift] + ', ' + times

            avail[slot.day].update({ shift : times })

        self.render('doctor_view.html', title=config.get_title(),
                    rec=rec, days=days, avail=avail)

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

        self.render('patient_view.html', title=config.get_title(),
                    rec=rec, d=session().query(models.Doctor))

    def get (self, role, field, value):
        """role is one of 'patient' or 'doctor', field will be one of Name or
        ID (for now). value is the value to lookup for the field in the
        database"""

        if role == 'patient':
            return self.view_patient(field, value)
        elif role == 'doctor':
            return self.view_doctor(field, value)
        else:
            ## FIXME: Need to highlight Error.
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
            res = re.search('(\d\d)/(\d\d)/(\d\d\d\d)', da)
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
            print 'Exception while saving modifications for %s (%s)' % (
                rec.name, e)

    def get (self, field, value):
        if field != 'id':
            ## FIXME: Error needs to be highlighted
            return
        q = session().query(models.Patient)
        rec = q.filter_by(id=value).first()
        self.render("patient_edit.html", title=config.get_title(),
                    rec=rec, today=models.today_uk())

class NewPatientHandler(BaseHandler):
    def post (self):
        ga = self.get_argument
        gender = ga('new_gender', 'Male')
        title  = 'Mr.' if gender == 'Male' else 'Ms.'
        da = ga('new_rdate', '')
        if da == '':
            da = datetime.now()
        else:
            res = re.search('(\d\d)/(\d\d)/(\d\d\d\d)', da)
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
            print '*** NewPatientHandler: ', msg

    def get (self):
        depts = models.Department.sorted_dept_names(session)
        depts.insert(0, '-- Select --')
        self.render('patient_new.html', title=config.get_title(),
                    depts=depts, today=models.today_uk())

class DoctorHandler(BaseHandler):
    ## FIXME: These arrays should be generated based on the actual shift
    ## timings from the 'Shift' table
    mophours=["-- Select --", "09:00", "10:00", "11:00", "12:00", "13:00"]
    aophours=["-- Select --", "14:00", "15:00", "16:00", "17:00", "18:00"]

    max_depts = 3

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
            res = re.search('(\d\d)/(\d\d)/(\d\d\d\d)', da)
            if not res:
                da = date.today()
            else:
                da = date(int(res.group(3)), int(res.group(2)),
                          int(res.group(1)))

        if not doc:
            doc = models.Doctor(name    = ga("new_name", ''),
                                title   = ga("new_title", ''),
                                regdate = da,
                                fee     = ga('new_rfee', 0),
                                quals   = ga('new_quals', ''),
                                phone   = ga('new_ph', ''),
                                address = ga('new_addr', ''),
                                email   = ga('new_em', ''))
        else:
            doc.name    = ga("new_name", '')
            doc.title   = ga("new_title", '')
            doc.regdate = da
            doc.fee     = ga('new_rfee', 0)
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
                    print 'issues with slots; argf: ', argf, '; argt: ', argt
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
            print '*** NewDoctorHandler: ', msg
            return

        self.add_depts_from_req_to_doc(doc)

        ## Now try to add the slot information and commit the changes
        self.add_slots_from_req_to_doc(doc)

        self.redirect('/view/doctor/id/%d' % doc.id)

    def get (self):
        depts = models.Department.sorted_dept_names(session)
        depts.insert(0, '-- Select --')

        self.render('doctor_new.html', title=config.get_title(),
                    depts=depts, days=days, today=models.today_uk(),
                    mophours=self.mophours, aophours=self.aophours)

class EditDoctorHandler(DoctorHandler):
    """Edit the patient details. The form is pre-loaded with the current
    personal details."""

    def post (self, field, value):
        if field != 'id':
            return

        q = session().query(models.Doctor)
        d = q.filter_by(id=value).first()

        ga = self.get_argument
        rec = self.make_doc_from_args(d)
        try:
            session().commit()
        except Exception, e:
            ## FIXME: Erorr handling to be performed
            print 'Exception while saving modifications for %s (%s)' % (
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
        self.render("doctor_edit.html", title=config.get_title(),
                    rec=rec, days=days, depts=depts,
                    mophours=self.mophours, aophours=self.aophours)

class NewVisitHandler(BaseHandler):
    def post (self):
        dept  = self.get_argument("newv_dept_list", None)
        dat   = self.get_argument("newv_date",  None)
        docid = self.get_argument("newv_docid_hack", None)
        deptn = self.get_argument("newv_dept_list", None)
        charge = self.get_argument("newv_charge", None)
        url   = self.request.full_url()
        patid = int(re.search('patid=(\d+)$', url).group(1))

        if not docid or docid == 'null':
            print 'Oops. Error checking in js not up to snuff...'
            self.redirect('/view/patient/id/%d' % patid)
            return

        if deptn:
            deptid = models.Department.id_from_name(session, deptn)
        else:
            deptid = None

        if not dat or dat == '':
            dat = date.today()
        else:
            res = re.search('(\d\d)/(\d\d)/(\d\d\d\d)', dat)
            if not res:
                dat = date.today()
            else:
                dat = date(int(res.group(3)), int(res.group(2)),
                           int(res.group(1)))

        c = models.Consultation(patient_id=patid, doctor_id=docid,
                                dept_id=deptid, date=dat, charge=charge)
        try:
            session().add(c)
            session().commit()
            self.redirect('/view/patient/id/%d' % patid)
        except Exception, e:
            msg = 'Error saving visit details for patient %s (Msg: %s)' % (
                patid, e)
            print '*** NewVisitHandler: ', msg

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

        numc = len(rec.consultations)
        print numc
        if numc > 0:
            lv = rec.consultations[numc-1]
            last_docid = lv.doctor_id
            last_deptn = models.Department.name_from_id(session, lv.dept_id)
        else:
            last_docid = None
            last_deptn = None        

        depts = models.Department.sorted_dept_names(session)
        depts.insert(0, '-- Select --')
        d = copy.deepcopy(days)
        d.insert(0, '-- Any --')

        date = models.today_uk()

        self.render('visit_new.html', title=config.get_title(), depts=depts,
                    patid=patid, patname=patname, date=date, days=d,
                    shifts=shifts, docid=last_docid, last_deptn=last_deptn)

class MainHandler(BaseHandler):
    def get (self):
        self.render('index.html', title=config.get_title())

def engine (val=None):
    global _engine
    if val:
        _engine = val
    else:
        return _engine

def session ():
    if db_env() == production:
        return sess_p
    elif db == sample:
        return sess_s

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

    (r"/miscadmin/", MiscAdminHandler),

    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': static_path})
], debug=True, template_path=os.path.join(DIR_PATH, 'templates'))

## override the tornado.web.ErrorHandler with our default ErrorHandler
tornado.web.ErrorHandler = ErrorHandler

if __name__ == "__main__":
    global eng_s, sess_s, eng_p, sess_p

    tornado.options.parse_command_line()

    eng_s, sess_s = models.setup_tables('db/sample.db')
    eng_p, sess_p = models.setup_tables('db/prs.db')

    port = 8888
    application.listen(port)
    webbrowser.open('http://localhost:%d' % port, new=2)
    tornado.ioloop.IOLoop.instance().start()
