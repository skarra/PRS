//
// Created       : Sat May 05 13:15:20 IST 2012
// Last Modified : Fri Jul 06 15:18:26 IST 2012
//
// Copyright (C) 2012, Sriram Karra <karra.etc@gmail.com>
// All Rights Reserved
//
// Licensed under the GNU GPL v3
//

var pat_srp_table;
var doc_srp_table;
var newv_doc_table;

var days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday',
            'Friday', 'Saturday'];
var shiftns = ['Morning', 'Afternoon'];

function dayOfWeek (date) {
    if (!(date instanceof Date)) {
	d = new Date();
	res = date.match(/(\d+)\/(\d+)\/(\d\d\d\d)/);
	d.setFullYear(res[3], res[2]-1, res[1]);
	date = d;
    }
        
    return days[date.getDay()];
}

function setupDeptNamesInControl () {
    var url = "/ajax/departments";
    $.getJSON(url, function(data) {
	console.log("Got " + data.count + " entries in ajax response.");
	$.each(data.departments, function(key) {
	    var name = data.departments[key][0];
	    var id   = data.departments[key][1];
	    $("#dept_doc_v").append("<option val=" + id + ">" + name 
				    + "</option>");
	});
    });
}

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
}

function refreshVisitDocTable () {
    newv_doc_table.fnClearTable();
    var dept = $("#newv_dept_list").val();
    var date = $("#newv_date").val();
    var day  = dayOfWeek(date);

    console.log('day of week : ' + day);

    // var day   = $("#newv_day_list").val();
    // var shift = $("#newv_shift_list").val();

    var base  = "/ajax/docavailability";
    var url   = base + "?dept=" + dept + "&day=" + day;

    $.getJSON(url, function(data) {
	console.log("Got " + data.count + " entries in ajax response.");
	$.each(data.doctors, function(key) {
	    var morns = data.doctors[key][day]["Morning"].join(", ");
	    var evens = data.doctors[key][day]["Afternoon"].join(", ");
	    newv_doc_table.dataTable().fnAddData([
		[data.doctors[key].id, "Dr. " + key, data.doctors[key].quals,
		 morns, evens]]);
	});
    });
}

/* Get the rows which are currently selected */
function fnGetSelected (oTableLocal) {
    var aReturn = new Array();
    var aTrs = oTableLocal.fnGetNodes();

    for ( var i=0 ; i<aTrs.length ; i++ ) {
	if ( $(aTrs[i]).hasClass('row_selected')) {
	    return oTableLocal.fnGetData(aTrs[i], 0);
	}
    }

    return null;
}

function validateNewVisitForm () {
    // Validate the selections and POST a message to the server
    var dept  = $("#newv_dept_list").val();
    var docid = fnGetSelected(newv_doc_table);
    var msg   = "";

    if (docid == null) {
	msg += "Select the doctor you want the patient to see\n";
    }

    if (dept == "-- Select --") {
	msg += "Select one department from the drop down menu";
    }

    if (msg != "") {
	alert(msg);
	return false;
    }

    return true;
}

function newvRowSelected (event) {
    $(newv_doc_table.fnSettings().aoData).each(function () {
	$(this.nTr).removeClass('row_selected');
    });

    $(event.target.parentNode).addClass('row_selected');
    var docid = fnGetSelected(newv_doc_table);
    $("#newv_docid_hack").val(docid);

    // We have to fetch the default consultation charge of the doctor
    // and popualte the 'Charge' field. Note that it will overwrite
    // any manual entry the user might have made before this

    $.getJSON("/ajax/doctor/id/"+docid, function(data) {
	$("#newv_charge").val(data.fee);
    });
}

//
// Event Handlers and stuff for the visit_new.html template.
//
function addHandlers_new_visit () {
    $("#newv_dept_list").change( refreshVisitDocTable);
    $("#newv_date").change(  refreshVisitDocTable);
    $("#newv_shift_list").change(refreshVisitDocTable);

    newv_doc_table = $("#new_visit_doc_table").dataTable({
	"aoColumns": [
            { "sWidth": "3%", "sClass": "center" },
            { "sWidth": "50%" },
            { "sWidth": "17%" },
            { "sWidth": "15%", "sClass": "center"},
            { "sWidth": "15%", "sClass": "center"}],
	"iDisplayLength": 20
    });

    $("#new_visit_doc_table tbody").click(newvRowSelected);
    $("#new_visit_form").submit(validateNewVisitForm);

    // Now select the deafult day as today, this will automatically
    // trigger an updation fo the doctors table.
    var day = dayOfWeek(new Date());
    $("#newv_day_list").val(day);
}

