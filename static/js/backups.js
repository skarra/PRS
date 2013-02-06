//
// Created       : Wed Jan 30 18:07:03 IST 2013
// Last Modified : Fri Feb 01 08:17:51 IST 2013
//
// Copyright (C) 2012, Sriram Karra <karra.etc@gmail.com>
// All Rights Reserved
//
// This file is part of PRS
//
// PRS is free software: you can redistribute it and/or modify it under
// the terms of the GNU Affero General Public License as published by the
// Free Software Foundation, version 3 of the License
//
// PRS is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
// FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
// License for more details.
//
// You should have a copy of the license in the base directory of PRS.  If
// not, see <http://www.gnu.org/licenses/>.
//

// This file is loaded only inside the backups.html template when
// the user clicks on the Manage Backups link in the Misc Admin function

function backupsOnLoad () {
    $('#backups_ftree').fileTree({
        script: '/ajax/jqueryFileTree',
        expandSpeed: 1000,
        collapseSpeed: 1000,
        multiFolder: false
    }, function(file) {
        alert(file);
    });
}

jQuery(backupsOnLoad);
