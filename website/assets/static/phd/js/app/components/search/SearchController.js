
(function () {
    'use strict';

    angular
        .module('phd.search.controllers')
        .controller('SearchController', SearchController);

    SearchController.$inject = ['$scope', '$location', '$httpParamSerializer', 'Search', 'Application', '$window', '$cookies', 'Authentication', 'Admin'];

    function SearchController($scope, $location, $httpParamSerializer, Search, Application, $window, $cookies, Authentication, Admin) {

        // If the user is not authenticated, they should not be here.
        if (!Authentication.isAuthenticated()) {
            $location.url('/login');
            return;
        }

        var vm = this;
        vm.searchOptions = {};
        vm.searchResults = [];
        vm.checkBoxSelection = {};
        vm.applicationFieldSelection = {};
        vm.allStaffRowSelection = false;
        vm.accessToken = $cookies.get('token');

        // In case there are query params in the URL at the new page visit
        attemptSearchByUrl();

        // Get all field names for column selection
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

        }, displayErrorMessage);

        // Get all checkbox multiple choices
        Application.getApplicationFieldChoices().then(function(response){
            vm.searchFieldOptions = response.data;
            for (var key in vm.searchFieldOptions) {
                if (vm.searchFieldOptions.hasOwnProperty(key)) {
                    if (typeof vm.checkBoxSelection[key] === "undefined"){
                        vm.checkBoxSelection[key] = {};
                    }
                }
            }
        }, displayErrorMessage);

        // Get all academic years
        vm.academicYears = [];
        Admin.getAllAcademicYears().then(function success(response){
            var academicYears = response.data.academic_years;
            for (var i=0; i<academicYears.length; i++){
                vm.academicYears.push(academicYears[i].name);
                if (academicYears[i].default){
                    vm.searchOptions.academicYearName = academicYears[i].name;
                }
            }
        }, displayErrorMessage);

        // Listen to when the user changes the sorting on the search table
        $scope.$on('tablesort:sortOrder', function(event, sortOrder){
            vm.sortField = sortOrder[0].name;
            vm.sortBy = sortOrder[0].order ? 'DESC' : 'ASC';
        });

        // Listen to URL changes: this is where most searches are launched
        $scope.$on('$routeUpdate', function(){

            // Save search to history
            $scope.sort = $location.search().sort;
            $scope.order = $location.search().order;
            $scope.offset = $location.search().offset;

            // Trigger the search
            attemptSearchByUrl();
        });

        // Called when the user initiates the search
        vm.search = function(){

            // Convert checkbox selection to search options
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

            // Search for all, or just change the URL
            var qs = $httpParamSerializer(vm.searchOptions);
            if (qs === "") {
                search({});
            }else{
                $location.search(qs);
            }
        };

        vm.selectStaffRow = function(data){
            data.selected = !data.selected;
        };

        vm.selectAllStaffRows = function(){
            vm.allStaffRowSelection = !vm.allStaffRowSelection;
            for (var i=0; i<vm.searchResults.length; i++){
                vm.searchResults[i].selected = vm.allStaffRowSelection;
            }
        };

        vm.downloadFile = function(fileType){
            var applicationIds = [];
            for (var i=0; i<vm.searchResults.length; i++){
                if ((vm.searchResults[i].selected)){
                    applicationIds.push(vm.searchResults[i].id);
                }
            }

            // TODO: add sorting variable, and column selection.

            // Column selection
            var selectedFields = [];
            for (var key in vm.applicationFieldSelection){
                if (vm.applicationFieldSelection.hasOwnProperty(key)){
                    if (vm.applicationFieldSelection[key].selected){
                        selectedFields.push(key);
                    }
                }
            }
            var zipQs = $httpParamSerializer({
                application_ids: applicationIds,
                token: vm.accessToken,
                selected_fields: selectedFields,
                sort_field: vm.sortField,
                sort_by: vm.sortBy
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

        // Populate the checkbox selection of the user based on search query parameters
        function populateCheckBoxSelection(getQueryParams){
            for (var key in vm.searchFieldOptions) {
                if (vm.searchFieldOptions.hasOwnProperty(key)) {
                    if (typeof vm.checkBoxSelection[key] === "undefined"){
                        vm.checkBoxSelection[key] = {};
                    }
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

        // Search for specific applications
        function search(options){
            Search.getResults(options).then(function(response){
                vm.searchResults = response.data["applications"];
            }, displayErrorMessage)
        }

        // Launch a search based on the URL
        function attemptSearchByUrl(){
            // Manage GET query parameters from the URL
            var getQueryParams = $location.search();
            var hasParams = Boolean(Object.keys(getQueryParams).length);

            // Conduct search or reset the selection
            if (hasParams){
                vm.searchOptions = getQueryParams;
                search(vm.searchOptions);
                populateCheckBoxSelection(getQueryParams);
            }else{
                vm.searchOptions = {}
            }
        }

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

        function displayErrorMessage(data){
            toastr.error(data.data.error, data.statusText + " " + data.status)
        }
    }
})();