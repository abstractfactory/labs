/*
 * spa.util.js
 * General Javascript utilities
 *
*/

/*global Qt, QtQuick, window*/
"use strict";

var makeError, setConfigMap;

// Begin Public constructor /makeError/
// Purpose: a convenience wrapper to create an error object
// Arguments:
//  * name_text - the error name
//  * msg_text - long error message
//  * data - optional data attached to error object
// Returns : newly constructed error object
// Throws : none
//
makeError = function (name_text, msg_text, data) {
    var error = new Error();
    error.name = name_text;
    error.message = msg_text;

    if (data) { error.data = data; }

    return error;
};


/**
* Synchronously create component
*/
function createComponent(path, parent, properties) {
    var component,
        object,
        finishComponent;

    properties = typeof properties !== "undefined" ? properties : {};

    finishComponent = function () {
        object = component.createObject(parent, properties);
        if (object === null) {
            console.log("Error creating object");
        } else if (component.status === QtQuick.Component.Error) {
            console.log(component.errorString());
        }

    };

    component = Qt.createComponent(path);
    if (component.status === QtQuick.Component.Ready) {
        finishComponent();
    } else {
        component.statusChanged.connect(finishComponent);
    }

    return component;
}
