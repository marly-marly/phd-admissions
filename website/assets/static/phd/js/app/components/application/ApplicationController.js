
(function () {
    'use strict';

    angular
        .module('phd.application.controllers')
        .controller('ApplicationController', ApplicationController);

    ApplicationController.$inject = ['$scope', '$location', '$cookies', 'Application', '$routeParams', 'Authentication', '$q', 'Admin'];

    function ApplicationController($scope, $location, $cookies, Application, $routeParams, Authentication, $q, Admin) {

        // If the user is not authenticated, they should not be here.
        if (!Authentication.isAuthenticated()) {
            $location.url('/login');
            return;
        }

        var vm = this;

        var applicationID = $routeParams.id;
        vm.newApplication = typeof applicationID === "undefined";
        vm.application = {};
        vm.currentTag = undefined;
        vm.application.tag_words = [];
        vm.addCurrentTag = function(){
            if (vm.newApplication){
                if (vm.application.tag_words.indexOf(vm.currentTag) > -1){
                    toastr.info(vm.currentTag + " already exists as a tag.")
                }else{
                    vm.application.tag_words.push(vm.currentTag);
                    vm.currentTag = undefined;
                }
            }else{
                Application.addTagToApplication(vm.application.id, vm.currentTag).then(function success(response){
                    vm.application.tags.push(response.data.tag);
                    vm.currentTag = undefined;

                    toastr.success("Added!");
                }, displayErrorMessage)
            }
        };

        vm.removeTag = function(tag){
            if (vm.newApplication){
                vm.application.tag_words = vm.application.tag_words.filter(function(word ) {
                    return word !== tag;
                });
            }else{
                Application.deleteTagFromApplication(tag.id, vm.application.id).then(function success(){
                    vm.application.tags = vm.application.tags.filter(function(obj ) {
                        return obj.id !== tag.id;
                    });
                    toastr.success("Tag removed!")
                });
            }
        };

        Admin.getAllTags().then(function success(response){
            vm.allTags = response.data.tags;
        });

        vm.application.possible_funding = [];
        vm.selectedPossibleFunding = {};
        vm.togglePossibleFunding = function(key){
            if (key in vm.selectedPossibleFunding){
                vm.selectedPossibleFunding[key] = ! vm.selectedPossibleFunding[key];
            }else{
                vm.selectedPossibleFunding[key] = true;
            }

            if (vm.selectedPossibleFunding[key]){
                vm.application.possible_funding.push(key);
            }else{
                for (var i=vm.application.possible_funding.length-1; i>=0; i--) {
                    if (vm.application.possible_funding[i] === key) {
                        vm.application.possible_funding.splice(i, 1);
                        break;
                    }
                }
            }
        };
        vm.application.supervisors = [];
        vm.newFileDescriptions = {};

        var fileTypeTemplate = {
            "APPLICATION_FORM": [],
            "RESEARCH_SUMMARY": [],
            "REFERENCE": [],
            "ADDITIONAL_MATERIAL": []
        };

        vm.creatorSupervisionFiles = {
            "APPLICATION_FORM": [],
            "RESEARCH_SUMMARY": [],
            "REFERENCE": [],
            "ADDITIONAL_MATERIAL": []
        };

        // User account details
        vm.access_token = $cookies.get('token');
        var userDetails = Authentication.getAuthenticatedAccount();
        if (userDetails != undefined){
            var userRole = userDetails.userRole;
            vm.isAdmin = userRole === 'ADMIN';
            vm.username = userDetails.username;
        }

        // Populate checkboxes
        var applicationFieldChoicesPromise = Application.getApplicationFieldChoices().then(function(response){
            vm.applicationFieldChoices = response.data;
        });

        // Fill list of supervisor usernames
        vm.currentlySelectedSupervisor = undefined;
        Application.getSupervisorUsernames().then(function(response){
            vm.supervisorUsernames = response.data['usernames'];
        });

        // Fill list of available academic years
        var academicYearsPromise = Application.getAllAcademicYears().then(function success(response){
            vm.academicYears = response.data.academic_years;

            // Find default academic year
            findDefaultAcademicYear();
        }, displayErrorMessage);

        // Setup for editing
        if (!vm.newApplication){
            var existingApplicationPromise = Application.getExistingApplication(applicationID).then(function(response){
                vm.application = response.data["application"];

                // For easier UI-binding, we store the "creator", the "supervisor", and the "admin" supervision details separately
                vm.creatorSupervision = undefined;
                vm.adminSupervisions = [];
                vm.supervisorSupervisions = [];
                vm.supervisorSupervisionFiles = {};
                var supervisions = response.data["application"]["supervisions"];
                for (var i=0; i<supervisions.length; i++){
                    var supervision = supervisions[i];
                    if (supervision.type === "ADMIN"){
                        vm.adminSupervisions.push(supervision);
                        if (supervision.creator){
                            vm.creatorSupervision = supervision;
                            vm.newFileDescriptions = {};
                        }
                    }else{
                        vm.supervisorSupervisions.push(supervision);
                        for (var j=0; j<supervision["documentations"].length; j++){
                            if (!(supervision.id in vm.supervisorSupervisionFiles)){
                                vm.supervisorSupervisionFiles[supervision.id] = [];
                            }
                            var documentation = supervision["documentations"][j];
                            vm.supervisorSupervisionFiles[supervision.id].push(documentation);
                        }
                    }
                }

                var documentations = vm.creatorSupervision["documentations"];
                for (i = 0; i < documentations.length; i++) {
                    var file = documentations[i];
                    var file_type = file["file_type"];
                    vm.creatorSupervisionFiles[file_type].push(file);
                }
            });

            // After both requests have ended
            $q.all([academicYearsPromise, existingApplicationPromise]).then(function(){
                // Point existing object reference to one of the academic year objects.
                // This is needed in order to correctly display the "select" form-input's options.
                for (var i=0; i<vm.academicYears.length; i++){
                    if (vm.academicYears[i].id == vm.application.academic_year.id){
                        vm.application.academic_year = vm.academicYears[i];
                        break;
                    }
                }
            });

            $q.all([applicationFieldChoicesPromise, existingApplicationPromise]).then(function(){
                // Select existing possible funding
                for (var i=0; i<vm.application.possible_funding.length; i++){
                    vm.selectedPossibleFunding[vm.application.possible_funding[i]] = true;
                }
            })
        }

        vm.editable = vm.newApplication;
        var temporaryApplication = undefined;
        vm.enableEdit = function(){
            temporaryApplication = angular.copy(vm.application);
            vm.editable = true;
        };

        vm.disableEdit = function(){
            vm.editable = false;
            vm.application = angular.copy(temporaryApplication);

            // Whenever we assign vm.application, we need the appropriate academic year object reference.
            findDefaultAcademicYear();
        };

        vm.updateApplication = function(){
            Application.updateApplication(vm.application).then(function(){
                vm.editable = false;
                toastr.success("Application saved!");
            }, displayErrorMessage)
        };

        // These temporary supervisors later need to be persisted with the new application
        vm.temporarySupervisors = [];
        vm.addCurrentlySelectedSupervisor = function(){
            if (vm.newApplication){

                // Add to a temporary list of supervisors that will be submitted with the application
                if (vm.temporarySupervisors.indexOf(vm.currentlySelectedSupervisor) == -1 && typeof vm.currentlySelectedSupervisor !== "undefined"){
                    vm.temporarySupervisors.push(vm.currentlySelectedSupervisor);
                }
            }else{

                // Check if supervisor is already added
                var supervisionExists = false;
                for (var key in vm.supervisorSupervisions) {
                    if (vm.supervisorSupervisions.hasOwnProperty(key)) {
                        if (vm.supervisorSupervisions[key]["supervisor"]["username"] === vm.currentlySelectedSupervisor){
                            supervisionExists = true;
                            break;
                        }
                    }
                }

                // Attempt to add the supervisor on the back-end
                if (!supervisionExists){
                    Application.addSupervision(applicationID, vm.currentlySelectedSupervisor).then(function success(response){
                        var newSupervision = response.data;
                        vm.supervisorSupervisions.push(newSupervision);

                        toastr.success(newSupervision.supervisor.username + ' was added as a supervisor!');
                    }, displayErrorMessage)
                }else{
                    toastr.info(vm.currentlySelectedSupervisor + ' is already a supervisor!');
                }
            }

            vm.currentlySelectedSupervisor = undefined;
        };

        vm.removeTemporarySupervisor = function(supervisor){
            var supervisorIndex = vm.temporarySupervisors.indexOf(supervisor);
            if (supervisorIndex != -1){
                vm.temporarySupervisors.splice(supervisorIndex, 1);
            }
        };

        vm.addAdminSupervision = function(){
            Application.addSupervision(applicationID, userDetails.username, "ADMIN").then(function success(response){
                var newSupervision = response.data;
                vm.adminSupervisions.push(newSupervision);

                toastr.success(newSupervision.supervisor.username + ' was added as an administrator!');
            }, displayErrorMessage)
        };

        vm.myAdminSupervisionExists = function(){
            if (typeof vm.adminSupervisions === "undefined"){
                return true;
            }
            for (var i=0; i<vm.adminSupervisions.length; i++){
                if (vm.adminSupervisions[i].supervisor.username === vm.username){
                    return true;
                }
            }

            return false;
        };

        vm.deleteSupervision = function(supervisionId){
            Application.deleteSupervision(supervisionId).then(function success(){

                // Update supervisions
                vm.supervisorSupervisions = vm.supervisorSupervisions.filter(function(obj ) {
                    return obj.id !== supervisionId;
                });
                vm.adminSupervisions = vm.adminSupervisions.filter(function(obj ) {
                    return obj.id !== supervisionId;
                });
                toastr.success('Supervisor was successfully removed!');
            }, displayErrorMessage)
        };

        // Register new newFiles
        vm.newFilesIndex = angular.copy(fileTypeTemplate);
        $scope.setFiles = function(element) {
            $scope.$apply(function(scope) {
                var fileType = element.name;
                var fileIndex = Number(element.id);
                var elementFiles = element.files;

                // If no file is selected, and there was one selected before, then remove the old one
                if (elementFiles.length == 0){
                    vm.newFilesIndex[fileType][fileIndex]["file"] = undefined;
                }else{
                    // Overwrite/add the new one
                    vm.newFilesIndex[fileType][fileIndex]["file"] = elementFiles[0];
                }
            });
        };

        // Removes a specific file from the server
        vm.deleteFile = function(fileType, fileId){
            Application.deleteFile(fileId).then(
                function success(){
                    for (var i = 0; i < vm.creatorSupervisionFiles[fileType].length; i++){
                        if (vm.creatorSupervisionFiles[fileType][i]["id"] === fileId){
                            vm.creatorSupervisionFiles[fileType].splice(i, 1);
                            break;
                        }
                    }

                    toastr.success("File successfully removed!")
                },displayErrorMessage
            )
        };

        // Uploads all newFiles corresponding to a specific supervision
        vm.uploadFile = function(index, fileType){
            Application.uploadFile(vm.creatorSupervision.id, vm.newFilesIndex[fileType][index].file, fileType + "_" + index, vm.newFilesIndex[fileType][index].description).then(
                function success(response){

                    // Update view-model variables
                    var documentations = response.data["documentations"];
                    if (typeof vm.creatorSupervisionFiles[fileType] === "undefined"){
                        vm.creatorSupervisionFiles[fileType] = documentations;
                    }else{
                        vm.creatorSupervisionFiles[fileType] = vm.creatorSupervisionFiles[fileType].concat(documentations);
                    }

                    // Remove uploaded file from the temporary storage
                    vm.newFilesIndex[fileType][index].file = undefined;
                    vm.newFilesIndex[fileType][index].description = undefined;

                    // Toast
                    var toastMessage = "";
                    for (var i=0; i<documentations.length; i++){
                        toastMessage += "- " + documentations[i]["file_name"] + "<br>";
                    }
                    toastr.options.escapeHtml = false;
                    toastr.success(toastMessage, "Successfully uploaded:")
                },displayErrorMessage
            );
        };

        // Dynamically appends more file inputs
        vm.addNewFileInput = function(fileTypeKey) {
            vm.newFilesIndex[fileTypeKey].push({
                file: undefined,
                description: ""
            });
        };

        vm.addNewFileInput("APPLICATION_FORM");
        vm.addNewFileInput("RESEARCH_SUMMARY");

        vm.removeFileInput = function(index, fileType) {
            vm.newFilesIndex[fileType].splice(index, 1);
        };

        vm.uploadNewApplication = uploadNewApplication;

        vm.deleteApplication = function(){
            Application.deleteApplication(vm.application["id"]).then(function success(){
                toastr.success("Application successfully deleted!");
                $location.url('/search');

            }, displayErrorMessage)
        };

        // Overwrites the academic year object reference of the application, with the corresponding one from options.
        function findDefaultAcademicYear(){
            for (var i=0; i<vm.academicYears.length; i++){
                if (vm.academicYears[i].default){
                    vm.application.academic_year = vm.academicYears[i];
                    break;
                }
            }
        }

        function uploadNewApplication(){
            var newFilesMap = {};
            var newFileDescriptions = {};
            for (var key in vm.newFilesIndex){
                if(vm.newFilesIndex.hasOwnProperty(key)){
                    var newFilesList = vm.newFilesIndex[key];
                    var counter = 0;
                    for (var i=0; i<newFilesList.length; i++){
                        var currentFileDetails = newFilesList[i];
                        if (typeof currentFileDetails.file === "undefined"){
                            continue;
                        }
                        var compositeKey = key + "_" + parseInt(counter);
                        newFilesMap[compositeKey] = currentFileDetails.file;
                        newFileDescriptions[compositeKey] = currentFileDetails.description;
                    }
                }
            }

            Application.uploadApplication(vm.application, newFilesMap, newFileDescriptions, vm.temporarySupervisors).then(uploadSuccess, displayErrorMessage);

            function uploadSuccess(response) {
                toastr.success("Successfully uploaded new application!");
                var newApplicationid = response.data["id"];
                var newApplicationRegistryRef = response.data["registry_ref"];
                $location.path('application/edit/' + newApplicationid.toString() + "/" + newApplicationRegistryRef.toString());
            }
        }

        function displayErrorMessage(data){
            toastr.error(data.data.error, data.statusText + " " + data.status)
        }
    }
})();