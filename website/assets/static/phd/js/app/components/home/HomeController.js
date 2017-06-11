
(function () {
    'use strict';

    angular
        .module('phd.home.controllers')
        .controller('IndexController', IndexController);

    IndexController.$inject = ['Home', 'Authentication', '$location'];

    function IndexController(Home, Authentication, $location) {

        // If the user is not authenticated, they should not be here.
        if (!Authentication.isAuthenticated()) {
            $location.url('/login');
            return;
        }

        var vm = this;

        // User account details
        var userDetails = Authentication.getAuthenticatedAccount();
        if (userDetails != undefined){
            var userRole = userDetails.userRole;
            vm.isAdmin = userRole === 'ADMIN';
        }

        Home.getStatistics().then(function(response){
            vm.numberOfApplications = response.data["number_of_applications"];
        });

    }
})();