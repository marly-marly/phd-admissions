
(function () {
    'use strict';

    angular
        .module('phd.search.controllers')
        .controller('SearchController', SearchController);

    SearchController.$inject = ['$scope', 'Search', 'Application'];

    function SearchController($scope, Search, Application) {
        var vm = this;
        vm.searchOptions = {};
        vm.searchResults = [];

        vm.checkBoxSelection = {};

        Application.getApplicationFieldChoices().then(function(response){
            vm.searchFieldOptions = response.data;
            for (var key in vm.searchFieldOptions) {
                if (vm.searchFieldOptions.hasOwnProperty(key)) {
                    vm.checkBoxSelection[key] = {};
                }
            }
        });

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

            Search.getResults(vm.searchOptions).then(function(response){
                vm.searchResults = response.data["applications"];
            })
        }
    }
})();