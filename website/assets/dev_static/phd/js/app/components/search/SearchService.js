
(function () {
    'use strict';

    angular
        .module('phd.search.services')
        .factory('Search', Search);

    Search.$inject = ['$http'];

    function Search($http) {

        return {
            getResults: getResults,
            getApplicationFields: getApplicationFields
        };

        function getResults(searchCriteria) {
            return $http.get('/api/applications/search/', {params: searchCriteria});
        }

        function getApplicationFields(){
            return $http.get('/api/applications/application_fields/');
        }
    }
})();