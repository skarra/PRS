//
// Created       : Wed Jan 30 18:07:03 IST 2013
// Last Modified : Tue Feb 12 14:41:47 IST 2013
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

function setUpTable (elemid) {
    $(elemid).dataTable({
	//       "bInfo" : false,

	"aLengthMenu": [[25, 50, 100, 200, -1],
			[25, 50, 100, 200, "All"]],

	"iDisplayLength" : -1,

	"aoColumns": [
            { "sClass": "right",},
            { "sClass": "left", },
            { "sClass": "right",},
            { "sClass": "right",}],

	"fnFooterCallback": function (nRow, aaData, iStart, iEnd, aiDisplay) {
	    /*
	     * Calculate the total visit count and net fee for all
	     * elements displayed in this page
	     */
	    var iTotalVisit = 0;
	    var iTotalFee   = 0;
	    for (var i=0 ; i<aaData.length ; i++ ) {
		iTotalVisit += aaData[i][2]*1;
		iTotalFee += aaData[i][3]*1;
	    }

            $("#vs_total_visits").html(iTotalVisit);
            $("#vs_total_fee").html('Rs. ' + iTotalFee);

	    /* Calculate the market share for browsers on this page */
	    var iPageVisit = 0;
	    var iPageFee   = 0;
	    for (var i=iStart; i<iEnd ; i++) {
		iPageVisit += aaData[aiDisplay[i]][2]*1;
		iPageFee   += aaData[aiDisplay[i]][3]*1;
	    }
      
	    /* Modify the footer row to match what we want */
	    var nCells = nRow.getElementsByTagName('th');
	    nCells[1].innerHTML = parseInt(iPageVisit);
	    nCells[2].innerHTML = 'Rs. ' + parseInt(iPageFee);
	}
    });
}

jQuery(function() {
    setUpTable("#vs_dept_table");
    setUpTable("#vs_doc_table");
});
