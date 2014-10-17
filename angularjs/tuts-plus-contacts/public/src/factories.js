app = angular.module("ContactsApp");

app.factory("Contact", function ($resource) {
	return $resource("/api/contact/:id", { id: "@id" }, {
		'update': { method: 'PUT' }
	});
});