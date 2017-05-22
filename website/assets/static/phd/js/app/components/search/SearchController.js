
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
        });

        // Manage GET query parameters from the URL
        var getQueryParams = $location.search();
        var hasParams = Boolean(Object.keys(getQueryParams).length);
        if (hasParams){
            vm.searchOptions = getQueryParams;

            // Populate checkBoxSelection
            for (var key in getQueryParams) {
                if (getQueryParams.hasOwnProperty(key)) {
                    vm.checkBoxSelection[key] = {};
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

            // Search for specific applications
            Search.getResults(vm.searchOptions).then(function(response){
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
                Search.getResults({}).then(function (response) {
                    vm.searchResults = response.data["applications"];
                });
            }else{
                $location.url('/search?' + qs);
            }
        }
    }
})();