"use strict";
/*global angular*/

angular.module('ContactsApp')
    .controller('ListCtrl', function ($scope,
                                      $rootScope,
                                      Contact,
                                      $location) {
        // Global variable for navigation.
        // This will be the ONLY global variable we'll make.
        $rootScope.PAGE = "all";
        $scope.contacts = Contact.query();
        $scope.fields = ['firstName', 'lastName'];

        $scope.sort = function (field) {
            $scope.sort.field = field;
            $scope.sort.order = !$scope.sort.order;
        };

        $scope.sort.field = 'firstName';
        $scope.sort.order = false;

        $scope.show = function (id) {
            $location.url('/contact/' + id);
        };
    })
    .controller("NewCtrl", function ($scope,
                                     $rootScope,
                                     Contact,
                                     $location) {
        $rootScope.PAGE = "new";
        $scope.contact = new Contact({
            firstName:  ["", "text"],
            lastName:   ["", "text"],
            email:      ["", "email"],
            homePhone:  ["", "tel"],
            cellPhone:  ["", "tel"],
            birthday:   ["", "date"],
            website:    ["", "url"],
            address:    ["", "text"]
        });

        $scope.save = function () {
            if ($scope.newContact.$invalid) {
                $scope.$broadcast("record:invalid");
            } else {
                $scope.contact.$save();
                $location.url("/contacts");
            }
        };
    })
    .controller("SingleCtrl", function ($scope,
                                        $rootScope,
                                        $location,
                                        Contact,
                                        $routeParams) {
        $rootScope.PAGE = "single";
        $scope.contact = Contact.get({ id: parseInt($routeParams.id, 10) });
        $scope.delete = function () {
            $scope.contact.$delete();
            $location.url("/contacts");
        };
    });