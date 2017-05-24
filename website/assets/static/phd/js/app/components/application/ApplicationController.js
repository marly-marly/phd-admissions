
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
        vm.fileDescriptions = {};

        // Setup for editing
        if (!vm.newApplication){
            Application.getExistingApplication(applicationID).then(function(response){
                vm.application = response.data["application"];

                // For easier UI-binding, we store the "creator" and the "supervisor" supervision details separately
                vm.creatorSupervision = undefined;
                vm.creatorSupervisionFiles = {};
                vm.supervisorSupervisions = [];
                vm.supervisorSupervisionFiles = {};
                var supervisions = response.data["application"]["supervisions"];
                for (var i=0; i<supervisions.length; i++){
                    var supervision = supervisions[i];
                    if (supervision.creator){
                        vm.creatorSupervision = supervision;
                        vm.creatorSupervisionFiles = {
                            "APPLICATION_FORM": undefined,
                            "RESEARCH_SUMMARY": undefined,
                            "REFERENCE": [],
                            "ADDITIONAL_MATERIAL": []
                        };
                        vm.fileDescriptions = {};
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
                    
                    if (typeof vm.creatorSupervisionFiles[file_type] === "undefined" ){
                        vm.creatorSupervisionFiles[file_type] = file;
                    }else{
                        if (vm.creatorSupervisionFiles[file_type].constructor === Array){
                            vm.creatorSupervisionFiles[file_type].push(file);
                        }
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

        vm.temporarySupervisors = [];
        vm.addCurrentlySelectedSupervisor = function(){
            if (vm.newApplication){
                if (vm.temporarySupervisors.indexOf(vm.currentlySelectedSupervisor) == -1 && typeof vm.currentlySelectedSupervisor !== "undefined"){

                    // Later needs to be persisted with the new application
                    vm.temporarySupervisors.push(vm.currentlySelectedSupervisor);
                }
            }else{
                var supervisionExists = false;
                for (var key in vm.supervisorSupervisions) {
                    if (vm.supervisorSupervisions.hasOwnProperty(key)) {
                        if (vm.supervisorSupervisions[key]["supervisor"]["username"] === vm.currentlySelectedSupervisor){
                            supervisionExists = true;
                            break;
                        }
                    }
                }

                if (!supervisionExists){

                    // Later needs to be persisted with the new application
                    Application.addSupervision(applicationID, vm.currentlySelectedSupervisor).then(function(response){
                        vm.supervisorSupervisions.push(response.data);
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

        vm.deleteSupervision = function(supervisionId){
            Application.deleteSupervision(supervisionId).then(function(){

                // Update supervisions
                vm.supervisorSupervisions = vm.supervisorSupervisions.filter(function(obj ) {
                    return obj.id !== supervisionId;
                });
            })
        };

        // Register new newFiles
        vm.newFiles = {};
        $scope.setFiles = function(element) {
            $scope.$apply(function(scope) {
                var element_id = element.id;
                var element_files = element.files;

                // If not file selected, and there was one selected before, then remove the old one
                if (element_files.length == 0){
                    if (element_id in vm.newFiles){
                        delete vm.newFiles[element_id];
                    }
                }else{
                    // Otherwise overwrite/add the new one
                    vm.newFiles[element_id] = element_files[0];
                }
            });
        };

        // Removes a specific file from the server
        vm.deleteFile = function(fileType, fileId){
            Application.deleteFile(fileId).then(function(response){
                for (var i = 0; i++; i < vm.creatorSupervisionFiles[fileType].length){
                    if (vm.creatorSupervisionFiles[fileType][i]["id"] === fileId){
                        vm.creatorSupervisionFiles[fileType].splice(i, 1);
                        break;
                    }
                }
            })
        };

        // Uploads all newFiles corresponding to a specific supervision
        vm.uploadFile = function(supervisionId){
            Application.uploadFile(supervisionId, vm.newFiles, vm.fileDescriptions);
        };

        // Dynamically appends more file inputs
        vm.multiFileIndex = [];
        vm.addNewFileInput = function(fileTypeKey) {
            if (!(fileTypeKey in vm.multiFileIndex)){
                vm.multiFileIndex[fileTypeKey] = [];
            }
            var newItemNo = (vm.multiFileIndex[fileTypeKey].length == 0 ? 0 : vm.multiFileIndex[fileTypeKey][vm.multiFileIndex[fileTypeKey].length-1] + 1);
            vm.multiFileIndex[fileTypeKey].push(newItemNo);

            console.log(vm.multiFileIndex);
        };

        vm.removeFileInput = function(index, id, fileTypeKey) {
            vm.multiFileIndex[fileTypeKey].splice(index, 1);

            // Don't forget to remove file registered for the input
            delete vm.newFiles[id.concat(index)];
        };

        vm.uploadApplication = uploadApplication;

        function uploadApplication(){
            Application.uploadApplication(true, vm.application, vm.newFiles, vm.fileDescriptions, vm.temporarySupervisors).then(uploadSuccess, uploadError);

            function uploadSuccess() {
                window.location = 'application/new';
            }

            function uploadError(status) {
                console.error('Upload failed: ' + status);
            }
        }
    }
})();