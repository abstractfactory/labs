"use strict";
/*global angular*/


angular.module("ContactsApp")
    .factory("Contact", function ($resource) {
        return $resource("/api/contact/:id", { id: "@id" }, {
            'update': { method: 'PUT' }
        });
    });