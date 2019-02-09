//
// Created       : Sat May 05 13:15:20 IST 2012
// Last Modified : Fri Feb 08 23:23:35 PST 2019
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

var pat_srp_table;
var doc_srp_table;
var pat_visits_table;
var newv_doc_table;
var last_cid   = null;
var last_deptn = null;
var last_docn  = null;
var last_docid = null;
var last_avail = null;

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
	    var name = data.departments[key][1];
	    var id   = data.departments[key][0];
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
    var f_phone    = $('#new_ph').val();
    var f_addr     = $('#new_addr').val();
    var f_relname  = $('#new_relname').val();
    var f_relph    = $('#new_relph').val();
    var f_relrel   = $('#new_relrel').val();

    var error  = false;
    var warning = false;
    var errmsg  = "Error!!\n\n";
    var warningmsg = "Warning!!\n\n";

    if (f_name === "") {
	error = true;
        errmsg += "Name cannot be empty\n";
    }

    if (f_age === "") {
	error = true;
        errmsg += "Age field cannot be empty\n";
    } else {
    }

    if (f_phone == "") {
	warning = true
	warningmsg += "We recommend providing a Patient phone number. You can provide it later.\n";
    } else if (!isValidPhoneNumber(f_phone, "Phone number")) {
	warning = true;
	warningmsg += "Patient phone number does not look valid.\n";
    }

    if (f_relname == "") {
	errmsg += "Emergency Contact details (name) cannot be empty\n";
    }

    if (f_relph == "") {
	error = true;
	errmsg += "Emergency Contact details (phone) cannot be empty\n";
    } else if (!isValidPhoneNumber(f_relph, "Relative's Phone number")) {
	warning = true;
	warningmsg += "Emergency Contact phone number does not appear valid\n";
    }

    if (f_relrel == "") {
	error = true;
	errmsg += "Emergency Contact details (relation) cannot be empty\n";
    }

    if (f_reg_date === "") {
        f_reg_date = new Date();
    }

    if (error) {
        alert(errmsg);
        return false;
    }

    if (warning) {
	alert(warningmsg);
    }
}

function refreshVisitDocTable () {
    newv_doc_table.fnClearTable();
    var dept = $("#newv_dept_list").val();
    var patid = $("#new_visit_form").attr("patid");
    var date = $("#newv_date").val();
    var day  = dayOfWeek(date);

    console.log('day of week : ' + day);

    // var day   = $("#newv_day_list").val();
    // var shift = $("#newv_shift_list").val();

    var base  = "/ajax/docavailability";
    var params = "?patid=" + patid + "&dept=" + encodeURIComponent(dept) + "&day=" + encodeURIComponent(day);
    var url   = base + params;

    $.getJSON(url, function(data) {
	console.log("Got " + data.count + " entries in ajax response.");
        if (data.count == 0) {
            $("#new_visit_doc_div").hide();
            $("#new_visit_doc_warning").show();
        } else {
            $("#new_visit_doc_div").show();
            $("#new_visit_doc_warning").hide();
            $.each(data.doctors, function(key) {
                var morns = data.doctors[key][day]["Morning"].join(", ");
                var evens = data.doctors[key][day]["Afternoon"].join(", ");
                newv_doc_table.dataTable().fnAddData(
                    [[data.doctors[key].id, "Dr. " + key, data.doctors[key].quals,
                      morns, evens, data.doctors[key].fee_newp, 
                      data.doctors[key].fee_oldp,
                      data.doctors[key].charge]]);
                });
        }
    });
}

/* Get the rows which are currently selected */
function fnGetSelected (oTableLocal, col) {
    var aReturn = new Array();
    var aTrs = oTableLocal.fnGetNodes();

    for ( var i=0 ; i<aTrs.length ; i++ ) {
	if ( $(aTrs[i]).hasClass('row_selected')) {
	    return oTableLocal.fnGetData(aTrs[i], col);
	}
    }

    return null;
}

