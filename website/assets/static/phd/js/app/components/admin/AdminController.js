
(function () {
    'use strict';

    angular
        .module('phd.admin.controllers')
        .controller('AdminController', AdminController);

    AdminController.$inject = ['$location', 'Admin', 'Authentication'];

    function AdminController($location, Admin, Authentication) {

        // If the user is not authenticated, they should not be here.
        if (!Authentication.isAuthenticated()) {
            $location.url('/login');
            return;
        }

        var vm = this;

        vm.staffMembers = [];
        vm.academicYears = [];
        vm.newRole = undefined;
        vm.newAcademicYear = {};

        Admin.getAllStaffMembers().then(function success(response){
            vm.staffMembers = response.data;
        }, displayErrorMessage);

        Admin.getAllAcademicYears().then(function success(response){
            // Convert date strings to date objects
            for (var i=0; i<response.data.academic_years.length; i++){
                response.data.academic_years[i].start_date = new Date(response.data.academic_years[i].start_date);
                response.data.academic_years[i].end_date = new Date(response.data.academic_years[i].end_date);
            }

            vm.academicYears = response.data.academic_years;
        }, displayErrorMessage);

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

        vm.selectYearRow = function(data){
            data.selected = !data.selected;
        };

        vm.selectAllYearRows = function(){
            vm.allYearRowSelection = !vm.allYearRowSelection;
            for (var i=0; i<vm.academicYears.length; i++){
                vm.academicYears[i].selected = vm.allYearRowSelection;
            }
        };

        vm.deselectAllYearRows = function(){
            vm.allYearRowSelection = false;
            for (var i=0; i<vm.academicYears.length; i++){
                vm.academicYears[i].selected = vm.allYearRowSelection;
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

        vm.uploadNewAcademicYear = function(){

            // If this is the first academic year uploaded, mark it as default
            if (vm.academicYears.length === 0){
                vm.newAcademicYear.default = true;
            }

            Admin.uploadNewAcademicYear(vm.newAcademicYear).then(function success(){
                vm.academicYears.push(vm.newAcademicYear);
                vm.newAcademicYear = {};
                toastr.success("New academic year has been added!");
            }, displayErrorMessage)
        };

        vm.updateAcademicYear = function(academicYear){
            Admin.updateAcademicYear(academicYear).then(function success(){
                academicYear.editable = false;

                toastr.success("Updated successfully!")
            }, displayErrorMessage)
        };

        vm.editAcademicYear = function(academicYear){
            academicYear.editable = true;
        };

        vm.closeAcademicYearEditing = function(academicYear){
            academicYear.editable = false;
        };

        vm.markAcademicYearDefault = function(academicYear){
            Admin.markAcademicYearDefault(academicYear).then(function success(){
                toastr.success("Saved!");
                for (var i=0; i<vm.academicYears.length; i++){
                    vm.academicYears[i].default = false;
                }
                academicYear.default = true;
            }, displayErrorMessage)
        };

        function displayErrorMessage(data){
            toastr.error(data.data.error, data.statusText + " " + data.status)
        }
    }
})();