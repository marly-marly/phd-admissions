
(function () {
    'use strict';

    angular
        .module('phd.navbar.controllers')
        .controller('NavbarController', NavbarController);

    NavbarController.$inject = ['$scope', '$http', 'Authentication', '$location'];

    function NavbarController($scope, $http, Authentication, $location) {
        var vm = this;

        var userDetails = Authentication.getAuthenticatedAccount();
        if (userDetails != undefined){
            vm.user = userDetails.username;
            vm.userRole = userDetails.userRole;
        }
        vm.isAuthenticated = Authentication.isAuthenticated();
        vm.logout = logout;
        vm.isActive = isActive;


        function logout() {
            Authentication.logout();
        }

        function isActive(viewLocation) {
            return viewLocation === $location.path();
        }
    }
})();