//
// Event Handlers and stuff for the doctor_base.html template.
//
function validateNewDoctor () {
    console.log('Validating new patient record...');

    var f_name     = $('#new_name').val();
    var f_phone    = $('#new_ph').val();
    var f_dept1    = $('#newd_dept_01').val();
    var f_dept2    = $('#newd_dept_02').val();
    var f_dept3    = $('#newd_dept_03').val();

    var errmsg  = "";

    if (f_name === "") {
        errmsg += "Name cannot be empty\n";
    }

    if (f_phone === "") {
        errmsg += "Phone field cannot be empty\n";
    }

    if (f_dept1 == "-- Select --" && f_dept2 == "-- Select --" && 
	f_dept3 == "-- Select --") {
	errmsg += "Please Select atleast one department from given list\n";
    }

    if (errmsg != "") {
        alert(errmsg)
        return false;
    }

    return true;
}

function addHandlers_doctor_base () {
    newd_avail_table = $("#newd_avail").dataTable({
	"bFilter": false,
	"bInfo": false,
	"bPaginate": false,
	"bSort" : false,
	"aoColumns": [
            { "sClass": "left" },
            { "sClass": "center" },
            { "sClass": "center" },
            { "sClass": "center" },
            { "sClass": "center"}],
	"iDisplayLength": 20
    });

    $("#new_doctor_form").submit(validateNewDoctor);

    var prev_val = null;
    $("select.deptsel").focus(function() {
	prev_val = $(this).val();
    }).change(function() {
	var val = $(this).val();
	if (prev_val != null && prev_val != '-- Select --') {
	    $(this).siblings().find("option:[value="+prev_val+"]")
		.removeAttr('disabled');	
	}

	if (val != '-- Select --') {
	    $(this).siblings().find("option:[value="+val+"]")
		.attr('disabled', 'disabled');
	}
    });
}

function addHandlers_doctor_view () {
    doc_view_avail_table = $("#doc_avail_table").dataTable({
	"bFilter": false,
	"bInfo": false,
	"bPaginate": false,
	"bSort" : false,
	"aoColumns": [
            { "sClass": "left" },
            { "sClass": "center" },
            { "sClass": "center" },
            { "sClass": "center" },
            { "sClass": "center" },
            { "sClass": "center" },
            { "sClass": "center" },
            { "sClass": "center"}],
    });
}

function addHandlers_doctor_edit () {
    $("#edit_doc_lab").click(function() {
	var url = window.location.pathname;
	var edit_url = url.replace('/view/', '/edit/');
	console.log('Redirecting to: ' + edit_url);
	window.location = edit_url;
    });
}

var dept_cnt;

function addHandlers_department_edit() {
    var new_box0 = '<div class="dept_inp_name"> <input type="text" ';
    var new_box1;
    var new_box2 = ' placeholder="Enter a new department name" /> </div>';
    var d = 'dept_name_new_';

    dept_cnt = 2;

    $("#dept_add_new").click(function() {
	new_box1 = ' id="' + d + dept_cnt + '" name="' + d + dept_cnt + '"';
	var new_box = new_box0 + new_box1 + new_box2
	$("#dept_inp_names").append(new_box);
	dept_cnt += 1;
    });

    // Set the right message for toggling environment

    $.getJSON("/ajax/appstate", function(data) {
	var msg;
	var url;
	var color;
	if (data['environment_is_demo']) {
	    msg = 'Switch to Production DB';
	    url = 'bkg.png?881083570';
	    color = 'beige';
	} else {
	    msg = 'Switch to Demo DB';
	    url = 'paper.jpg?884184256';
	    color = '#666666';
	}

	url = 'url("/static/img/' + url + '")';
	console.log('url: ' + url);
	$("header").css('background-image', url);
	$("#site-title").css('color', color);
	$("#site-title:hover").css('color', 'blue');
	$("#mas_db").text(msg);
    });    
}

function addHandlers () {
    console.log('addFormHandlers...');

    $("#site-title").click(function() {
	window.location = "/";
    })

    $("#dispatch_new_p").click(function() {
	window.location = '/new/patient';
    });

    $("#view_all_p").click(function() {
	window.location = '/search/patient?id=all';
    });

    $("#dispatch_new_d").click(function() {
	window.location = '/new/doctor';
    });

    $("#view_all_d").click(function() {
	window.location = '/search/doctor?id=all';
    });

    setupDeptNamesInControl();

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

    $("#visit_pat_lab").click(function() {
	var url = window.location.pathname;
	var patid = url.match(/\/(\d+)$/)[1];
	console.log("matched patid: " + patid);
	var edit_url = "/new/visit?patid=" + patid;
	console.log('Redirecting to: ' + edit_url);
	window.location = edit_url;
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

    addHandlers_new_visit();
    addHandlers_doctor_base();
    addHandlers_doctor_view();
    addHandlers_doctor_edit();
    addHandlers_department_edit()
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
