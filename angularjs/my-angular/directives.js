"use strict";
/*global angular*/

angular.module('myApp', [])
    .directive('moSparkline', function () {
        return {
            restrict: 'EA',
            replace: true,
            scope: {
                record: "="
            },
            templateUrl: 'sparkline.html'
        };
    });