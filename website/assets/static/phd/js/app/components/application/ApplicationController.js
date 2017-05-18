
(function () {
    'use strict';

    angular
        .module('phd.application.controllers')
        .controller('ApplicationController', ApplicationController);

    ApplicationController.$inject = ['$scope', '$rootScope', 'Application', '$routeParams'];

    function ApplicationController($scope, $rootScope, Application, $routeParams) {
        var vm = this;

        // Decide between New or Existing
        var applicationID = $routeParams.id;
        vm.newApplication = typeof applicationID === "undefined";

        // New else Edit
        if (vm.newApplication){
            vm.application = {};
            vm.application.supervisors = [];
        }else{
            Application.getExistingApplication(applicationID).then(function(response){
                vm.application = response.data["application"];
                vm.application.supervisors = [];
                vm.existingSupervisions = response.data["application"]["supervisions"];

                // For easier UI-binding, we store the "creator" supervision details separately
                vm.creatorSupervision = response.data["application"]["supervisions"].filter(function(obj ) {
                    return obj.creator;
                })[0];

                vm.creatorFiles = {
                    "APPLICATION_FORM": undefined,
                    "RESEARCH_SUMMARY": undefined,
                    "REFERENCE": [],
                    "ADDITIONAL_MATERIAL": []
                };
                var documentations = vm.creatorSupervision["documentations"];
                for (var i = 0, len = documentations.length; i < len; i++) {
                    var file = documentations[i];
                    var file_type = file["file_type"];

                    if (typeof vm.creatorFiles[file_type] === "undefined" ){
                        vm.creatorFiles[file_type] = file;
                    }else{
                        vm.creatorFiles[file_type].push(file);
                    }
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

        // This list of supervisors needs to be submitted with a new application
        vm.temporarySupervisors = [];
        vm.addCurrentlySelectedSupervisor = function(){
            if (vm.temporarySupervisors.indexOf(vm.currentlySelectedSupervisor) == -1 && typeof vm.currentlySelectedSupervisor !== "undefined"){
                if (vm.newApplication){
                    // Needs to be persisted with the new application
                    vm.temporarySupervisors.push(vm.currentlySelectedSupervisor);
                }else{
                    Application.addSupervision(applicationID, vm.currentlySelectedSupervisor).then(function(response){
                        vm.existingSupervisions.push(response.data);
                    })
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

        vm.updateSupervision = function(data){
            Application.updateSupervision(data.id, {acceptance_condition:data.acceptance_condition, recommendation:data.recommendation});
        };

        vm.deleteSupervision = function(supervisionId){
            Application.deleteSupervision(supervisionId).then(function(){

                // Update supervisions
                vm.existingSupervisions = vm.existingSupervisions.filter(function(obj ) {
                    return obj.id !== supervisionId;
                });
            })
        };

        // Register new files
        var files = {};
        vm.fileDescriptions = {};
        $scope.setFiles = function(element, key) {
            $scope.$apply(function(scope) {
                var element_id = element.id;
                var element_files = element.files;

                // If not file selected, and there was one selected before, then remove the old one
                if (element_files.length == 0){
                    if (element_id in files[key]){
                        delete files[key][element_id];
                    }
                }else{
                    // Otherwise overwrite/add the new one
                    if (!(key in files)){
                        files[key] = {};
                    }
                    files[key][element_id] = element_files[0];
                }
            });
        };

        // Removes a specific file from the server
        vm.deleteFile = function(fileType, fileId){
            Application.deleteFile(fileId).then(function(response){
                for (var i = 0; i++; i < vm.creatorFiles[fileType].length){
                    if (vm.creatorFiles[fileType][i]["id"] === fileId){
                        vm.creatorFiles[fileType].splice(i, 1);
                        break;
                    }
                }
            })
        };

        // Uploads all files corresponding to a specific supervision
        vm.uploadFile = function(supervisionId, filesKey){
            Application.uploadFile(supervisionId, files[filesKey], vm.fileDescriptions);
        };

        // Dynamically appends more file inputs
        vm.multiFileIndex = [];
        vm.addNewFileInput = function(fileTypeKey) {
            if (!(fileTypeKey in vm.multiFileIndex)){
                vm.multiFileIndex[fileTypeKey] = [];
            }
            var newItemNo = (vm.multiFileIndex[fileTypeKey].length == 0 ? 0 : vm.multiFileIndex[fileTypeKey][vm.multiFileIndex[fileTypeKey].length-1] + 1);
            vm.multiFileIndex[fileTypeKey].push(newItemNo);
        };

        vm.removeFileInput = function(index, id, fileTypeKey, filesKey) {
            vm.multiFileIndex[fileTypeKey].splice(index, 1);

            // Don't forget to remove file registered for the input
            if (filesKey in files){
                delete files[filesKey][id.concat(index)];
            }
        };

        vm.uploadApplication = uploadApplication;

        function uploadApplication(){
            Application.uploadApplication(true, vm.application, files['creator'], vm.fileDescriptions, vm.temporarySupervisors).then(uploadSuccess, uploadError);

            function uploadSuccess() {
                window.location = 'application/new';
            }

            function uploadError(status) {
                console.error('Upload failed: ' + status);
            }
        }
    }
})();