##
## Created       : Mon May 14 23:04:44 IST 2012
## Last Modified : Tue Jan 29 17:06:55 IST 2013
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

import demjson, logging, os

class Config:
    def __init__ (self, confn, synct=True):
        confi   = None

        self.sync_through = synct
        self.confn  = os.path.abspath(confn)

        try:
            confi = open(confn, "r")
        except IOError, e:
            logging.critical('Error! Could not Open file (%s): %s', confn, e)
            raise

        stc = confi.read()
        self.state = demjson.decode(stc)

        confi.close()

        self.set_app_root(os.path.abspath(''))

    ##
    ## Helper routines
    ##

    ## Not dependent on sync state between a pair of PIMDs

    def _get_prop (self, key):
        return self.state[key]

    def _set_prop (self, key, val, sync=False):
        self.state[key] = val

        if self.sync_through and sync:
            self.save_config()

    def _append_to_prop (self, key, val, sync=False):
        """In the particular property value is an array, we would like to
        append individual elements to the property value. this method does
        exactly that."""

        if not self.state[key]:
            self.state[key] = [val]
        else:
            self.state[key].append(val)

        if self.sync_through and sync:
            self.save_config()

    def _update_prop (self, prop, which, val, sync=False):
        """If a particular property value is a dictionary, we would like to
        update the dictinary with a new mapping or alter an existing
        mapping. This method does exactly that."""

        if not self.state[prop]:
            self.state[prop] = {which : val}
        else:
            self.state[prop].update({which : val})

        if self.sync_through and sync:
            self.save_config()

    ##
    ## get/set properties for specified sync profiles.Invalid field access
    ## will throw a AsynkConfigError exeption. ss in the method names stands
    ## for 'sync_state'
    ##

    def get_config (self):
        """Return the full configuration as read from the config.json file"""

        return self.state

    def get_trial_db (self):
        return self._get_prop('trial_db')

    def get_http_port (self):
        return self._get_prop('http_port')

    def get_title (self):
        return self._get_prop('title')    

    def get_app_root (self):
        return self._get_prop('app_root')

    def set_app_root (self, val):
        return self._set_prop('app_root', val)

    ##
    ## Finally the two save routines.
    ##

    def _save (self, fn, json):
        """fn should be the full absolute path. json is the json to be written
        out"""

        try:
            fi = open(fn, "w")
        except IOError, e:
            logging.critical('Error! Could not Open file (%s): %s', fn, e)
            return

        fi.write(json)
        fi.close()

    def save_config (self, fn=None):
        logging.debug(' ==== Alert - trying to save config.json ==== ')
        return
