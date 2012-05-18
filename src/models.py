##
## Created       : Mon May 14 23:04:44 IST 2012
## Last Modified : Fri May 18 07:13:48 IST 2012
##
## Copyright (C) 2012 Sriram Karra <karra.etc@gmail.com>
##
## Licensed under the GNU AGPL v3
##
#####
##
## Our database schema delcarations, and other such hair raising stuff.
##

import datetime

from   sqlalchemy        import orm, create_engine
from   sqlalchemy.orm    import relationship, backref
from   sqlalchemy.types  import Integer, Boolean, Text, DateTime, Unicode
from   sqlalchemy.schema import Column, ForeignKey

from   sqlalchemy.ext.declarative import declarative_base

Base   = declarative_base(bind=create_engine('sqlite:///../db/prs.db',
                                           echo=False))

def now():
    return datetime.datetime.now()

class Patient(Base):
    __tablename__ = 'patient'

    id      = Column(Integer, primary_key=True)
    name    = Column(Unicode(255), nullable=False)
    regdate = Column(DateTime(), default=now)
    age     = Column(Integer, nullable=False)

    phone   = Column(Unicode(255), nullable=False)
    address = Column(Text())
    email   = Column(Unicode(255))

    relative          = Column(Unicode(255), nullable=False)
    relative_phone    = Column(Unicode(255))
    relative_relation = Column(Unicode(255))

    free = Column('free', Boolean, default=True)

    consultations = relationship("Consultation", backref=backref('patient'))

    # def __init__(self, name, regdate=None, age, phone, address=None,
    #              email=None, relative=None, relative_phone=None,
    #              relative_relation=None):
    #     """Doh, this was not even required, as this is the same as the
    #     default..."""

    #     self.name              = name
    #     self.regdate           = regdate
    #     self.age               = age
    #     self.phone             = phone
    #     self.address           = address
    #     self.email             = email
    #     self.relative          = relative
    #     self.relative_phone    = relative_phone
    #     self.relative_relation = relative_relation

    def __repr__(self):
        return ("<Patient(id:%d,Name:%s, age:%d)>" %
                (self.id, self.name, self.age))

class Doctor(Base):
    __tablename__ = 'doctor'

    id      =  Column(Integer, primary_key=True)
    name    =  Column(Unicode(255), nullable=False)
    regdate =  Column(DateTime(), default=now)
    quals   =  Column(Text())

    phone   =  Column(Unicode(255))
    address =  Column(Text())
    email   =  Column(Unicode(255))

    hours         = Column(Text(), nullable=False)
    # consultations = relationship("Consultation", backref=backref('doctor_id'))
    # detps         = relationship("Department")

class Department(Base):
    __tablename__ = 'dept'

    id   = Column(Integer, primary_key=True)
    name = Column(Unicode(255), nullable=False)

class DepartmentDoctors(Base):
    __tablename__ = 'dept_doctors'

    id        = Column(Integer, primary_key=True)
    dept_id   = Column(Integer, ForeignKey('dept.id'))
    doctor_id = Column(Integer, ForeignKey('doctor.id'))

class Consultation(Base):
    __tablename__ = 'consultation'

    id         = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patient.id'))
    date       = Column(DateTime(), default=now)
    charge     = Column(Integer, default=0)
    notes      = Column(Text())

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
