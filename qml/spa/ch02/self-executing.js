"use strict";
// Self-executing function

var namespace = (function () {
    var variableA = "A",
        variableB = "B",
        unaccessible = "X";

    return {
        variableA: variableA,
        variableB: variableB
    };
}());

console.log(namespace.variableB);