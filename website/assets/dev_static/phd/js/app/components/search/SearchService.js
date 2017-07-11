
(function () {
    'use strict';

    angular
        .module('phd.search.services')
        .factory('Search', Search);

    Search.$inject = ['$http'];

    function Search($http) {

        return {
            getResults: getResults
        };

        function getResults(searchCriteria) {
            return $http.get('/api/applications/search/', {params: searchCriteria});
        }
    }
})();