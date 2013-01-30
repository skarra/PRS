//
// Created       : Wed Jan 30 18:07:03 IST 2013
// Last Modified : Wed Jan 30 20:17:05 IST 2013
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

// This file is loaded only inside the visit_new.html template when
// the user clicks on the New Visit link while viewing a patient
// record.


// contains a unique list of all the doctors (IDs) that a given
// patient has visited in the past.
var vn_visited_docids = [];
var vn_curr_patid = null;

function vnOnLoad () {
    var t   = '' + window.location;
    vn_curr_patid = t.match(/patid=(\d+)/)[1];

    // Populate the visited doctors list
    $.getJSON('/ajax/patient/id/' + vn_curr_patid, function(data) {
	$.each(data['visits'], function(index, value) {
	    var docid = value['doctor_id'];
	    if ($.inArray(docid, vn_visited_docids) == -1) {
		vn_visited_docids.push(docid);
	    }
	});
	console.log('Visited docids: ' + vn_visited_docids);
    });

    // For revisit patients, the department and doctor should be
    // preselected. For that to happen, we should at least refresh the
    // doctor availability table
    var dept = $("#newv_dept_list").val();
    if ((dept != "") && (dept != null)) {
	refreshVisitDocTable();
    }
}

jQuery(vnOnLoad);
