
(function () {
    'use strict';

    angular
        .module('phd.search.services')
        .factory('Search', Search);

    Search.$inject = ['$http'];

    function Search($http) {

        var Search = {
            getResults: getResults,
            getApplicationFields: getApplicationFields
        };

        return Search;

        function getResults(searchOptions) {
            var application_data = {
                registry_ref: searchOptions.registryRef,
                surname: searchOptions.surname,
                forename: searchOptions.forename,
                possible_funding: searchOptions.possible_funding,
                funding_status: searchOptions.funding_status,
                origin: searchOptions.origin,
                student_type: searchOptions.student_type
            };

            return $http.get('/api/applications/search/', {params: application_data});
        }

        function getApplicationFields(){
            return $http.get('/api/applications/application_fields/');
        }
    }
})();