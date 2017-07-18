
(function () {
    'use strict';

    angular
        .module('phd.statistics.controllers')
        .controller('StatisticsController', StatisticsController);

    StatisticsController.$inject = ['Authentication', '$location', 'Toast', 'Statistics', 'Application'];

    function StatisticsController(Authentication, $location, Toast, Statistics, Application) {

        // If the user is not authenticated, they should not be here.
        if (!Authentication.isAuthenticated()) {
            $location.url('/login');
            return;
        }

        var vm = this;

        vm.ratioStatisticsField = ["gender", "status", "origin", "student_type"];
        getRatioStatistics(undefined, vm.ratioStatisticsField);
        getStaffStatistics();
        getApplicationsStatistics(undefined);

        // Fill list of available academic years
        Application.getAllAcademicYears().then(function success(response){
            vm.academicYears = response.data.academic_years;
            var defaultAcademicYear = Application.findDefaultAcademicYear(vm.academicYears);
            vm.selectedAcademicYearId = defaultAcademicYear.id;
            vm.academicYears.push({id: "all", name: "All"});
        }, Toast.showHttpError);

        vm.onAcademicYearChange = function(){
            getRatioStatistics(vm.selectedAcademicYearId, vm.ratioStatisticsField);
            getApplicationsStatistics(vm.selectedAcademicYearId);
        };

        // Various chart options
        vm.chartOptions = {
            animation: false,
            legend: {display: true, position: "bottom", labels: {boxWidth: 15, fontSize: 10}}
        };

        function getRatioStatistics(academicYearId, ratioStatisticsField){
            Statistics.getRatioStatistics(academicYearId, ratioStatisticsField).then(function success(response){
                for (var i=0; i<ratioStatisticsField.length; i++){
                    var field = ratioStatisticsField[i];
                    vm[field + "Series"] = response.data[field]["series"];
                    vm[field + "Labels"] = response.data[field]["labels"];
                    vm[field + "Data"] = response.data[field]["data"];
                }
            }, Toast.showHttpError);
        }

        function getStaffStatistics(){
            Statistics.getStaffStatistics().then(function success(response){
                vm.numberOfUsersToday = response.data["number_of_users_today"];
                vm.averageSupervisionsPerSupervisor = response.data["average_supervisions_per_supervisor"];
            }, Toast.showHttpError);
        }

        function getApplicationsStatistics(academicYearId){
            Statistics.getApplicationsStatistics(academicYearId).then(function success(response){

                vm.applicationPerDayLabels = response.data["applications_by_day"]["labels"];
                vm.applicationPerDaySeries = response.data["applications_by_day"]["series"];
                vm.applicationPerDayData = [response.data["applications_by_day"]["data"]];
            }, Toast.showHttpError)
        }
    }
})();