
(function () {
    'use strict';

    angular
        .module('phd.application.controllers')
        .controller('SupervisionController', SupervisionController);

    SupervisionController.$inject = ['$cookies', 'Application', 'Authentication'];

    function SupervisionController($cookies, Application, Authentication) {
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
                toastr.success("Comment was successfully posted!");
            }, displayErrorMessage);
        };

        vm.recommendationChange = function(){
            Application.updateSupervision(vm.supervision.id, copyFlattened(vm.supervision)).then(function success(){
                toastr.success("Supervision updated successfully");
            }, displayErrorMessage)
        };

        vm.allocateSupervision = function(){
            Application.allocateSupervision(vm.supervision.id).then(function success(){
                vm.supervision.allocated = true;
                toastr.success("Supervisor successfully allocated!")
            }, displayErrorMessage)
        };

        vm.deAllocateSupervision = function(){
            Application.deAllocateSupervision(vm.supervision.id).then(function success(){
                vm.supervision.allocated = false;
                toastr.success("Supervisor not allocated any longer.")
            }, displayErrorMessage)
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

        function displayErrorMessage(data){
            toastr.error(data.data.error, data.statusText + " " + data.status)
        }
    }
})();