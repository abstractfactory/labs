"use strict";
/*global angular*/

angular.module("ContactsApp")
    .value("FieldTypes", {
        text:       ["Text",            "should be text"],
        email:      ["Email",           "should be an email address"],
        number:     ["Number",          "should be a number"],
        date:       ["Date",            "should be a date"],
        datetime:   ["Datetime",        "should be a datetime"],
        time:       ["Time",            "should be a time"],
        month:      ["Month",           "should be a month"],
        week:       ["Week",            "should be a week"],
        url:        ["URL",             "should be a url"],
        tel:        ["Phone Number",    "should be a tel"],
        color:      ["Color",           "should be a color"]
    })
    .directive("formField", function ($timeout, FieldTypes) {
        return {
            restrict: "EA",
            templateUrl: "views/form-field.html",
            replace: true,
            scope: {
                record: "=", // A two-way binding
                field: "@",  // A one-way binding
                live: "@",
                required: "@"
            },

            // Unused variables ok
            link: function ($scope, element, attr) {
                $scope.$on("record:invalid", function () {
                    $scope[$scope.field].$setDirty();
                });

                $scope.types = FieldTypes;
                $scope.remove = function (field) {
                    delete $scope.record[field];
                    $scope.blurUpdate();
                };

                $scope.blurUpdate = function () {
                    if ($scope.live !== "false") {
                        $scope.record.$update(function (updatedRecord) {
                            $scope.record = updatedRecord;
                        });
                    }
                };

                var saveTimeout;
                $scope.update = function () {
                    $timeout.cancel(saveTimeout);
                    saveTimeout = $timeout($scope.blurUpdate, 1000);
                };
            }
        };
    });