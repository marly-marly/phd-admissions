
(function () {
    'use strict';

    angular
        .module('phd.application.controllers')
        .controller('SupervisionController', SupervisionController);

    SupervisionController.$inject = ['$cookies', 'Application', 'Authentication', 'Toast', 'Email'];

    function SupervisionController($cookies, Application, Authentication, Toast, Email) {
        var vm = this;

        vm.access_token = $cookies.get('token');
        var userDetails = Authentication.getAuthenticatedAccount();
        if (userDetails != undefined){
            vm.username = userDetails.username;
            vm.userRole = userDetails.userRole;
            vm.isAdmin = vm.userRole === 'ADMIN';
        }

        vm.supervisorComment = "";
        vm.postComment = function(){
            Application.postComment(vm.supervision.id, vm.supervisorComment).then(function(response){
                var newComment = response.data;
                vm.supervision.comments.push(newComment);
                vm.supervisorComment = "";

                $uibModalInstance.close();
                Toast.showSuccess("Comment was successfully posted!");
            }, Toast.showHttpError);
        };

        vm.recommendationChange = function(){
            Application.updateSupervision(vm.supervision.id, copyFlattened(vm.supervision)).then(function success(){
                Toast.showSuccess("Supervision updated successfully");
            }, Toast.showHttpError)
        };

        vm.allocateSupervision = function(){
            Application.allocateSupervision(vm.supervision.id).then(function success(){
                vm.supervision.allocated = true;
                Toast.showSuccess("Supervisor successfully allocated!")
            }, Toast.showHttpError)
        };

        vm.deAllocateSupervision = function(){
            Application.deAllocateSupervision(vm.supervision.id).then(function success(){
                vm.supervision.allocated = false;
                Toast.showSuccess("Supervisor not allocated any longer.")
            }, Toast.showHttpError)
        };

        vm.loadEmailContent = function(){
            Email.getGeneratedEmailPreview(vm.supervision.id).then(function success(response){
                vm.emailContent = response.data;
            }, Toast.showHttpError);
        };

        function copyFlattened(object){
            var copiedObject = angular.copy(object);
            for (var key in copiedObject){
                if (copiedObject.hasOwnProperty(key)){
                    if (typeof copiedObject[key] === "object"){
                        delete copiedObject[key];
                    }
                }
            }

            return copiedObject;
        }
    }
})();