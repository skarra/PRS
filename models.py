##
## Created       : Mon May 14 23:04:44 IST 2012
## Last Modified : Tue May 15 23:40:21 IST 2012
##
## Copyright (C) 2012 Sriram Karra <karra.etc@gmail.com>
##
## Licensed under the GNU AGPL v3
##
#####
##
## Our database schema delcarations, and other such hair raising stuff.

import datetime

from   sqlalchemy        import orm
from   sqlalchemy.orm    import relationship, backref
from   sqlalchemy.types  import Integer, Boolean, Text, DateTime, Unicode
from   sqlalchemy.schema import Column, ForeignKey

from   sqlalchemy import create_engine
from   sqlalchemy.ext.declarative import declarative_base

Base   = declarative_base(bind=create_engine('sqlite:///:memory:',
                                           echo=False))

def now():
    return datetime.datetime.now()

class Patient(Base):
    __tablename__ = 'patient'

    id      = Column('id',      Integer, primary_key=True)
    name    = Column('name',    Unicode(255), nullable=False)
    regdate = Column('regdate', DateTime(), default=now)
    age     = Column('age',     Integer, nullable=False)

    phone   = Column('phone',   Unicode(255), nullable=False)
    address = Column('address', Text())
    email   = Column('addess',  Unicode(255))

    relative          = Column(Unicode(255), nullable=False)
    relative_phone    = Column(Unicode(255))
    relative_relation = Column(Unicode(255))

    free = Column('free', Boolean, default=True)

    consultations = relationship("Consultation", backref=backref('patient'))

class Doctor(Base):
    __tablename__ = 'doctor'

    id      =  Column('id',      Integer, primary_key=True)
    name    =  Column('name',    Unicode(255), nullable=False)
    regdate =  Column('regdate', DateTime(), default=now)
    quals   =  Column('quals',   Text())

    phone   =  Column('phone',   Unicode(255))
    address =  Column('address', Text())
    email   =  Column('email',   Unicode(255))

    hours         = Column('hours', Text(), nullable=False)
    # consultations = relationship("Consultation", backref=backref('doctor_id'))
    # detps         = relationship("Department")

class Department(Base):
    __tablename__ = 'dept'

    id   = Column('id',   Integer, primary_key=True)
    name = Column('name', Unicode(255), nullable=False)

class DepartmentDoctors(Base):
    __tablename__ = 'dept_doctors'

    id        = Column('id',        Integer, primary_key=True)
    dept_id   = Column('dept_id',   Integer, ForeignKey('dept.id'))
    doctor_id = Column('doctor_id', Integer, ForeignKey('doctor.id'))

class Consultation(Base):
    __tablename__ = 'consultation'

    id         = Column('id',     Integer, primary_key=True)
    patient_id = Column('patient_id', Integer, ForeignKey('patient.id'))
    date       = Column('date',   DateTime(), default=now)
    charge     = Column('charge', Integer, default=0)
    notes      = Column('notes',  Text())

    ## backrefs from patient and doctor

def setup_tables ():
    # Set up the session
    engine = Base.metadata.bind
    Base.metadata.create_all(engine)

    session = orm.scoped_session(orm.sessionmaker(autoflush=True,
                                                  autocommit=False,
                                                  expire_on_commit=True,
                                                  bind=engine))

    return engine, session
