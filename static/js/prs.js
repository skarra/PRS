//
// Created       : Sat May 05 13:15:20 IST 2012
// Last Modified : Mon May 28 11:41:09 IST 2012
//
// Copyright (C) 2012, Sriram Karra <karra.etc@gmail.com>
// All Rights Reserved
//
// Licensed under the GNU GPL v3
//

var pat_srp_table;
var doc_srp_table;

function validateNewPatient (event) {
    console.log('Validating new patient record...');

    var f_name     = $('#new_name').val();
    var f_age      = $('#new_age').val();
    var f_reg_date = $('#new_reg_date').val();
    var f_phone    = $('#new_phone').val();
    var f_addr     = $('#new_addr').val();
    var f_doc      = $('#new_doc').val();

    var failed  = false;
    var errmsg  = "";

    if (f_name === "") {
        errmsg += "Name cannot be empty\n";
    }

    if (f_age === "") {
        errmsg += "Age field cannot be empty\n";
    } else {
    }

    if (f_reg_date === "") {
        f_reg_date = new Date();
    }

    if (errmsg != "") {
        alert(errmsg)
        return false;
    }

    console.log('WTF.... f_name: ' + f_name)
}

function addHandlers () {
    console.log('addFormHandlers...');

    $("#site-title").click(function() {
	window.location = "/";
    })

    $("#dispatch_new_p").click(function() {
	window.location = '/newpatient';
    });

    $("#view_all_p").click(function() {
	window.location = '/search/patient?id=all';
    });

    $("#view_all_d").click(function() {
	window.location = '/search/doctor?id=all';
    });

    // The following only applies to the srp.html, but it is still
    // desirable to have all the javascipt centralized here (??)...
    pat_srp_table = $("#pat_srp_table").dataTable({
	"fnDrawCallback" : function(oSettings) {
	    $("#pat_srp_table tbody td").click(function () {
		var aPos  = pat_srp_table.fnGetPosition(this);
		var aData = pat_srp_table.fnGetData(aPos[0]);
		console.log('Hurrah. Patient ID selected is: ' + aData[0]);
		window.location = '/view/patient/id/' + aData[0];
	    });
	}
    });

    // The following only applies to the srp.html, but it is still
    // desirable to have all the javascipt centralized here (??)...
    doc_srp_table = $("#doc_srp_table").dataTable({
	"fnDrawCallback" : function(oSettings) {
	    $("#doc_srp_table tbody td").click(function () {
		var aPos  = doc_srp_table.fnGetPosition(this);
		var aData = doc_srp_table.fnGetData(aPos[0]);
		console.log('Hurrah. Doc ID selected is: ' + aData[0]);
		window.location = '/view/doctor/id/' + aData[0];
	    });
	}
    });

    $("#new_patient_form").submit(validateNewPatient);
}

function onLoad () {
    console.log('jQuery.onLoad(): Howdy dowdy');

    window.onerror = function (em, url, ln) {
        alert(em + ", " + url + ", " + ln);
        return false;
    }

    addHandlers();
}

jQuery(onLoad);
