## -*- python -*-
##
## Created       : Mon May 14 18:10:41 IST 2012
## Last Modified : Mon Feb 18 11:07:41 IST 2013
##
## Copyright (C) 2012-18 Sriram Karra <karra.etc@gmail.com>
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

import logging, os, random, re, string, sys

DIR_PATH    = os.path.abspath('')
EXTRA_PATHS = [os.path.join(DIR_PATH, '../libs'),
               os.path.join(DIR_PATH, '../src'),
               os.path.join(DIR_PATH, '../libs/tornado')]
sys.path = EXTRA_PATHS + sys.path

import models

def generate_random_allergies ():
    choices = ['pennicilin', 'pollen', 'streptocaucus']
    return '\n'.join(random.sample(choices, random.randint(1, len(choices))))

def generate_old_diagnosis ():
    diag = 'Ipsum Lorem Dictum scrotum'
    num = random.randint(1, 3)
    ret = [diag]
    for i in range(num):
        ret.append(diag)

    return '\n'.join(ret)

def add_uscongressmen_as_patients (session):
    patients_file = os.path.join(DIR_PATH, 'uscongress.txt')

    ## Each line has the following information. We are keen to retain only the
    ## relevant stuff. We auto-generate the relation contact name and number.

    # District	Name	Party	DC Office	DC Voice	District Voice
    # Electronic Correspondence	Web
    with open(patients_file, 'r') as f:
        line = f.readline()
        fields = line.split('\t')

        while True:
            line = f.readline()
            fields = line.split('\t')
            if line == '':
                break

            logging.debug('Processing %s...', fields[1])
            names  = fields[1].split()         # To construct Relative's Name
            gender = random.choice(['Female', 'Male'])
            allergies = generate_random_allergies()
            old_diag  = generate_old_diagnosis()
            free = random.choice([True, False])
            reg_fee = random.choice([20, 50, 100]) if free else 0

            pat = models.Patient(name=fields[1],
                                 age=random.randint(30, 80),
                                 gender=gender,
                                 title='Mr.' if gender == 'Male' else 'Ms.',
                                 phone=fields[4],
                                 address=fields[3],
                                 relative=(random.choice(['John', 'Jill']) +
                                           ' ' + random.choice(names)),
                                relative_phone=fields[5],
                                relative_relation='Friend',
                                occupation=random.choice(['Freelance',
                                                          'Jobless',
                                                          'Self Employed',
                                                          'Govt Servant',]),
                                free=free,
                                reg_fee=reg_fee
                )
            session.add(pat)

        session.commit()

def add_departments_from_file (session, depts_file):
    with open(depts_file, 'r') as f:
        line = string.strip(f.readline())

        while True:
            line = string.strip(f.readline())
            if line == '':
                break

            logging.debug('Processing %s...', line)
            dept = models.Department(name=line)
            session.add(dept)

        session.commit()

def gen_random_hours ():
    """Generate and return a string of random consultation hours in a comma
    separated format.

    - Four digit times in 24-hr format
    - comma separated values for each day
    - Within each day there can be one or more ranges times separated by
      spaces

    Starts on Sunday

    E.g. 0900-1000 1500-1700 means there are two consultations on that day.
    """

    values = ['0900-1000', '1000-1200', '1200-1300', '1400-1600', '1600-1800']

    ret = []
    for i in range(7):
        num = random.randint(1, 3)
        cons = random.sample(values, num)
        ret.append(' '.join(cons))

    return ','.join(ret)

def add_doctor_names (session, doctors_file):
    ph_lower = 7000000000
    ph_upper = 9999999999

    degrees = ['MBBS', 'MD', 'FRCS', 'BD', 'DO']

    with open(doctors_file, 'r') as f:
        line = f.readline()

        while True:
            line = string.strip(f.readline())
            if line == '':
                break

            names = line.split()
            for name in names:
                if len(name) > 2:
                    n = name
                    break

            logging.debug('Processing %s...', line)
            res = re.search('^Dr\. (.*)', line)
            if res:
                line = res.group(1)

            quals = ', '.join(random.sample(degrees,
                              random.randint(2, 3)))
            doc = models.Doctor(title='Dr.',
                                active=random.choice([True, False]),
                                name=line,
                                fee_newp=random.choice([0, 20, 30, 50]),
                                fee_oldp=random.choice([0, 20, 30, 50]),
                                quals=quals,
                                phone=str(random.randint(ph_lower, ph_upper)),
                                email=n + '@mentalasylum.in')
            session.add(doc)

        session.commit()

