##
## Created       : Mon May 14 23:04:44 IST 2012
## Last Modified : Sun Feb 03 01:00:19 PST 2019
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
##
#####
##
## Our database schema delcarations, and other such hair raising stuff.
##

import datetime, logging, re

## FIXME: This is related to using apsw for database backup
# from   pysqlite2 import dbapi2 as s3
# import apsw

from   sqlalchemy        import orm, create_engine
from   sqlalchemy.orm    import relationship, backref, column_property, validates
from   sqlalchemy.pool   import SingletonThreadPool as STP
from   sqlalchemy.types  import Integer, Boolean, Date, Text, Unicode
from   sqlalchemy.schema import Column, ForeignKey, Table
from   sqlalchemy.ext.hybrid import hybrid_property

from   sqlalchemy.ext.declarative import declarative_base

schema_ver = 1

Base   = declarative_base()
days   = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday',
          'Friday', 'Saturday']
shiftns = ['Morning', 'Afternoon']

production = 0
sample     = 1
db = sample
#db = production
sess_p = None
sess_s = None
eng_s  = None
eng_p  = None

def session (env=None):
    if env == production or db_env() == production:
        return sess_p
    else:
        return sess_s

def db_env ():
    return db

def env_name (inpdb=None):
    """Return a string representation of the database environment current
    active or the specfied"""

    db = inpdb if inpdb else db_env()
    if is_production(db):
        return 'production'
    else:
        return 'dev'

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

class MyT: 
    @classmethod
    def today (self):
        """Return today's date in YYYY-MM-DD format"""
        return datetime.date.today()
    
    @classmethod
    def today_s (self):
        """Return today's date in YYYY-MM-DD format"""
        d = datetime.date.today()
        return "%4d-%02d-%02d" % (d.year, d.month, d.day)
    
    @classmethod
    def today_uk (self):
        """Return today's date in DD-MM-YYYY format"""
        d = datetime.date.today()
        return "%02d-%02d-%04d" % (d.day, d.month, d.year)

    @classmethod
    def date_from_uk (self, value):
        """Return a Python datetime.date object from a string formatted as a
        UK date string DD-MM-YYYY."""
        dt = datetime.datetime.strptime(value, '%d-%m-%Y')
        return datetime.date(year=dt.year, month=dt.month, day=dt.day)

    @classmethod
    def date_to_uk (self, d):
        return d.strftime("%d-%m-%Y")

class Patient(Base):
    __tablename__ = 'patient'

    id      = Column(Integer, primary_key=True)
    title   = Column(Unicode(5))
    name    = Column(Unicode(255), nullable=False)
    regdate = Column(Date(), default=MyT.today())
    age     = Column(Integer, nullable=False)
    gender  = Column(Unicode(6), nullable=False)

    phone   = Column(Unicode(255), nullable=False)
    address = Column(Text())

    relative          = Column(Unicode(255))
    relative_phone    = Column(Unicode(255))
    relative_relation = Column(Unicode(255))

    occupation = Column(Unicode(255))

    free    = Column(Boolean, default=True)
    reg_fee = Column(Integer, default=0)

    consultations = relationship("Consultation", 
                                 backref=backref('patient',
                                                 cascade="all"))

    @classmethod
    def find_by_id (self, session, did):
        """Returns the record that matches given id. Returns None if
        there is no match."""

        q   = session().query(Patient)
        recs = q.filter_by(id=did)
        return recs.first() if recs.count() > 0 else None

    def earliest_visit_id (self, session):
        """Returns the ID of this patient's earliest visit. For now this is
        estimated as the visit done on the earliest date. If there is more
        than one visit on that day, the visit with the lowest ID is
        returned. FIXME: This stuff is way too slow to work in practise. to
        generate statistics"""

        q = session().query(Consultation).filter_by(patient_id=self.id).order_by(Consultation.date).order_by(Consultation.cid)
        return q.first().id if q.count() > 0 else None

    def __repr__(self):
        return ("<Patient(id:%d,Name:%s, age:%d)>" %
                (self.id, self.name, self.age))

dept_doc_atable = Table('dept_doctors', Base.metadata,
    Column('dept_id', Integer, ForeignKey('dept.id')),
    Column('doctor_id', Integer, ForeignKey('doctor.id')))

