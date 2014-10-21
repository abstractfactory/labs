/*global angular*/
"use strict";

angular.module("ContactsApp")
    .value("FieldTypes", {
        text:     ["Text",         "should be text"],
        email:    ["Email",        "should be an email address"],
        number:   ["Number",       "should be a number"],
        date:     ["Date",         "should be a date"],
        datetime: ["Datetime",     "should be a datetime"],
        time:     ["Time",         "should be a time"],
        month:    ["Month",        "should be a month"],
        week:     ["Week",         "should be a week"],
        url:      ["URL",          "should be a url"],
        tel:      ["Phone Number", "should be a tel"],
        color:    ["Color",        "should be a color"]
    })
    .directive("formField", function ($timeout, FieldTypes) {
        return {
            restrict: "A",
            templateUrl: "static/views/form-field.html",
            replace: true,
            scope: {
                record: "=",  // Two-way binding
                field: "@",   // One-way binding
                live: "@",
                required: "@"
            },
            link: function (scope, element, attr) {
                scope.$on("record:invalid", function () {
                    scope[scope.field].$setDirty();
                });

                scope.types = FieldTypes;
                scope.remove = function (field) {
                    delete scope.record[field];
                    scope.blurUpdate();
                };

                scope.blurUpdate = function () {
                    // This function actually writes to the database
                    if (scope.live !== "false") {
                        scope.record.$update(function (updatedRecord) {
                            scope.record = updatedRecord;
                        });
                    }
                };

                // Any time the user hits a key, a timeout will be triggered.
                // The timer is reset anytime a key is hit.
                var saveTimeout;
                scope.update = function () {
                    $timeout.cancel(saveTimeout);
                    saveTimeout = $timeout(scope.blurUpdate, 1000);
                };
            }
        };
    })
    .directive("newField", function ($filter, FieldTypes) {
        return {
            restrict: "A",
            templateUrl: "static/views/new-field.html",
            replace: true,
            scope: {
                record: "=",
                live: "@"
            },
            require: "^form",
            link: function (scope, element, attr, form) {
                scope.types = FieldTypes;
                scope.field = {};

                scope.show = function (type) {
                    scope.field.type = type;
                    scope.display = true;
                };

                scope.remove = function () {
                    scope.field = {};
                    scope.display = false;
                };

                scope.add = function () {
                    if (form.newField.$valid) {
                        var camelCase = $filter("camelCase")(scope.field.name);
                        // Store as array, to match our FieldTypes schema above
                        scope.record[camelCase] = [scope.field.value, scope.field.type];
                        scope.remove();

                        if (scope.live !== "false") {
                            scope.record.$update(function (updatedRecord) {
                                scope.record = updatedRecord;
                            });
                        }
                    }
                };
            }
        };
    });