def add_shifts (session):
    m = models.Shift(name='Morning', start='0900', end='1300')
    a = models.Shift(name='Afternoon', start='1400', end='1800')
    session.add(m)
    session.add(a)
    session.commit()

def add_slots (session):
    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday',
                    'Friday', 'Saturday']
    shiftns = ['Morning', 'Afternoon']

    q = session.query(models.Doctor)
    s = session.query(models.Shift)
    for doc in q:
        for day in random.sample(days, random.randint(1, len(days))):
            for shift in s:
                start, end = get_random_times(shift)
                slot = models.Slot(doctor_id=doc.id, shift=shift.name,
                                   day=day, start_time=start, end_time=end)
                session.add(slot)

    session.commit()

def get_random_times (shift):
    min = int(shift.start)/100
    max = int(shift.end)/100

    start = random.randint(min, max-1)
    end   = random.randint(start+1, max)

    return ('%02d:00' % start), ('%02d:00' % end)

def add_departments (session):
    q = session.query(models.Doctor)
    doc_cnt = q.count()
    doc_ids = [doc.id for doc in q]

    i = 0
    q = session.query(models.Department)
    while True:
        try:
            for dept in q:
                doc_id = doc_ids[i]
                p = session.query(models.Doctor)
                doc = p.filter_by(id = doc_id).first()
                logging.debug('i = %3d; Adding Doc (%-20s) to Dept (%s)...',
                              i, doc.name, dept.name)
                dept.doctors.append(doc)
                i += 1
        except Exception, e:
            logging.info('Caught exception (%s) breaking by design.', e)
            break

    session.commit()        

def add_consultations (session):
    logging.debug('')
    p = session.query(models.Doctor)
    docs = [doc for doc in p]

    q = session.query(models.Patient)
    for pat in q:
        logging.debug('Adding visits to patient: %s...', pat.name)
        num = random.randint(1, 3)
        for i in range(num):
            charge = random.choice([10, 20, 30, 40, 50])
            date_str = "%d-01-2013" % (random.randint(1, 31))
            dat = models.MyT.date_from_uk(date_str)
            cid = models.Consultation.num_in_day(session, dat) + 1
            con = models.Consultation(charge=charge, cid=cid, date=dat,
                                      notes='Lorem Ipsum Gypsum zero sum')
            doc = random.choice(docs)
            logging.debug('\tAdded doctor ID: %3d, Name: %s...',
                          doc.id, doc.name)
            con.dept_id = doc.depts[0].id
            pat.consultations.append(con)
            doc.consultations.append(con)

    session.commit()

def main ():
    logging.getLogger().setLevel(logging.INFO)

    logging.info('Setting up empty database with approved schema and tables....')
    engine, session = models.setup_tables("../db/empty.db")

    logging.info('Setting up schema and tables....')
    engine, session = models.setup_tables("../db/sample.db")
    models.sess_s = session

    logging.info('Importing US Congressmen as Patients...')
    add_uscongressmen_as_patients(session)

    logging.info('Importing department names from file...')
    add_departments_from_file(session, 'depts.txt')

    logging.info('Adding TN MLAs as doctors...')
    add_doctor_names(session, 'tnmlas.txt')

    logging.info('Setting up Shifts...')
    add_shifts(session)

    logging.info('Setting up Consulting Hours...')
    add_slots(session)

    logging.info('Assigning Departments to doctors...')
    add_departments(session)

    logging.info('Setting up random visits...')
    add_consultations(session)

if __name__ == '__main__':
    main()
