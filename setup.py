##
## Created       : Tue May 21 14:34:15 IST 2012
## Last Modified : Tue May 22 14:36:26 IST 2012
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

## This is a configuration file for py2exe to conver PRS into a single
## directory MS EXE distribution.
##
## To build, invoke this as: "python setup.py py2exe"
##
## Of coure, this assumes that py2exe is available in the parent directory as
## py2exe-0.6.9 directory.
##

import glob, os, sys

curr_dir = os.path.abspath('.')
pare_dir = os.path.abspath('..')

sys.path = [os.path.join(pare_dir, 'py2exe-0.6.9', 'py2exe'),
           os.path.join(curr_dir, 'src'),
           os.path.join(curr_dir, 'libs', 'tornado'),
           os.path.join(curr_dir, 'libs', 'sqlalchemy'),
           os.path.join(curr_dir, 'libs')] + sys.path


from distutils.core import setup
import py2exe

data_files = [('', ['config.json']),
              ('db', ['db/prs.db']),
              ('templates',      glob.glob('templates/*.*')),
              ('static',         glob.glob('static/*.*  ')),
              ('static/css',     glob.glob('static/css/*.*')),
              ('static/js',      glob.glob('static/js/*.*')),
              ('static/js/libs', glob.glob('static/js/libs/*.*')),
              ('static/img',     glob.glob('static/img/*.*')),
              ]

setup(console=['prs.py'], options={
    'py2exe' : {
        'includes' : ['demjson'],
        'packages' : ['sqlalchemy.dialects.sqlite'],
        }},
    data_files=data_files,
    )

# The following modules appear to be missing - as identified by the py2exe
# run, but overall does not have any impact on the program's execution.
##
# ['Carbon', 'Carbon.Files', '_curses', '_scproxy', 'django.utils', 'dummy.Process', 'pkg_resources', 'pysqlite2', 'simplejson', 'sqlalchemy.cprocessors', 'sqlalchemy.cresultproxy', 'tornado.epoll']
