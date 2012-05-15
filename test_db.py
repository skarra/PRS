import os, sys

DIR_PATH    = os.path.abspath('')
EXTRA_PATHS = [os.path.join(DIR_PATH, 'libs'),
               os.path.join(DIR_PATH, 'libs/tornado')]
sys.path = EXTRA_PATHS + sys.path

import models

def add (session):
    pat = models.Patient()
    pat.name = 'Donald Duck'
    pat.age  = '100'
    pat.phone = '+91 90084 88997'
    pat.relative = 'Disney'
    pat.relativeRelation = 'Creator'

    session.add(pat)
    session.flush()
    session.commit()

    print 'Here we go. Patient ID: ', pat.id

def query (session):
    pat_q = session.query(models.Patient)
    i = 0
    for pat in pat_q:
        print 'i = %2d. Patient Name: %s' % (i, pat.name)
        i += 1

def main ():
    engine, session = models.setup_tables()
    add(session)
    query(session)

if __name__ == "__main__":
    main()
