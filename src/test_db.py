import os, sys

DIR_PATH    = os.path.abspath('')
EXTRA_PATHS = [os.path.join(DIR_PATH, '../libs'),
               os.path.join(DIR_PATH, '../libs/tornado')]
sys.path = EXTRA_PATHS + sys.path

import models

def query (session):
    pat_q = session.query(models.Patient)
    i = 0
    for pat in pat_q:
        print 'i = %2d. Patient Name: %s' % (i, pat.name)
        i += 1

def main ():
    engine, session = models.setup_tables()
    session.add(models.Patient(name='Donald Rumsfield',
                               age=40, phone='+1 234 456 7890',
                               relative='George Bush'))
    query(session)

if __name__ == "__main__":
    main()
