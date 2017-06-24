
(function () {
    'use strict';

    angular
        .module('phd.admin.controllers')
        .controller('StaffController', StaffController);

    StaffController.$inject = ['$location', 'Admin', 'Authentication', '$filter'];

    function StaffController($location, Admin, Authentication, $filter) {

        // If the user is not authenticated, they should not be here.
        if (!Authentication.isAuthenticated()) {
            $location.url('/login');
            return;
        }

        var vm = this;

        var userDetails = Authentication.getAuthenticatedAccount();
        vm.username = userDetails.username;

        vm.staffMembers = [];
        vm.newRole = "SUPERVISOR";

        getAllStaffMembers();

        vm.selectStaffRow = function(data){
            data.selected = !data.selected;
        };

        vm.selectAllStaffRows = function(){
            vm.allStaffRowSelection = !vm.allStaffRowSelection;
            for (var i=0; i<vm.staffMembers.length; i++){
                vm.staffMembers[i].selected = vm.allStaffRowSelection;
            }
        };

        vm.deselectAllStaffRows = function(){
            vm.allStaffRowSelection = false;
            for (var i=0; i<vm.staffMembers.length; i++){
                vm.staffMembers[i].selected = vm.allStaffRowSelection;
            }
        };

        vm.changeRoles = function(){
            var newUseRoles = {};

            for (var i=0; i<vm.staffMembers.length; i++){
                if (vm.staffMembers[i].selected){
                    newUseRoles[vm.staffMembers[i].username] = vm.newRole;
                }
            }

            Admin.changeRoles(newUseRoles).then(function success(){
                var toastMessage = "";
                for (var key in newUseRoles){
                    if (newUseRoles.hasOwnProperty(key)){
                        toastMessage += "- " + key + "<br>";
                    }
                }

                toastMessage = "Changed to " + vm.newRole + "<br>" + toastMessage;
                toastr.options.escapeHtml = false;
                toastr.success(toastMessage, "Success");

                for (var i=0; i<vm.staffMembers.length; i++){
                    if (vm.staffMembers[i].selected){
                        vm.staffMembers[i].role.name = vm.newRole;
                    }
                }
                vm.newRole = undefined;
                vm.deselectAllStaffRows();
            }, displayErrorMessage)
        };

        vm.syncStaff = function(){
            Admin.syncStaff().then(function success(){
                toastr.success("Successfully synchronised!");

                getAllStaffMembers();
            }, displayErrorMessage)
        };

        function getAllStaffMembers(){
            Admin.getAllStaffMembers().then(function success(response){
                vm.staffMembers = response.data;
            }, displayErrorMessage);
        }

        function displayErrorMessage(data){
            toastr.error(data.data.error, data.statusText + " " + data.status)
        }
    }
})();