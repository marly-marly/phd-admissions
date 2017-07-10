
(function () {
    'use strict';

    angular
        .module('phd.admin.controllers')
        .controller('EmailTemplateController', EmailTemplateController);

    EmailTemplateController.$inject = ['$location', 'Admin', 'Authentication', 'Toast', '$scope'];

    function EmailTemplateController($location, Admin, Authentication, Toast, $scope) {

        // If the user is not authenticated, they should not be here.
        if (!Authentication.isAuthenticated()) {
            $location.url('/login');
            return;
        }

        var vm = this;

        Admin.getEmailTemplate().then(function success(response){
            vm.emailContent = response.data.value;
        }, Toast.showHttpError);

        vm.updateEmailContent = function(){
            Admin.updateEmailTemplate(vm.emailContent).then(function success(){
                Toast.showSuccess("Saved!")
            }, Toast.showHttpError)
        };

        vm.emailContentChanged = function(){
            return !!$scope.emailTemplateForm.$dirty;
        }
    }
})();