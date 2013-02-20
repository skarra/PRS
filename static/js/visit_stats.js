//
// Created       : Wed Jan 30 18:07:03 IST 2013
// Last Modified : Wed Feb 20 07:47:06 IST 2013
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
	    var iTotalVisitN = 0, iTotalVisitO = 0;
	    var iTotalFee    = 0;
	    for (var i=0 ; i<aaData.length ; i++ ) {
		iTotalVisitN += aaData[i][cols-3]*1;
		iTotalVisitO += aaData[i][cols-2]*1;
		iTotalFee    += aaData[i][cols-1]*1;
	    }

            $("#vs_total_visits").html(iTotalVisitN+iTotalVisitO);
            $("#vs_total_fee").html('Rs. ' + iTotalFee);

	    /* Calculate the market share for browsers on this page */
	    var iPageVisitN = 0, iPageVisitO = 0;
	    var iPageFee    = 0;
	    for (var i=iStart; i<iEnd ; i++) {
		iPageVisitN += aaData[aiDisplay[i]][cols-3]*1;
		iPageVisitO += aaData[aiDisplay[i]][cols-2]*1;
		iPageFee    += aaData[aiDisplay[i]][cols-1]*1;
	    }
      
	    /* Modify the footer row to match what we want */
	    var nCells = nRow.getElementsByTagName('th');
	    nCells[1].innerHTML = parseInt(iPageVisitN);
	    nCells[2].innerHTML = parseInt(iPageVisitO);
	    nCells[3].innerHTML = 'Rs. ' + parseInt(iPageFee);
	}
    });
}

jQuery(function() {
    setUpTable("#vs_dept_table", 
	       [{ "sClass": "center",},  // S. No
		{ "sClass": "left", },   // Department Name
		{ "sClass": "right",},
		{ "sClass": "right",},
		{ "sClass": "right"}]);
    setUpTable("#vs_doc_table", 
	       [{ "sClass": "center",},  // S. No
		{ "sClass": "center", }, // Title
		{ "sClass": "left", },   // Name
		{ "sClass": "left", },   // Qualifications
		{ "sClass": "right",},
		{ "sClass": "right",},
		{ "sClass": "right"}]);
});
