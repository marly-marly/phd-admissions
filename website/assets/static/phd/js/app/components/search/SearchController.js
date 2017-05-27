
(function () {
    'use strict';

    angular
        .module('phd.search.controllers')
        .controller('SearchController', SearchController);

    SearchController.$inject = ['$scope', '$location', '$httpParamSerializer', 'Search', 'Application', '$window', '$cookies'];

    function SearchController($scope, $location, $httpParamSerializer, Search, Application, $window, $cookies) {
        var vm = this;
        vm.searchOptions = {};
        vm.searchResults = [];
        vm.checkBoxSelection = {};
        vm.applicationFieldSelection = {};
        vm.accessToken = $cookies.get('token');

        Search.getApplicationFields().then(function success(response){
            var applicationFields = response.data["application_fields"];
            var excludedFields = response.data["excluded_fields"];
            for (var i=0; i<applicationFields.length; i++){
                if (excludedFields.includes(applicationFields[i])){
                    continue;
                }
                vm.applicationFieldSelection[applicationFields[i]] = {
                    selected: false,
                    pretty: removeSnakeCase(applicationFields[i])
                };
            }

            var applicationDefaultFields = response.data["default_fields"];
            for (i=0; i<applicationDefaultFields.length; i++){
                vm.applicationFieldSelection[applicationDefaultFields[i]].selected = true;
            }


        }, function error(data){
            toastr.error(data.data.error, data.statusText + " " + data.status)
        });

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
        };

        vm.selectRow = function(data){
            data.selected = !data.selected;
        };

        vm.downloadFile = function(fileType){
            var applicationIds = [];
            for (var i=0; i<vm.searchResults.length; i++){
                if ((vm.searchResults[i].selected)){
                    applicationIds.push(vm.searchResults[i].id);
                }
            }

            // TODO: add sorting variable, and column selection.
            var zipQs = $httpParamSerializer({
                application_ids: applicationIds,
                token: vm.accessToken
            });

            switch(fileType){
                case "csv":
                    $window.open('api/applications/csv_download/?' + zipQs, '_blank');
                    break;
                case "zip":
                    $window.open('api/applications/zip_download/?' + zipQs, '_blank');
                    break;
            }
        };

        function removeSnakeCase(word){
            var wordLength = word.length;
            if (wordLength == 0){
                return ""
            }
            var result = word[0].toUpperCase();
            var previousUndescore = false;
            for (var i=1; i<word.length; i++){
                var character = word[i];
                if (character !== "_"){
                    if (previousUndescore){
                        result += character.toUpperCase();
                        previousUndescore = false;
                    }else{
                        result += character;
                    }

                }else{
                    result += " ";
                    previousUndescore = true;
                }
            }

            return result;
        }
    }
})();