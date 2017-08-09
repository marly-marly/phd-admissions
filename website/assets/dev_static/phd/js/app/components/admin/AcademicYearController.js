
(function () {
    'use strict';

    angular
        .module('phd.admin.controllers')
        .controller('AcademicYearController', AcademicYearController);

    AcademicYearController.$inject = ['$location', 'Admin', 'Authentication', 'Toast'];

    function AcademicYearController($location, Admin, Authentication, Toast) {

       // If the user is not authenticated, they should not be here.
        if (!Authentication.isAuthenticated()) {
            $location.url('/login');
            return;
        }

        // Check if the user is an admin
        var userDetails = Authentication.getAuthenticatedAccount();
        var userRole = userDetails.userRole;
        if (userRole !== 'ADMIN') {
            $location.url('/home');
        }

        var vm = this;
        vm.username = userDetails.username;

        vm.academicYears = [];
        vm.newAcademicYear = {};

        // Set the default start-date to 01 October this year
        vm.newAcademicYear.start_date = new Date();
        vm.newAcademicYear.start_date.setMonth(9);
        vm.newAcademicYear.start_date.setDate(1);

        // Set the default end-date to 30 September next year
        vm.newAcademicYear.end_date = new Date();
        vm.newAcademicYear.end_date.setFullYear(vm.newAcademicYear.end_date.getFullYear()+1);
        vm.newAcademicYear.end_date.setMonth(8);
        vm.newAcademicYear.end_date.setDate(30);

        Admin.getAllAcademicYears().then(function success(response){
            // Convert date strings to date objects
            for (var i=0; i<response.data.academic_years.length; i++){
                response.data.academic_years[i].start_date = new Date(response.data.academic_years[i].start_date);
                response.data.academic_years[i].end_date = new Date(response.data.academic_years[i].end_date);
            }

            vm.academicYears = response.data.academic_years;
        }, Toast.showHttpError);

        // Deal with date picker incompatibility when document is ready
        $(function () {
            if ($('[type="date"]').prop('type') != 'date') {
            // If not native HTML5 support, fallback to jQuery datePicker
                $('input[type=date]').datepicker({
                    // Consistent format with the HTML5 picker
                        dateFormat : 'yy-mm-dd'
                    },
                    // Localization
                    $.datepicker.regional['uk']
                );
            }
        });

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

        vm.uploadNewAcademicYear = function(){

            // If this is the first academic year uploaded, mark it as default
            if (vm.academicYears.length === 0){
                vm.newAcademicYear.default = true;
            }

            Admin.uploadNewAcademicYear(vm.newAcademicYear).then(function success(response){
                var newYear = response.data.academic_year;
                newYear.start_date = new Date(newYear.start_date);
                newYear.end_date = new Date(newYear.end_date);
                vm.academicYears.push(newYear);
                vm.newAcademicYear = {};
                Toast.showSuccess("New academic year has been added!");
            }, Toast.showHttpError)
        };

        vm.updateAcademicYear = function(academicYear){
            Admin.updateAcademicYear(academicYear).then(function success(){
                academicYear.editable = false;

                Toast.showSuccess("Updated successfully!")
            }, Toast.showHttpError)
        };

        var tempAcademicYearMap = {};
        vm.editAcademicYear = function(academicYear){
            tempAcademicYearMap[academicYear.id] = angular.copy(academicYear);
            academicYear.editable = true;
        };

        vm.closeAcademicYearEditing = function(academicYear){
            academicYear.editable = false;
            angular.copy(tempAcademicYearMap[academicYear.id], academicYear);
        };

        vm.markAcademicYearDefault = function(academicYear){
            Admin.markAcademicYearDefault(academicYear).then(function success(){
                Toast.showSuccess("Saved!");
                for (var i=0; i<vm.academicYears.length; i++){
                    vm.academicYears[i].default = false;
                }
                academicYear.default = true;
            }, Toast.showHttpError)
        };
    }
})();