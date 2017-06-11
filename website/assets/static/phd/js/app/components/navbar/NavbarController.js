
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
            vm.username = userDetails.username;
            vm.userRole = userDetails.userRole;
            vm.isAdmin = vm.userRole === 'ADMIN';
        }

        vm.isAuthenticated = Authentication.isAuthenticated();
        vm.logout = logout;
        vm.isActive = isActive;

        function logout() {
            Authentication.logout();
        }

        function isActive(viewLocation) {
            return $location.path().includes(viewLocation);
        }
    }
})();