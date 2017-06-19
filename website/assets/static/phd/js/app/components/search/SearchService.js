
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
            return $http.get('/api/applications/search/', {params: searchOptions});
        }

        function getApplicationFields(){
            return $http.get('/api/applications/application_fields/');
        }
    }
})();