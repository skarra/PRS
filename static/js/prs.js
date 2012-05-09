// 
// Created       : Sat May 05 13:15:20 IST 2012
// Last Modified : Wed May 09 09:00:20 IST 2012
//
// Copyright (C) 2012, Sriram Karra <karra.etc@gmail.com>
// All Rights Reserved
//
// Licensed under the GNU GPL v3
// 

// This is the Javascript code needed for manipulating the Indexed DB
// database and other such stuff.

// Some ideas and code borrowed from David Flanagan's Zipcodes
// example in "Javascript, The Definitive Guide, 6th Edition."

// IndexedDB implementations still use API prefixes
var indexedDB = window.indexedDB ||    // Use the standard DB API
    window.mozIndexedDB ||             // Or Firefox's early version of it
    window.webkitIndexedDB;            // Or Chrome's early version

var dbName    = "PRS";
var dbVersion = 4;

// Firefox does not prefix these two:
var IDBTransaction = window.IDBTransaction || window.webkitIDBTransaction;
var IDBKeyRange = window.IDBKeyRange || window.webkitIDBKeyRange;

// We'll use this function to log any database errors that occur
function logerr(e) {
    console.log("IndexedDB error! " + e.target.code + ": " + e.target.message);
    return false;
} 

// This function asynchronously obtains the database object (creating
// and initializing the database if necessary) and passes it to the
// function f().
function withDB (f) {
    var request = indexedDB.open(dbName, dbVersion); // Patient Record System
    request.onerror = logerr;		 // Log any errors
    request.onsuccess = function() {	 // Or call this when done
        var db = request.result;  // The result of the request is the database
	return f(db);
    }
    return false;
}

// Create the two object stores - one for patiens and one for doctors.
function initdb (db) {
    // If the latest version is different than the version we are
    // dealing with, only then there is something to do here. 
    if (db.version == dbVersion) {
	console.log("Database exists, and has the right version: " + dbVersion);
	return;
    }

    if (db.version) {
	console.log("No Database found. Initializing...");
    } else {
	console.log("Database is old version(" + db.version + "). " +
		    "Will upgrade to version: " + dbVersion);
    }

    var request = db.setVersion(dbVersion); // Try to update the DB version
    request.onerror = logerr;
    request.onsuccess  = function() { // Otherwise call this function

	// Delete any existing stores of the same name, and reset counts.
	if(db.objectStoreNames.contains("patients")) {
            db.deleteObjectStore("patients");
	    key = dbName + "_patients_cnt";
	    window.localStorage.setItem(key, 0);
        }

	if(db.objectStoreNames.contains("doctors")) {
            db.deleteObjectStore("doctors");
	    key = dbName + "_doctors_cnt";
	    window.localStorage.setItem(key, 0);
        }

	// Create the patient object store and a few indexes to make queries fast
        var pstore = db.createObjectStore("patients", // store name
                                          { keyPath: "id"});
	pstore.createIndex("patientnames", "name")

	var dstore = db.createObjectStore("doctors", // store name
                                          { keyPath: "id"})
	dstore.createIndex("doctornames", "name")
    }
    alert('Databases initialized. You can now use the system.')
}

function getNewPatientData (event) {
    // Display the data entry form, and return without refreshing the page.
    showElement("new_patient_form");
    return false;
}

// Callback that will be invoked when the indexeddb lookup results set
// is ready to be displayed
function displayRecords (recs) {
    alert("Hoorah! " + recs[0].name);
}

function showElement (elt) {
    document.getElementById("new_patient_form").style.display = "none";
    document.getElementById("display_patients_table").style.display = "none";

    document.getElementById("sheet").style.display = "block";
    document.getElementById(elt).style.display     = "block";
}

function viewAllRecords () {
    showElement("display_patients_table");

    var aaDataSet   = [];
    var aaColumnSet = [{'sTitle' : 'ID'},
		      {'sTitle' : 'Name'},
		      {'sTitle' : 'Age', 'sClass' : "center"},
		      {'sTitle' : 'Regn. Date'},
		      {'sTitle' : 'Doctors Seen'},
		      {'sTitle' : 'Last Visit'},
		      {'sTitle' : 'Visit Count', 'sClass' : "center"},
		      {'sTitle' : 'Phone No.'},
		      {'sTitle' : 'Postal Address'}];

    withDB(function(db) {
	var txn   = db.transaction(["patients"], IDBTransaction.READ_WRITE);
	var store = txn.objectStore("patients");

	var keyRange      = IDBKeyRange.lowerBound(0);
	var cursorRequest = store.openCursor(keyRange);

	console.log("cursorRequest.onsuccess...");

	cursorRequest.onsuccess = function(e) {
	    var result = e.target.result;
	    if(!!result == false) {
		console.log('Returning from here')
		return false;
	    }

	    console.log("Found: " + result.value.name);
	    item = [result.value.id,        result.value.name,  result.value.age, 
		    result.value.reg_date,  result.value.docs,  result.value.last_visit,
		    result.value.visit_cnt, result.value.phone, result.value.addr];
	    aaDataSet.push(item);
	    console.log('item    : ' + item);
	    console.log('dataset : ' + aaDataSet);
	    result.continue();
	};
	cursorRequest.onerror = logerr;
	
	$("#display_patients_table").dataTable({"aaData"    : aaDataSet,
						"aoColumns" : aaColumnSet});

	return false;
    })
    return false;
}

function createNewRecord (event) {
    var f_name     = $("#new_name").val();
    var f_age      = $("#new_age").val();
    var f_reg_date = $("#new_reg_date").val();
    var f_phone    = $("#new_phone").val();
    var f_addr     = $("#new_addr").val();
    var f_doc      = $("#new_doc").val();

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

    var key = dbName + "_patients_cnt";
    var f_id = parseInt(window.localStorage.getItem(key)) + 1

    console.log('Storing rec for ' + f_name + ' to DB with id: ' + f_id);

    withDB(function(db) {
	try {
	    var trans = db.transaction(["patients"], IDBTransaction.READ_WRITE);
	    var store = trans.objectStore("patients");

	    var record = {
		"id"       : f_id,
		"name"     : f_name,
		"age"      : f_age,
		"reg_date" : f_reg_date,
		"phone"    : f_phone,
		"addr"     : f_addr,
		"docs"     : [f_doc], // Can see diff doctors on diff days
		"visit_cnt"  : 0,
		"last_visit" : f_reg_date,
	    }
	    var req = store.add(record);
	    req.onerror = logerr;
	    req.onsuccess = function () {
		console.log("Hurrah!");
		window.localStorage.setItem(key, f_id);
		return false;
	    }
	} catch (e) {
	    console.log('fuxkeed');
	    return false;
	}
    });
    return false;
}  

function addHandlerToElement (elt, event, hdlr) {
    console.log(elt);
    if (elt.addEventListener)
	elt.addEventListener(event, hdlr, false);
    else
	elt.attachEvent(event, hdlr);
}

// Register callbacks to handle specific events on our main UI.
function addFormHandlers () {
    addHandlerToElement(document.getElementById("dispatch_new_p"),
			"click", getNewPatientData);

    addHandlerToElement(document.getElementById("new_patient_form"),
			"submit", createNewRecord);

    addHandlerToElement(document.getElementById("view_all_p"),
			"click", viewAllRecords);

//    var bal = $("controls:input[id=new_record]").submit(createNewRecord);
}

function onLoad () {
    // Initialize the database if available
    withDB(initdb);
    addFormHandlers();
}

jQuery(onLoad);
