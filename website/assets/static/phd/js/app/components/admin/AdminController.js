
(function () {
    'use strict';

    angular
        .module('phd.admin.controllers')
        .controller('AdminController', AdminController);

    AdminController.$inject = ['$scope', '$location', '$cookies', 'Admin', '$routeParams'];

    function AdminController($scope, $location, $cookies, Admin, $routeParams) {
        var vm = this;

        vm.staffMembers = [];
        vm.newRole = undefined;

        Admin.getAllStaffMembers().then(function success(response){
            vm.staffMembers = response.data;
        }, displayErrorMessage);

        vm.selectRow = function(data){
            data.selected = !data.selected;
        };

        vm.selectAllRows = function(){
            vm.allRowSelection = !vm.allRowSelection;
            for (var i=0; i<vm.staffMembers.length; i++){
                vm.staffMembers[i].selected = vm.allRowSelection;
            }
        };

        vm.deselectAllRows = function(){
            vm.allRowSelection = false;
            for (var i=0; i<vm.staffMembers.length; i++){
                vm.staffMembers[i].selected = vm.allRowSelection;
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
                vm.deselectAllRows();
            }, displayErrorMessage)
        };

        function displayErrorMessage(data){
            toastr.error(data.data.error, data.statusText + " " + data.status)
        }
    }
})();