class Doctor(Base):
    __tablename__ = 'doctor'

    id      = Column(Integer, primary_key=True)
    active  = Column(Boolean, default=True)

    title   = Column(Unicode(5), default=u"Dr. ")
    name    = Column(Unicode(255), nullable=False)
    regdate = Column(Date(), default=MyT.today())
    fee_newp = Column(Integer, default=0)     # Fee per visit for new patients
    fee_oldp = Column(Integer, default=0)     # Fee per visit for old patients
    quals   = Column(Text())               # qualifications

    phone   = Column(Unicode(255))
    address = Column(Text())
    email   = Column(Unicode(255))

    consultations = relationship('Consultation',
                                 backref=backref('doctor',
                                                 cascade="all"))
    # 'slots' through backref from Slot
    # 'depts' through backref from Department

    def get_availability (self):
        """REturns the present doctor's consulting hours in as much detail as
        available. The format is a dictionary with the name of day as key."""

        avail = {}
        for day in days:
            avail.update({day : {
                'Morning' : '-',
                'Afternoon' : '-',
                }})

        for slot in self.slots:
            shift = '%s' % slot.shift
            times = '%s-%s' % (slot.start_time, slot.end_time)

            if avail[slot.day][shift] != '-':
                times = avail[slot.day][shift] + ', ' + times

            avail[slot.day].update({ shift : times })

        return avail

    def get_availability_pretty (self):
        """Get the current doctor's availability as a compressed string that
        can be easily printed out on a single line (if possible)."""

        day_map = {"Monday"    : 0,
                   "Tuesday"   : 1,
                   "Wednesday" : 2,
                   "Thursday"  : 3,
                   "Friday"    : 4,
                   "Saturday"  : 5,
                   "Sunday"    : 6,
                   }
        days = ['M', 'T', 'W', 'Th', 'F', 'Sa', 'Su']
        avail = {}

        for slot in self.slots:
            times = '%s-%s' % (slot.start_time, slot.end_time)
            if times in avail:
                avail[times].append(day_map[slot.day])
            else:
                avail[times] = [day_map[slot.day]]

        ret = []
        for k, v in avail.iteritems():
            ret.append(','.join([days[x] for x in sorted(v)]) + ": " + k)

        return ';'.join(ret)

    @classmethod
    def sorted_doc_names_with_id (self, session):
        """Returns all the doctors in the system as (id, name) tuples, sorted
        by name"""

        q = session().query(Doctor).order_by(Doctor.name)
        ret = [(d.id, d.name) for d in q]
        return ret

    @classmethod
    def sorted_doc_names_with_id_in_dept_id (self, session, id):
        """Returns the doctors in the specified department. An array of (ID,
        name) tuples is returned such that it is sorted on the name."""

        q = session().query(Doctor)
        q = q.filter(Doctor.depts.any(Department.id==id))
        ret = [(d.id, d.name) for d in q]
        return ret

    @classmethod
    def sorted_doc_names_with_id_in_dept_name (self, session, name):
        """Returns the doctors in the specified department. An array of (ID,
        name) tuples is returned such that it is sorted on the name."""

        q = session().query(Doctor)
        q = q.filter(Doctor.depts.any(Department.name==name))
        ret = [(d.id, d.name) for d in q]
        return ret

    @classmethod
    def name_from_id (self, session, id):
        rec = self.find_by_id(session, id)
        return rec.name if rec else None

    @classmethod
    def find_by_id (self, session, did):
        """Returns the record that matches given id. Returns None if
        there is no match."""

        q   = session().query(Doctor)
        recs = q.filter_by(id=did)
        return recs.first() if recs.count() > 0 else None

