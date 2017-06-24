
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
    }
})();