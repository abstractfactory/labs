angular.module('ContactsApp', ['ngRoute', 'ngResource'])
	.config(function($routeProvider, $locationProvider) {
		// Provide an overview of contacts available in our application
		$routeProvider
			.when('/contacts', {
				controller: 'ListCtrl',
				templateUrl: 'views/list.html'
			})
			.when('/contact/new', {
				controller: 'NewController',
				templateUrl: 'views/new.html'
			});

		// Remove the # from urls, as HTML5 is capable of dynamically
		// switching URLs and thus won't need the hash-bang.
		$locationProvider.html5Mode(true);
	});
	