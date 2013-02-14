//
// Created       : Wed Jan 30 18:07:03 IST 2013
// Last Modified : Thu Feb 14 15:20:58 IST 2013
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

// This file is loaded only inside the visit_stats.html template when
// the user clicks on 'Visit Stats' link in the main navigation bar to the left.

function setUpTable (elemid, aoColumns) {
    var cols = aoColumns.length;
    $(elemid).dataTable({
	//       "bInfo" : false,

	"aLengthMenu": [[25, 50, 100, 200, -1],
			[25, 50, 100, 200, "All"]],

	"iDisplayLength" : -1,

	"aoColumns": aoColumns,

	"fnFooterCallback": function (nRow, aaData, iStart, iEnd, aiDisplay) {
	    /*
	     * Calculate the total visit count and net fee for all
	     * elements displayed in this page
	     */
	    var iTotalVisit = 0;
	    var iTotalFee   = 0;
	    for (var i=0 ; i<aaData.length ; i++ ) {
		iTotalVisit += aaData[i][cols-2]*1;
		iTotalFee   += aaData[i][cols-1]*1;
	    }

            $("#vs_total_visits").html(iTotalVisit);
            $("#vs_total_fee").html('Rs. ' + iTotalFee);

	    /* Calculate the market share for browsers on this page */
	    var iPageVisit = 0;
	    var iPageFee   = 0;
	    for (var i=iStart; i<iEnd ; i++) {
		iPageVisit += aaData[aiDisplay[i]][cols-2]*1;
		iPageFee   += aaData[aiDisplay[i]][cols-1]*1;
	    }
      
	    /* Modify the footer row to match what we want */
	    var nCells = nRow.getElementsByTagName('th');
	    nCells[1].innerHTML = parseInt(iPageVisit);
	    nCells[2].innerHTML = 'Rs. ' + parseInt(iPageFee);
	}
    });
}

jQuery(function() {
    setUpTable("#vs_dept_table", 
	       [{ "sClass": "center",},  // S. No
		{ "sClass": "left", },   // Department Name
		{ "sClass": "right",},
		{ "sClass": "right"}]);
    setUpTable("#vs_doc_table", 
	       [{ "sClass": "center",},  // S. No
		{ "sClass": "center", }, // Title
		{ "sClass": "left", },   // Name
		{ "sClass": "left", },   // Qualifications
		{ "sClass": "right",},
		{ "sClass": "right"}]);
});
