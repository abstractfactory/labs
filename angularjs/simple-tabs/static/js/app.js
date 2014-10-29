"use strict";
/*global angular*/

(function () {

    var app = angular.module("awesomeApp", ["ngRoute"]);

    app.config(function ($routeProvider, $locationProvider) {
        $routeProvider
            .when("/tabs", {
                templateUrl: "static/views/tabs.html",
            })
            .when("/about", {
                templateUrl: "static/views/about.html"
            })
            .otherwise("/");

        $locationProvider.html5Mode(true);
    });

    app.controller("NavigationController", function () {
        this.pages = [
            ["Home", "/"],
            ["Tabs", "/tabs"],
            ["About", "/about"]
        ];
    });

    app.controller("TabController", function () {
        this.tabs = [
            "Tab 1",
            "Tab 2",
            "Tab 3",
        ];

        this.active = "Tab 1";

        this.setTab = function (tab) {
            this.active = tab;
        };

        this.isActive = function (tab) {
            return this.active === tab;
        };
    });

    app.directive("aaContentTabs", function () {
        return {
            restrict: "E",
            templateUrl: "static/templates/content-tabs.html",
            controller: "TabController",
            controllerAs: "tabCtrl"
        };
    });

    app.directive("aaNavigation", function () {
        return {
            restrict: "E",
            templateUrl: "static/templates/navigation.html",
            controller: "NavigationController",
            controllerAs: "navCtrl"
        };
    });

}());