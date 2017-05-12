
(function () {
    'use strict';

    angular
        .module('phd.search.services')
        .factory('Search', Search);

    Search.$inject = ['$http'];

    function Search($http) {

        var Search = {
            getResults: getResults
        };

        return Search;

        function getResults(searchOptions) {
            var application_data = {
                registry_ref: searchOptions.registryRef,
                surname: searchOptions.surname,
                forename: searchOptions.forename,
                possible_funding: searchOptions.possibleFunding,
                funding_status: searchOptions.fundingStatus,
                origin: searchOptions.origin,
                student_type: searchOptions.studentType,
            };

            return $http.get('/api/applications/search/', application_data);
        }
    }
})();