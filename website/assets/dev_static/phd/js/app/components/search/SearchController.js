
(function () {
    'use strict';

    angular
        .module('phd.search.controllers')
        .controller('SearchController', SearchController);

    SearchController.$inject = ['$scope', '$location', '$httpParamSerializer', 'Search', 'Application', '$window', '$cookies', 'Authentication', 'Admin', '$q', 'Toast'];

    function SearchController($scope, $location, $httpParamSerializer, Search, Application, $window, $cookies, Authentication, Admin, $q, Toast) {

        // If the user is not authenticated, they should not be here.
        if (!Authentication.isAuthenticated()) {
            $location.url('/login');
            return;
        }

        var vm = this;
        vm.accessToken = $cookies.get('token');
        
        vm.searchCriteria = {};
        vm.searchResults = [];
        vm.checkBoxSelection = {};
        vm.applicationColumnSelection = {};
        vm.allRowSelection = false;
        
        // Get all field names for column selection
        Search.getApplicationFields().then(function success(response){

            // Populate column selection, excluding the excluded columns
            var applicationFields = response.data["application_fields"];
            var extraFields = response.data["extra_fields"];
            var excludedFields = response.data["excluded_fields"];
            applicationFields = applicationFields.concat(extraFields);
            for (var i=0; i<applicationFields.length; i++){
                if (excludedFields.indexOf(applicationFields[i]) > -1) {
                    continue;
                }
                vm.applicationColumnSelection[applicationFields[i]] = {
                    selected: false,
                    pretty: snakeCaseToPretty(applicationFields[i])
                };
            }

            // Select the default fields
            var applicationDefaultFields = response.data["default_fields"];
            for (i=0; i<applicationDefaultFields.length; i++){
                vm.applicationColumnSelection[applicationDefaultFields[i]].selected = true;
            }

        }, Toast.showHttpError);

        // Get all checkbox multiple choices
        var checkboxMultipleChoicesPromise = Application.getCheckboxMultipleChoices().then(function(response){
            vm.checkboxMultipleChoices = response.data;

            // Initialise data structure that stores the checkbox selection of the user
            for (var key in vm.checkboxMultipleChoices) {
                if (vm.checkboxMultipleChoices.hasOwnProperty(key)) {
                    if (typeof vm.checkBoxSelection[key] === "undefined"){
                        vm.checkBoxSelection[key] = {};
                    }
                }
            }
        }, Toast.showHttpError);

        // In case there are query params in the URL at the new page visit, initiate a new search
        attemptSearchByUrl();

        // Get all academic years
        vm.academicYears = [];
        Admin.getAllAcademicYears().then(function success(response){
            var academicYears = response.data.academic_years;
            for (var i=0; i<academicYears.length; i++){
                vm.academicYears.push(academicYears[i].name);

                // Set the default academic year to be selected on page load
                if (academicYears[i].default){
                    // Only set it if there is no search currently in progress
                    if (Object.keys(vm.searchCriteria).length === 0){
                        vm.searchCriteria.academic_year_name = academicYears[i].name;
                    }
                }
            }
        }, Toast.showHttpError);

        // Listen to when the user changes the sorting on the search table
        $scope.$on('tablesort:sortOrder', function(event, sortOrder){
            vm.sortField = sortOrder[0].name;
            vm.sortBy = sortOrder[0].order ? 'DESC' : 'ASC';
        });

        // Listen to URL changes: this is where searches are launched
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

            // Convert checkbox selection to search criteria
            for (var key in vm.checkBoxSelection) {
                if (vm.checkBoxSelection.hasOwnProperty(key)) {
                    vm.searchCriteria[key] = [];
                    var category = vm.checkBoxSelection[key];
                    for (var subKey in category) {
                        if (category.hasOwnProperty(subKey)) {
                            if (category[subKey]){
                                vm.searchCriteria[key].push(subKey);
                            }
                        }
                    }
                }
            }

            // Search for all, or just change the URL
            var qs = $httpParamSerializer(vm.searchCriteria);
            if (qs === "") {
                search({});
            }else{
                $location.search(qs);
            }
        };

        // TAGS
        vm.currentTag = undefined;
        vm.addCurrentTag = function(){
            if (typeof vm.searchCriteria.tags === "undefined"){
                vm.searchCriteria.tags = [];
            }

            if (vm.searchCriteria.tags.indexOf(vm.currentTag) > -1){
                Toast.showInfo(vm.currentTag + " already exists as a tag.")
            }else{
                vm.searchCriteria.tags.push(vm.currentTag);
                vm.currentTag = undefined;
            }
        };

        vm.removeTag = function(tag){
            vm.searchCriteria.tags= vm.searchCriteria.tags.filter(function(word ) {
                return word !== tag;
            });
        };

        Admin.getAllTags().then(function success(response){
            vm.allTags = response.data.tags;
        }, Toast.showHttpError);

        // ROW SELECTION
        vm.numberOfSelectedRows = 0;
        vm.selectRow = function(data){
            data.selected = !data.selected;
            if (data.selected){
                vm.numberOfSelectedRows++;
            }else{
                vm.numberOfSelectedRows--;
            }
        };

        vm.selectAllRows = function(){
            vm.allRowSelection = !vm.allRowSelection;
            for (var i=0; i<vm.searchResults.length; i++){
                vm.searchResults[i].selected = vm.allRowSelection;
            }

            if (vm.allRowSelection){
                vm.numberOfSelectedRows = vm.searchResults.length;
            }else{
                vm.numberOfSelectedRows = 0;
            }
        };

        vm.downloadFile = function(fileType){
            var applicationIds = [];
            for (var i=0; i<vm.searchResults.length; i++){
                if ((vm.searchResults[i].selected)){
                    applicationIds.push(vm.searchResults[i].id);
                }
            }

            // Column selection
            var selectedFields = [];
            for (var key in vm.applicationColumnSelection){
                if (vm.applicationColumnSelection.hasOwnProperty(key)){
                    if (vm.applicationColumnSelection[key].selected){
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

        // Populates the multiple choice selection of the user based on search query parameters of the URL
        function populateMultiChoiceSearchSelection(getQueryParams){

            // Make sure we wait until all search field options are loaded
            $q.all([checkboxMultipleChoicesPromise]).then(function() {

                // Tick the appropriate checkboxes
                for (var key in vm.checkboxMultipleChoices) {
                    if (vm.checkboxMultipleChoices.hasOwnProperty(key)) {
                        if (key in getQueryParams) {
                            var value = getQueryParams[key];

                            // It might be an array of values or a single value
                            if (value.constructor === Array) {
                                for (var i = 0; i < value.length; i++) {
                                    vm.checkBoxSelection[key][value[i]] = true;
                                }
                            } else {
                                vm.checkBoxSelection[key][value] = true;
                            }
                        }
                    }
                }
            });

            // If there was only 1 tag, we have to explicitly convert the string to array
            if (typeof getQueryParams.tags === "string"){
                vm.searchCriteria.tags = [getQueryParams.tags]
            }
        }

        // Search for specific applications
        function search(options){
            Search.getResults(options).then(function(response){
                vm.searchResults = response.data["applications"];
            }, Toast.showHttpError)
        }

        // Launch a search based on the URL
        function attemptSearchByUrl(){
            // Manage GET query parameters from the URL
            var getQueryParams = $location.search();
            var hasParams = Boolean(Object.keys(getQueryParams).length);

            // Conduct search or reset the selection
            if (hasParams){
                vm.searchCriteria = getQueryParams;
                search(vm.searchCriteria);
                populateMultiChoiceSearchSelection(getQueryParams);
            }else{
                vm.searchCriteria = {}
            }
        }

        function snakeCaseToPretty(word){
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