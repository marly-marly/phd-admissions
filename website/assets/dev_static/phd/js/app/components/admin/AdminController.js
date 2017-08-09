
(function () {
    'use strict';

    angular
        .module('phd.admin.controllers')
        .controller('AdminController', AdminController);

    AdminController.$inject = ['$location', 'Authentication'];

    function AdminController($location, Authentication) {

        // If the user is not authenticated, they should not be here.
        if (!Authentication.isAuthenticated()) {
            $location.url('/login');
        }

        // Check if the user is an admin
        var userDetails = Authentication.getAuthenticatedAccount();
        var userRole = userDetails.userRole;
        if (userRole !== 'ADMIN') {
            $location.url('/home');
        }
    }
})();