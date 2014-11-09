"use strict";

/*global Qt, model, fs, Filesystem, window, Screen*/


var color = {
    background: Qt.rgba(0.4, 0.4, 0.4)
};

var init = function () {
    console.log("Initializing..");

    fs.listdir("").forEach(function (item) {
        model.append({path: item});
    });
};