function validateNewVisitForm () {
    // Validate the selections and POST a message to the server
    var dept  = $("#newv_dept_list").val();
    var docid = fnGetSelected(newv_doc_table, 0);
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
    var docid = fnGetSelected(newv_doc_table, 0);
    $("#newv_docid_hack").val(docid);
    $("#newv_charge").val(fnGetSelected(newv_doc_table, 7));
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
            { "sWidth": "15%", "sClass": "center"},
	    { "sClass": "right"},
            { "sClass": "right"},
            { "sClass": "right"}],
	"aLengthMenu": [[10, 25, 50, 100, 200, -1],
			[10, 25, 50, 100, 200, "All"]],
        "columnDefs": [{
                "targets": [ 7 ],
                "visible": false,
                "searchable": false
            }],
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
    var silent_err = false;

    if (f_name === "") {
        errmsg += "Name cannot be empty\n";
    }

    if (f_phone === "") {
        errmsg += "Phone field cannot be empty\n";
    } else {
	if (!isValidPhoneNumber(f_phone, "Phone number")) {
	    silent_err = true;
	}
    }

    if (f_dept1 == "-- Select --" && f_dept2 == "-- Select --" && 
	f_dept3 == "-- Select --") {
	errmsg += "Please Select atleast one department from given list\n";
    }

    if (errmsg != "") {
        alert(errmsg)
        return false;
    }

    if (silent_err) {
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
	"aLengthMenu": [[10, 25, 50, 100, 200, -1],
			[10, 25, 50, 100, 200, "All"]],
	"iDisplayLength": 20
    });

    $("#new_doctor_form").submit(validateNewDoctor);

    // In the department dropdowns, any time the user selects one of the
    // options, we want to mark such elements as not available in the other
    // sibling dropddowns, so that we get unique department names.
    var prev_val = null;
    $("select.deptsel").focus(function() {
	prev_val = $(this).val();
	if (prev_val != '-- Select --') {
	    $(this).siblings().find("option:[value='"+prev_val+"']")
		.attr('disabled', 'disabled');
	}
    }).change(function() {
	var val = $(this).val();
        if (prev_val != null && prev_val != '-- Select --') {
	    $(this).siblings().find("option:[value='"+prev_val+"']")
		.removeAttr('disabled');	
	}

	if (val != '-- Select --') {
	    $(this).siblings().find("option:[value='"+val+"']")
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
	"aLengthMenu": [[10, 25, 50, 100, 200, -1],
			[10, 25, 50, 100, 200, "All"]],
	"aoColumns": [
            { "sClass": "left" },
            { "sClass": "center" },
            { "sClass": "center" },
            { "sClass": "center" },
            { "sClass": "center" },
            { "sClass": "center" },
            { "sClass": "center" },
            { "sClass": "center"}]
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
	var msg, disp;
	if (data['config']['trial_db']) {
	    if (data['environment_is_demo']) {
		msg = 'Switch to Production DB';
		disp = 'block';
	    } else {
		msg = 'Switch to Demo DB';
		disp = 'none';
	    }

	    $("#site-title:hover").css('color', 'blue');
	    $("#demo_db_warn").css('display', disp);
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
		  window.location = '//www.google.com';
	      } catch (err) {
		  console.log('Message 2: ' + err);
		  window.close();
	      }
	  });
}

var mainDialogCB;

function setUpExitHandlerDialog () {
    $("#main-dialog").dialog({
	autoOpen: false,
	resizable: false,
	height: 160,
	width: 500,
	modal: true,
	buttons: {
	    "Yes, I know what I am doing": function() {
		$(this).dialog("close");
		mainDialogCB();
	    },
	    Cancel: function() {
		$(this).dialog("close");
	    }
	}
    });
}

function handleExit () {
    $("#main-dialog-text").text("You will exit the System. Are you sure?");
    mainDialogCB = exit;
    $("#main-dialog").dialog("open");
}

