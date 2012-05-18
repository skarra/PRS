// 
// Created       : Sat May 05 13:15:20 IST 2012
// Last Modified : Fri May 18 22:33:10 IST 2012
//
// Copyright (C) 2012, Sriram Karra <karra.etc@gmail.com>
// All Rights Reserved
//
// Licensed under the GNU GPL v3
// 

function addHandlers () {
    console.log('addFormHandlers');

    $("#new_submit").submit(function () {
	
    })
}

function onLoad () {
    console.log('jQuery.onLoad(): Howdy dowdy');
    addHandlers();
}

jQuery(onLoad);
