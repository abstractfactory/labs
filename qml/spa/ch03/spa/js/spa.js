/*
* spa.js
* Root namespace module
*/

/*global Qt, window*/


"use strict";

var initModule = function () {
    Qt.createQmlObject("import QtQuick 2.0; Text { x: 100; y: 100; text: \"Hello World\"; font.pointSize: 23}", window);
};
