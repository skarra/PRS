//
// Created       : Sat May 05 13:15:20 IST 2012
// Last Modified : Tue Jul 17 23:09:25 IST 2012
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
	res = date.match(/(\d+)\-(\d+)\-(\d\d\d\d)/);
	d.setFullYear(res[3], res[2]-1, res[1]);
	date = d;
    }

    return days[date.getDay()];
}

function setupDateLocale () {
    $.datepicker.regional['en-GB'] = {
	closeText: 'Done',
	prevText: 'Prev',
	nextText: 'Next',
	currentText: 'Today',
	monthNames: ['January','February','March', 'April',
		     'May','June', 'July', 'August',
		     'September','October','November','December'],
	monthNamesShort: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
			  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
	dayNames: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 
		   'Friday', 'Saturday'],
	dayNamesShort: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
	dayNamesMin: ['Su','Mo','Tu','We','Th','Fr','Sa'],
	weekHeader: 'Wk',
	dateFormat: 'dd-mm-yy',
	firstDay: 1,
	isRTL: false,
	showMonthAfterYear: false,
	yearSuffix: ''};

    $.datepicker.setDefaults($.datepicker.regional['en-GB']);

    // Now bind all elements marked as date-field as date pickers.
    $(".date-field").each(function() {
	$(this).datepicker();
    });
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

    $("#dept_doc_v").change(function() {
	console.log('val: ' + $(this).val());
	$("#search_dept_d").submit();
    });
}