class Department(Base):
    __tablename__ = 'dept'

    id   = Column(Integer, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    doctors = relationship('Doctor', secondary=dept_doc_atable,
                           backref=backref('depts', cascade="all"))

    ## No idea if this is the right way to do this, but anyway, here goes...
    @classmethod
    def id_from_name (self, session, name):
        rec = self.find_by_name(session, name)
        if rec:
            return rec.id
        else:
            return None

    @classmethod
    def name_from_id (self, session, id):
        rec = self.find_by_id(session, id)
        if rec:
            return rec.name
        else:
            return None        

    @classmethod
    def find_by_name (self, session, name):
        """Returns the first record that matches given name. Returns None if
        there is no match."""

        q   = session().query(Department)
        recs = q.filter_by(name=name)
        if recs.count() > 0:
            return recs.first()

        return None

    @classmethod
    def find_by_id (self, session, did):
        """Returns the record that matches given id. Returns None if
        there is no match."""

        q   = session().query(Department)
        recs = q.filter_by(id=did)
        if recs.count() > 0:
            return recs.first()

        return None

    @classmethod
    def sorted_dept_names (self, session):
        """Returns a list of department names sorted alphabetically."""

        q = session().query(Department)
        return sorted([dept.name for dept in q])

    @classmethod
    def sorted_dept_names_with_id (self, session):
        """Returns a list of department name, id tupes, where the
        array is sorted on the department name"""

        q = session().query(Department)
        ds = sorted([d.name for d in q])

        ret = []
        for d in ds:
            ret.append((q.filter_by(name=d).first().id, d))

        return ret

    @classmethod
    def sorted_depts (self, session):
        """Returns a list of Department objects, such that they are
        sorted by their name field."""

        q = session().query(Department)
        ds = sorted([d.name for d in q])

        ret = []
        for d in ds:
            ret.append(q.filter_by(name=d).first())

        return ret

## The proper way for us to model this is to use a separate table for the
## working hours every day. But this is proving to be too complicated. For now
## this database table is only used to create the sampledb.
class Shift(Base):
    __tablename__ = 'shift'

    id    = Column(Integer, primary_key=True)
    name  = Column(Unicode(16))                     # ['Morning', 'Afternoon']
    start = Column(Unicode(4))
    end   = Column(Unicode(4))

class Slot(Base):
    __tablename__ = 'slot'

    id         = Column(Integer, primary_key=True)
    doctor_id  = Column(Integer, ForeignKey('doctor.id'))
    # shift_id   = Column(Integer, ForeignKey('shift.id'))
    day        = Column(Unicode(8))       # ['Sunday', 'Monday'... 'Saturday']
    shift      = Column(Unicode(16))      # ['Morning', 'Afternoon']
    start_time = Column(Unicode(8))
    end_time   = Column(Unicode(8))
    doctor     = relationship('Doctor',
                              backref=backref('slots', cascade="all"))

## The following was suggested by someone on bangpypers, but it does not work.
# def gen_cid (context):
#     return Consultation.query.filter_by(date=context.current_parameters['date']).count() + 1

##
## 2019-02-02: No idea why these two global functions are even in the
## code. Looks like some debugging code sneaked in. Commenting this out for
## now.
##
## def first_doc_visit (context):
##     try:
##         pat_id = context.current_parameters['patient_id']
##         doc_id = context.current_parameters['doctor_id']
##     except KeyError, e:
##         ## We are not updating the patient record.
##         return False
##
##     p = Patient.find_by_id(session, pat_id)
##     for con in p.consultations:
##         if con.doctor_id == doc_id:
##             return False
##
##     return True
##
## def first_dept_visit (context):
##     try:
##         pat_id = context.current_parameters['patient_id']
##         dept_id = context.current_parameters['dept_id']
##     except KeyError, e:
##         ## We are not updating the patient record.
##         return False
##
##     p = Patient.find_by_id(session, pat_id)
##     for con in p.consultations:
##         if con.dept_id == dept_id:
##             return False
##
##     return True

class Consultation(Base):
    __tablename__ = 'consultation'

    id         = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patient.id'))
    doctor_id  = Column(Integer, ForeignKey('doctor.id'))
    dept_id    = Column(Integer, ForeignKey('dept.id'))
    date       = Column(Date(),  default=MyT.today())
    charge     = Column(Integer, default=0)
    notes      = Column(Text())
    cid        = Column(Integer, default=0)   # Visit No. in day.
    first_doc_visit  = Column(Boolean(), default=None)
    first_dept_visit = Column(Boolean(), default=None)

    ## backrefs from patient and doctor

    @validates('doctor_id', 'dept_id', 'patient_id')
    def set_first_visit (self, key, value):
        if key == 'doctor_id':
            if not self.patient_id or not self.dept_id:
                return value
            docid = int(value)
            patid = self.patient_id
            depid = self.dept_id

        if key == 'patient_id':
            if not self.doctor_id or not self.dept_id:
                return value
            docid = self.doctor_id
            patid = int(value)
            depid = self.dept_id

        if key == 'dept_id':
            if not self.patient_id or not self.doctor_id:
                return value
            docid = self.doctor_id
            patid = self.patient_id
            depid = int(value)

        ## Now we are confident that of the 3 attributes we are interested in,
        ## only one remains to be set, and that is the last value.

        first_docv = True
        first_depv = True

        p = Patient.find_by_id(session, patid)
        for con in p.consultations:
            if con.doctor_id == docid:
                first_docv = False
                break

        for con in p.consultations:
            if con.dept_id == depid:
                first_depv = False
                break
    
        self.first_doc_visit  = first_docv
        self.first_dept_visit = first_depv

        logging.info("first_docv: %s; first_devp: %s", first_docv, first_depv)

        return value

    @classmethod
    def num_in_day (self, session, date):
        """Returns the number of consultations that have been registered on
        specified date."""

        q = session().query(Consultation)
        return q.filter_by(date=date).count()


def setup_tables (dbfile):
    """dbfile has to be relative to APP ROOT"""

    logging.debug('setup_tables with dbfile: %s', dbfile)

    ## FIXME: This is related to using apsw for database backup
    # _connection = apsw.Connection(dbfile)
    # connection = s3.connect(_connection)

    logging.debug('Creating engine...')
    engine = create_engine('sqlite:///%s' % dbfile, echo=False)
    logging.debug('Creating engine...done (%s)', engine)

    ## FIXME: This is related to using apsw for database backup
    # _pool = STP(lambda: s3.connect(_connection))
    # engine = create_engine('sqlite://', echo=False, pool=_pool)

    # Set up the session
    logging.debug('Setting up tables...')
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    logging.debug('Setting up tables...done')

    session = orm.scoped_session(orm.sessionmaker(autoflush=True,
                                                  autocommit=False,
                                                  expire_on_commit=True,
                                                  bind=engine))

    return engine, session

def tables ():
    """Returns an array of all the database tables used by the app."""

    return [Patient, Doctor, Department, Shift, Slot, Consultation]
