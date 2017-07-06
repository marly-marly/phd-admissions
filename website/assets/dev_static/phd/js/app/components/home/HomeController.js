
(function () {
    'use strict';

    angular
        .module('phd.home.controllers')
        .controller('IndexController', IndexController);

    IndexController.$inject = ['Home', 'Authentication', '$location', 'Toast'];

    function IndexController(Home, Authentication, $location, Toast) {

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
            vm.username = userDetails.username;
        }

        vm.currentAcademicYear = "";
        Home.getStatistics().then(function success(response){
            vm.numberOfApplications = response.data["number_of_applications"];
            vm.currentAcademicYear = response.data["current_academic_year"];
        }, function error(data){

            // If the cause of the error is the lack of default academic year, trigger warning instead of error.
            if (data.data.hasOwnProperty("current_academic_year")){
                if (data.data.current_academic_year == 0){
                    vm.currentAcademicYear = undefined;
                }
            }else{
                Toast.showHttpError(data);
            }
        });
    }
})();