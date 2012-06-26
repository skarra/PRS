//
// Created       : Sat May 05 13:15:20 IST 2012
// Last Modified : Tue Jun 26 10:35:57 IST 2012
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
    var f_dept     = $('#newp_dept_list').val();
    var f_doc      = $('#newp_doc_list').val();

    var failed  = false;
    var errmsg  = "";

    if (f_name === "") {
        errmsg += "Name cannot be empty\n";
    }

    if (f_age === "") {
        errmsg += "Age field cannot be empty\n";
    } else {
    }

    if (f_dept == "-- Select --") {
	errmsg += "Please Select a department from the given list\n";
    }

    if (f_doc == "-- Select --") {
	errmsg += "Please Select a doctor from the given list\n";
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

    $("#edit_pat_lab").click(function() {
	var url = window.location.pathname;
	var edit_url = url.replace('/view/', '/edit/');
	console.log('Redirecting to: ' + edit_url);
	window.location = edit_url;
    });

    $("#print_pat_lab").click(function() {
	window.print();
    });

    $("#new_patient_form").submit(validateNewPatient);

    $("#newp_dept_list").change(function() {
	console.log('Value: ' + $(this).val());
	// ajax call to fetch doctors in given department and update
	// element for doctor list
	docdiv = $("#newp_doc_list");
	docdiv.html($("<option />").val("-- Select --").text("-- Select --"));
	$.getJSON("/ajax/doctors/department/name/" + $(this).val(),
		  function(data) {
		      $.each(data.doctors, function() {
			  docdiv.append($("<option />").val(this).text(this));
		      });
		      console.log(data.doctors);
		  });
    });
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

function temp () {
    var url = window.location.pathname;
    var pat_url = url.replace('/view/', '/ajax/');
    $.getJSON(pat_url, function(data) {
	$("#new_name").val(data[name]);
    });
}
