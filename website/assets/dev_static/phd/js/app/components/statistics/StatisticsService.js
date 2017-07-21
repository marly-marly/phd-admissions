
(function () {
    'use strict';

    angular
        .module('phd.statistics.services')
        .factory('Statistics', Statistics);

    Statistics.$inject = ['$http'];

    function Statistics($http) {
        return {
            getStatistics: getStatistics,
            getRatioStatistics: getRatioStatistics,
            getStaffStatistics: getStaffStatistics,
            getApplicationsStatistics: getApplicationsStatistics
        };

        function getStatistics(){
            return $http.get('/api/applications/statistics/');
        }

        function getRatioStatistics(academicYearId, fields){
            return $http.get('/api/applications/statistics/ratios/', {params: {academic_year_id: academicYearId, fields: fields}});
        }

        function getStaffStatistics(){
            return $http.get('/api/applications/statistics/staff/');
        }

        function getApplicationsStatistics(academicYearId, historyType){
            return $http.get('/api/applications/statistics/applications/', {params: {academic_year_id: academicYearId, history_type: historyType}});
        }
    }
})();