function validateNewPatient (event) {
    console.log('Validating new patient record...');

    var f_name     = $('#new_name').val();
    var f_age      = $('#new_age').val();
    var f_reg_date = $('#new_reg_date').val();
    var f_phone    = $('#new_phone').val();
    var f_addr     = $('#new_addr').val();
    var f_relname  = $('#new_relname').val();
    var f_relph    = $('#new_ph').val();
    var f_relrel   = $('#new_relrel').val();

    var failed  = false;
    var errmsg  = "";

    if (f_name === "") {
        errmsg += "Name cannot be empty\n";
    }

    if (f_age === "") {
        errmsg += "Age field cannot be empty\n";
    } else {
    }

    if (f_relname == "") {
	errmsg += "Emergency Contact details (name) cannot be empty\n";
    }

    if (f_relph == "") {
	errmsg += "Emergency Contact details (phone) cannot be empty\n";
    }

    if (f_relrel == "") {
	errmsg += "Emergency Contact details (relation) cannot be empty\n";
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
    $("#newv_dept_list").change(refreshVisitDocTable);
    $("#newv_date").change(refreshVisitDocTable);
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

function addHandlers_department_edit () {
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
}

function addHandlers_db_toggle () {
    // Set the right message for toggling environment if the config
    // allows the usage of a trial database in addition to the
    // production database.

    $.getJSON("/ajax/appstate", function(data) {
	var msg, url, color;
	if (data['config']['trial_db']) {
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
	} else {
	    $("#mas_db").remove();
	}
    });
}

function exit () {
    // The guy really wants to exit. Do the needful.
    $.get('/miscadmin/',
	  {'misc_admin_s' : 'mas_exit'},
	  function(data) {
	      console.log('Message 3');
	      window.close();
	  }).error(function() {
	      try {
		  console.log('Message 1');
		  window.close();
	      } catch (err) {
		  console.log('Message 2: ' + err);
		  window.close();
	      }
	  });
}

function setUpExitHandlerDialog () {
    $("#exit-dialog-confirm" ).dialog({
	autoOpen: false,
	resizable: false,
	height: 160,
	width: 500,
	modal: true,
	buttons: {
	    "Yes, I want to Exit": function() {
		$(this).dialog("close");
		exit();
	    },
	    Cancel: function() {
		$(this).dialog("close");
		window.location = '/';
	    }
	}
    });
}

function handleExit () {
    $("#exit-dialog-confirm").dialog("open");
}

function addHandlers_misc_menu () {
    // Set up the elements of the drop down "Misc Menu"
    addHandlers_department_edit();
    addHandlers_db_toggle();

    // Set up an event handler for a change event
    $("#misc_admin_s").change(function() {
	var val = $("#misc_admin_s").val();
	if (val == 'mas_exit') {
	    handleExit(val);
	} else {
	    $("#misc_admin").submit();
	}
    });
}

// The following function addTextFilters() is taken verbatim from
// example 17.06 of David Flanagan's book "Javascript - The Definitive
// Guide" His own desription and comments are reproduced in full below

/*
 * InputFilter.js: unobtrusive filtering of keystrokes for <input> elements
 *
 * This module finds all <input type="text"> elements in the document that
 * have an "data-allowed-chars" attribute. It registers keypress, textInput, and
 * textinput event handlers for any such element to restrict the user's input
 * so that only characters that appear in the value of the attribute may be
 * entered. If the <input> element also has an attribute named "data-messageid",
 * the value of that attribute is taken to be the id of another document
 * element. If the user types a character that is not allowed, the message
 * element is made visible. If the user types a character that is allowed, the
 * message element is hidden. This message id element is intended to offer
 * an explanation to the user of why her keystroke was rejected. It should
 * typically be styled with CSS so that it is initially invisible.
 *
 * Here is sample HTML that uses this module.
 *   Zipcode: <input id="zip" type="text"
 *                   data-allowed-chars="0123456789" data-messageid="zipwarn">
 *   <span id="zipwarn" style="color:red;visibility:hidden">Digits only</span>
 *
 * This module is purely unobtrusive: it does not define any symbols in
 * the global namespace.
 */
function addTextFilters () {
    // Find all <input> elements
    var inputelts = document.getElementsByTagName("input");
    // Loop through them all
    for(var i = 0 ; i < inputelts.length; i++) {
        var elt = inputelts[i];
        // Skip those that aren't text fields or that don't have
        // a data-allowed-chars attribute.
        if (elt.type != "text" || !elt.getAttribute("data-allowed-chars"))
            continue;
        
        // Register our event handler function on this input element
        // keypress is a legacy event handler that works everywhere.
        // textInput (mixed-case) is supported by Safari and Chrome in 2010.
        // textinput (lowercase) is the version in the DOM Level 3 Events draft.
        if (elt.addEventListener) {
            elt.addEventListener("keypress", filter, false);
            elt.addEventListener("textInput", filter, false);
            elt.addEventListener("textinput", filter, false);
        }
        else { // textinput not supported versions of IE w/o addEventListener()
            elt.attachEvent("onkeypress", filter); 
        }
    }

    // This is the keypress and textInput handler that filters the user's input
    function filter(event) {
        // Get the event object and the target element target
        var e = event || window.event;         // Standard or IE model
        var target = e.target || e.srcElement; // Standard or IE model
        var text = null;                       // The text that was entered

        // Get the character or text that was entered
        if (e.type === "textinput" || e.type === "textInput") text = e.data;
        else {  // This was a legacy keypress event
            // Firefox uses charCode for printable key press events
            var code = e.charCode || e.keyCode;

            // If this keystroke is a function key of any kind, do not filter it
            if (code < 32 ||           // ASCII control character
                e.charCode == 0 ||     // Function key (Firefox only)
                e.ctrlKey || e.altKey) // Modifier key held down
                return;                // Don't filter this event

            // Convert character code into a string
            var text = String.fromCharCode(code);
        }
        
        // Now look up information we need from this input element
        var allowed = target.getAttribute("data-allowed-chars"); // Legal chars
        var messageid = target.getAttribute("data-messageid");   // Message id
        if (messageid)  // If there is a message id, get the element
            var messageElement = document.getElementById(messageid);
        
        // Loop through the characters of the input text
        for(var i = 0; i < text.length; i++) {
            var c = text.charAt(i);
            if (allowed.indexOf(c) == -1) { // Is this a disallowed character?
                // Display the message element, if there is one
                if (messageElement) messageElement.style.visibility = "visible";

                // Cancel the default action so the text isn't inserted
                if (e.preventDefault) e.preventDefault();
                if (e.returnValue) e.returnValue = false;
                return false;
            }
        }

        // If all the characters were legal, hide the message if there is one.
        if (messageElement) messageElement.style.visibility = "hidden";
    }
}

//
// Event Handlers and validations for visit_stats.html 
//

function validateVisitStatsSubmit () {
    var from = $("#vs_from").val();
    var to   = $("#vs_to").val();
    var msg  = '';

    if (from == '') {
	msg += 'From date cannot be empty.\n';
    }

    if (to == '') {
	msg += 'To date cannot be empty.\n';
    }

    if (msg == '' && (from == to)) {
	msg += 'From has to be an earlier date than .\n';
    }

    // FIXME: Dates need to be validated. The following does not work.

    if (msg == '' && (from > to)) {
	msg += 'From has to be an earlier date than .\n';
    }

    if (msg != '') {
 	alert(msg);
 	return false;
    }
}

function addHandlers_visit_stats () {
    $("#vs_dept_list").change(function() {
	// ajax call to fetch doctors in given department and update
	// element for doctor list
	docdiv = $("#vs_doc_list");
	docdiv.html($("<option />").val("All").text("All"));
	$.getJSON("/ajax/doctors/department/id/" + $(this).val(),
		  function(data) {
		      $.each(data.doctors, function() {
			  docdiv.append($("<option />")
					.val(this[0]).text(this[1]));
		      });
		  });
    });

    $("#vs_form").submit(validateVisitStatsSubmit);
}

function addHandlers () {
    console.log('addFormHandlers...');

    setupDateLocale();
    setUpExitHandlerDialog();

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

    addHandlers_new_visit();
    addHandlers_doctor_base();
    addHandlers_doctor_view();
    addHandlers_doctor_edit();
    addHandlers_misc_menu()
    addHandlers_visit_stats();

    addTextFilters();
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
