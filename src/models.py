##
## Created       : Mon May 14 23:04:44 IST 2012
## Last Modified : Thu May 24 21:58:46 IST 2012
##
## Copyright (C) 2012 Sriram Karra <karra.etc@gmail.com>
##
## Licensed under the GNU AGPL v3
##
#####
##
## Our database schema delcarations, and other such hair raising stuff.
##

import datetime, logging

from   sqlalchemy        import orm, create_engine
from   sqlalchemy.orm    import relationship, backref
from   sqlalchemy.types  import Integer, Boolean, Text, DateTime, Unicode
from   sqlalchemy.schema import Column, ForeignKey, Table

from   sqlalchemy.ext.declarative import declarative_base

Base   = declarative_base()

def now():
    return datetime.datetime.now()

class Patient(Base):
    __tablename__ = 'patient'

    id      = Column(Integer, primary_key=True)
    title   = Column(Unicode(5))
    name    = Column(Unicode(255), nullable=False)
    regdate = Column(DateTime(), default=now)
    age     = Column(Integer, nullable=False)
    gender  = Column(Unicode(6), nullable=False)

    phone   = Column(Unicode(255), nullable=False)
    address = Column(Text())
    email   = Column(Unicode(255))

    relative          = Column(Unicode(255))
    relative_phone    = Column(Unicode(255))
    relative_relation = Column(Unicode(255))

    free    = Column(Boolean, default=True)
    reg_fee = Column(Integer, default=0)

    allergies = Column(Text())
    old_diag  = Column(Text())

    consultations = relationship("Consultation", cascade="all, delete-orphan")

    def __repr__(self):
        return ("<Patient(id:%d,Name:%s, age:%d)>" %
                (self.id, self.name, self.age))

dept_doc_atable = Table('dept_doctors', Base.metadata,
    Column('dept_id', Integer, ForeignKey('dept.id')),
    Column('doctor_id', Integer, ForeignKey('doctor.id')))

doc_slot_atable = Table('doc_slots', Base.metadata,
    Column('doctor_id', Integer, ForeignKey('doctor.id')),
    Column('slot_id', Integer, ForeignKey('slot.id')))

doc_hour_atable = Table('doc_hours', Base.metadata,
    Column('doctor_id', Integer, ForeignKey('doctor.id')),
    Column('hour_id', Integer, ForeignKey('hour.id')))

class Doctor(Base):
    __tablename__ = 'doctor'

    id      = Column(Integer, primary_key=True)
    title   = Column(Unicode(5))
    name    = Column(Unicode(255), nullable=False)
    regdate = Column(DateTime(), default=now)
    quals   = Column(Text())

    phone   = Column(Unicode(255))
    address = Column(Text())
    email   = Column(Unicode(255))

    consultations = relationship('Consultation', cascade="all, delete-orphan")
    slots         = relationship('Slot', secondary=doc_slot_atable,
                                 backref=backref('doctors', cascade="all"))
    hours         = relationship('Hour', backref=backref('doctor', cascade="all"))

class Department(Base):
    __tablename__ = 'dept'

    id   = Column(Integer, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    doctors = relationship('Doctor', secondary=dept_doc_atable,
                           backref=backref('depts', cascade="all"))

class Slot(Base):
    __tablename__ = 'slot'

    id    = Column(Integer, primary_key=True)
    day   = Column(Unicode(8))
    shift = Column(Unicode(8))
    # doctors through backref via many-to-many doc_slots_atable

class Hour(Base):
    __tablename__ = 'hour'

    id         = Column(Integer, primary_key=True)
    doctor_id  = Column(Integer, ForeignKey('doctor.id'))
    start_time = Column(Unicode(4))
    end_time   = Column(Unicode(4))

class Consultation(Base):
    __tablename__ = 'consultation'

    id         = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patient.id'))
    doctor_id  = Column(Integer, ForeignKey('doctor.id'))
    date       = Column(DateTime(), default=now)
    charge     = Column(Integer, default=0)
    notes      = Column(Text())

    ## backrefs from patient and doctor

def setup_tables (dbfile):
    """dbfile has to be relative to APP ROOT"""

    logging.debug('setup_tables with dbfile: %s', dbfile)

    logging.debug('Creating engine...')
    engine = create_engine('sqlite:///%s' % dbfile, echo=False)
    logging.debug('Creating engine...done (%s)', engine)

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
