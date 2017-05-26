
(function () {
    'use strict';

    angular
        .module('phd.search.controllers')
        .controller('SearchController', SearchController);

    SearchController.$inject = ['$scope', '$location', '$httpParamSerializer', 'Search', 'Application'];

    function SearchController($scope, $location, $httpParamSerializer, Search, Application) {
        var vm = this;
        vm.searchOptions = {};
        vm.searchResults = [];
        vm.checkBoxSelection = {};

        Application.getApplicationFieldChoices().then(function(response){
            vm.searchFieldOptions = response.data;
            for (var key in vm.searchFieldOptions) {
                if (vm.searchFieldOptions.hasOwnProperty(key)) {
                    if (typeof vm.checkBoxSelection[key] === "undefined"){
                        vm.checkBoxSelection[key] = {};
                    }
                }
            }

            // TODO: Loading circle here

            // Manage GET query parameters from the URL
            var getQueryParams = $location.search();
            var hasParams = Boolean(Object.keys(getQueryParams).length);
            if (hasParams){

                // Conduct search
                vm.searchOptions = getQueryParams;
                search(vm.searchOptions);

                // Populate checkBoxSelection
                for (key in vm.searchFieldOptions) {
                    if (vm.searchFieldOptions.hasOwnProperty(key)) {
                        vm.checkBoxSelection[key] = {};
                        if (key in getQueryParams){
                            var value = getQueryParams[key];
                            if (value.constructor === Array){
                                for (var i=0; i<value.length; i++){
                                    vm.checkBoxSelection[key][value[i]] = true;
                                }
                            }else{
                                vm.checkBoxSelection[key][value] = true;
                            }
                        }
                    }
                }
            }
        });

        // Search for specific applications
        function search(options){
            Search.getResults(options).then(function(response){
                vm.searchResults = response.data["applications"];
            })
        }

        vm.search = function(){
            for (var key in vm.checkBoxSelection) {
                if (vm.checkBoxSelection.hasOwnProperty(key)) {
                    vm.searchOptions[key] = [];
                    var category = vm.checkBoxSelection[key];
                    for (var subKey in category) {
                        if (category.hasOwnProperty(subKey)) {
                            if (category[subKey]){
                                vm.searchOptions[key].push(subKey);
                            }
                        }
                    }
                }
            }

            // Navigate to a new page to conduct the search
            var qs = $httpParamSerializer(vm.searchOptions);
            if (qs === "") {

                // Search for all applications
                search({});
            }else{
                $location.url('/search?' + qs);
            }
        }
    }
})();