function handleSwitchDB () {
    $("#main-dialog-text").text("Are you sure you want to change the database?");
    mainDialogCB = function () {
	$("#misc_admin").submit();
    }
    $("#main-dialog").dialog("open");
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
	} else if (val == 'mas_db') {
	    handleSwitchDB();
	} else {
	    if (val == 'mas_vl') {
		var msg = 'Browser: ' + BrowserDetect.browser;
		msg += ' Version: ' + BrowserDetect.version;
		msg += '. OS: ' + BrowserDetect.OS;
		$("#misc_admin_params").val(msg);
	    }
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
// Ensure the number we got is actually valid. This method returns
// true if valid and false otherwise. In the process of parsing it may
// check with the user about a doubtful number, and return true if the
// user confirms
//

function isValidPhoneNumber (phoneNumber, text) {
    var regionCode = 'IN';
    var output = new goog.string.StringBuffer();
    var isNumberValid    = false;
    var isValidForRegion = false;
    var isPossibleNumber = false;

    try {
	var phoneUtil = i18n.phonenumbers.PhoneNumberUtil.getInstance();
	var number = phoneUtil.parseAndKeepRawInput(phoneNumber, regionCode);

	// output.append(goog.json.serialize(new goog.proto2.ObjectSerializer(
        //     goog.proto2.ObjectSerializer.KeyOption.NAME).serialize(number)));

	isNumberValid = phoneUtil.isValidNumber(number);
	isValidForRegion = phoneUtil.isValidNumberForRegion(number, regionCode);
	isPossibleNumber = phoneUtil.isPossibleNumber(number);

	if (isValidForRegion) {
	    return true;
	}

	if (isPossibleNumber) {
	    // We need to ask for a confirmation here
	    if (confirm(text + " (" + phoneNumber + ") " +
			"may be invalid. Are you sure it is correct?")) {
		return true;
	    }
	}

	return false;
    } catch (e) {
	alert('Exception while parsing number (' + phoneNumber + '): '  + e);
	return false;
    }
}

//
// Event Handlers and validations for visit_stats.html 
//

function validateVisitStatsSubmit () {
    var from = $("#vs_from").val();
    var to   = $("#vs_to").val();
    var msg  = '';
    var res = null;

    if (from == '') {
	msg += 'From date cannot be empty.\n';
    }

    if (to == '') {
	msg += 'To date cannot be empty.\n';
    }

    res  = from.match(/(\d+)\-(\d+)\-(\d\d\d\d)/);
    from = new Date(res[3], res[2]-1, res[1]);
    res  = to.match(/(\d+)\-(\d+)\-(\d\d\d\d)/);
    to   = new Date(res[3], res[2]-1, res[1]);

    console.log('res: ' + res);
    console.log('From: ' + from + '; to: ' + to);

    if (msg == '' && (from > to)) {
	msg += 'From has to be an earlier than or same as To date.\n';
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

//
// Handlers for the stuff in patient_view.html
//

function newpvRowSelected (event) {
    $(pat_visits_table.fnSettings().aoData).each(function () {
	$(this.nTr).removeClass('row_selected');
    });

    $(event.target.parentNode).addClass('row_selected');
    last_date  = fnGetSelected(pat_visits_table, 0);
    last_cid   = fnGetSelected(pat_visits_table, 1);
    last_deptn = fnGetSelected(pat_visits_table, 2);
    last_docn  = fnGetSelected(pat_visits_table, 3);
    last_charge= fnGetSelected(pat_visits_table, 4);
    last_docid = fnGetSelected(pat_visits_table, 5);
    last_avail = fnGetSelected(pat_visits_table, 6);
    visit_type = fnGetSelected(pat_visits_table, 7);

    $("#lvisit_date").text(last_date);
    $("#lvisit_cid").text(last_cid);
    $("#lvisit_dname").text(last_deptn);
    $("#lvisit_docn").text(last_docn);
    $("#lvisit_davail").text(last_avail);

    if (last_charge == 0) {
        $("#visit_receipt").hide();
    } else {
        $("#visit_receipt").show();
        $("#lvisit_charge").text(last_charge);
        $("#lvisit_type").text(visit_type);
    }
}

function addHandlers_patient_view () {
    pat_visits_table = $("#pat_visits_table").dataTable({
	"bFilter": false,
	"bInfo": false,
	"bPaginate": false,
	"bSort" : false,

	"aLengthMenu": [[10, 25, 50, 100, 200, -1],
			[10, 25, 50, 100, 200, "All"]],

	"aoColumns": [
            { "sClass": "left" },
            { "sClass": "right" },
            { "sClass": "left" },
            { "sClass": "left" },
            { "sClass": "right" },
            { "sClass": "right" },
            { "sClass": "right" },
	    { "sClass": "right" }]
    });

    $("#pat_visits_table tbody").click(newpvRowSelected);

    $("#edit_pat_lab").click(function() {
	var url = window.location.pathname;
	var edit_url = url.replace('/view/', '/edit/');
	console.log('Redirecting to: ' + edit_url);
	window.location = edit_url;
    });

    $(".printElem").click(function() {
	window.print();
    });

    $("#visit_pat_lab").click(function() {
	var url = window.location.pathname;
	var patid = url.match(/\/(\d+)$/)[1];
	console.log("matched patid: " + patid);
	var edit_url = "/new/visit?patid=" + patid;
	if (last_docid) {
	    edit_url += '&last_docid=' + last_docid;
	}
	if (last_deptn) {
	    edit_url += '&last_deptn=' + encodeURIComponent(last_deptn);
	}
	console.log('Redirecting to: ' + edit_url);
	window.location = edit_url;
    });
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
	"aLengthMenu": [[10, 25, 50, 100, 200, -1],
			[10, 25, 50, 100, 200, "All"]],

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
	"aLengthMenu": [[10, 25, 50, 100, 200, -1],
			[10, 25, 50, 100, 200, "All"]],
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

    addHandlers_new_visit();
    addHandlers_doctor_base();
    addHandlers_doctor_view();
    addHandlers_doctor_edit();
    addHandlers_misc_menu()
    addHandlers_visit_stats();
    addHandlers_patient_view();

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
