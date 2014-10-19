"use strict";
/*global angular*/

angular.module("myApp")
    .controller("myCtrl", function ($scope) {
        console.log(Object.keys($scope));
        $scope.record = "London";
    });