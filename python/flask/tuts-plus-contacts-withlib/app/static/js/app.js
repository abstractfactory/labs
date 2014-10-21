"use strict";
/*global angular*/

angular.module("ContactsApp", ["ngRoute", "ngResource", "ngMessages"])
    .config(function ($routeProvider, $locationProvider) {
        // Provide an overview of contacts available in our application
        $routeProvider
            .when("/contacts", {
                controller: "ListCtrl",
                templateUrl: "static/views/list.html"
            })
            .when("/contact/new", {
                controller: "NewCtrl",
                templateUrl: "static/views/new.html"
            })
            .when("/contact/:id", {
                controller: "SingleCtrl",
                templateUrl: "static/views/single.html"
            });

        // Remove the # from urls, as HTML5 is capable of dynamically
        // switching URLs and thus won"t need the hash-bang.
        $locationProvider.html5Mode(true);
    });
