
(function () {
    'use strict';

    angular
        .module('phd.application.controllers')
        .controller('ApplicationController', ApplicationController);

    ApplicationController.$inject = ['$scope', '$rootScope', '$cookies', 'Application', '$routeParams'];

    function ApplicationController($scope, $rootScope, $cookies, Application, $routeParams) {
        var vm = this;

        vm.access_token = $cookies.get('token');

        // Decide between New or Existing
        var applicationID = $routeParams.id;
        vm.newApplication = typeof applicationID === "undefined";
        vm.application = {};
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

        // Setup for editing
        if (!vm.newApplication){
            Application.getExistingApplication(applicationID).then(function(response){
                vm.application = response.data["application"];

                // For easier UI-binding, we store the "creator" and the "supervisor" supervision details separately
                vm.creatorSupervision = undefined;
                vm.supervisorSupervisions = [];
                vm.supervisorSupervisionFiles = {};
                var supervisions = response.data["application"]["supervisions"];
                for (var i=0; i<supervisions.length; i++){
                    var supervision = supervisions[i];
                    if (supervision.creator){
                        vm.creatorSupervision = supervision;
                        vm.newFileDescriptions = {};
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
        }

        // Populate checkboxes
        Application.getApplicationFieldChoices().then(function(response){
            vm.applicationFieldChoices = response.data;
        });

        // Fill list of supervisor usernames
        vm.currentlySelectedSupervisor = undefined;
        Application.getSupervisorUsernames().then(function(response){
            vm.supervisorUsernames = response.data['usernames'];
        });

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

        vm.deleteSupervision = function(supervisionId){
            Application.deleteSupervision(supervisionId).then(function success(){

                // Update supervisions
                vm.supervisorSupervisions = vm.supervisorSupervisions.filter(function(obj ) {
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

                    // Toast
                    var toastMessage = "";
                    for (var i=0; i<documentations.length; i++){
                        toastMessage += "- " + documentations[i]["file_name"];
                    }
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

            Application.uploadApplication(true, vm.application, newFilesMap, newFileDescriptions, vm.temporarySupervisors).then(uploadSuccess, displayErrorMessage);

            function uploadSuccess(response) {
                toastr.success("Successfully uploaded new application!");
                var newApplicationid = response.data["id"];
                var newApplicationRegistryRef = response.data["registry_ref"];
                window.location = 'application/edit/' + newApplicationid.toString() + "/" + newApplicationRegistryRef.toString();
            }
        }

        function displayErrorMessage(data){
            toastr.error(data.data.error, data.statusText + " " + data.status)
        }
    }
})();