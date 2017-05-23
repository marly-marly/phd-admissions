
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
                vm.supervisorSupervisions = [];
                vm.supervisionFiles = {};
                var supervisions = response.data["application"]["supervisions"];
                var i = undefined;
                for (i=0; i<supervisions.length; i++){
                    var supervision = supervisions[i];
                    if (supervision.creator){
                        vm.creatorSupervision = supervision;
                        vm.supervisionFiles["creator"] = {
                            "APPLICATION_FORM": undefined,
                            "RESEARCH_SUMMARY": undefined,
                            "REFERENCE": [],
                            "ADDITIONAL_MATERIAL": []
                        };
                        vm.fileDescriptions["creator"] = {};
                    }else{
                        vm.supervisorSupervisions.push(supervision);
                        vm.supervisionFiles["supervisor_" + supervision.id.toString()] = {
                            "APPLICATION_FORM": undefined,
                            "RESEARCH_SUMMARY": undefined,
                            "REFERENCE": [],
                            "ADDITIONAL_MATERIAL": []
                        };
                        vm.fileDescriptions["supervisor_" + supervision.id.toString()] = {};
                    }
                }

                var documentations = vm.creatorSupervision["documentations"];
                for (i = 0; i < documentations.length; i++) {
                    var file = documentations[i];
                    var file_type = file["file_type"];

                    if (typeof vm.supervisionFiles["creator"][file_type] === "undefined" ){
                        vm.supervisionFiles["creator"][file_type] = file;
                    }else{
                        if (vm.supervisionFiles["creator"][file_type].constructor === Array){
                            vm.supervisionFiles["creator"][file_type].push(file);
                        }
                    }
                }

                for (i = 0; i < vm.supervisorSupervisions.length; i++) {
                    documentations = vm.supervisorSupervisions[i]["documentations"];
                    var supervisionId = vm.supervisorSupervisions[i]["id"];
                    for (var j = 0; j < documentations.length; j++) {
                        file = documentations[j];
                        file_type = file["file_type"];

                        if (typeof vm.supervisionFiles["supervisor_" + supervisionId.toString()][file_type] === "undefined" ){
                            vm.supervisionFiles["supervisor_" + supervisionId.toString()][file_type] = file;
                        }else{
                            if (vm.supervisionFiles["supervisor_" + supervisionId.toString()][file_type].constructor === Array){
                                vm.supervisionFiles["supervisor_" + supervisionId.toString()][file_type].push(file);
                            }
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

        // This list of supervisors needs to be submitted with a new application
        vm.temporarySupervisors = [];
        vm.addCurrentlySelectedSupervisor = function(){
            if (vm.temporarySupervisors.indexOf(vm.currentlySelectedSupervisor) == -1 && typeof vm.currentlySelectedSupervisor !== "undefined"){
                if (vm.newApplication){
                    // Needs to be persisted with the new application
                    vm.temporarySupervisors.push(vm.currentlySelectedSupervisor);
                }else{
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

        vm.updateSupervision = function(data){
            var supervisionId = data.id;
            Application.updateSupervision(supervisionId, {acceptance_condition:data.acceptance_condition, recommendation:data.recommendation});
            vm.uploadFile(supervisionId, "supervisor_" + supervisionId.toString());
        };

        vm.deleteSupervision = function(supervisionId){
            Application.deleteSupervision(supervisionId).then(function(){

                // Update supervisions
                vm.supervisorSupervisions = vm.supervisorSupervisions.filter(function(obj ) {
                    return obj.id !== supervisionId;
                });
            })
        };

        // Register new files
        vm.files = {};
        $scope.setFiles = function(element) {
            $scope.$apply(function(scope) {
                var element_id = element.id;
                var element_files = element.files;
                var key = element.name;

                // If not file selected, and there was one selected before, then remove the old one
                if (element_files.length == 0){
                    if (element_id in vm.files[key]){
                        delete vm.files[key][element_id];
                    }
                }else{
                    // Otherwise overwrite/add the new one
                    if (!(key in vm.files)){
                        vm.files[key] = {};
                    }
                    vm.files[key][element_id] = element_files[0];
                }
            });
        };

        // Removes a specific file from the server
        vm.deleteFile = function(fileType, fileId, supervisionKey){
            Application.deleteFile(fileId).then(function(response){
                for (var i = 0; i++; i < vm.supervisionFiles[supervisionKey][fileType].length){
                    if (vm.supervisionFiles[supervisionKey][fileType][i]["id"] === fileId){
                        vm.supervisionFiles[supervisionKey][fileType].splice(i, 1);
                        break;
                    }
                }
            })
        };

        // Uploads all files corresponding to a specific supervision
        vm.uploadFile = function(supervisionId, supervisionKey){
            Application.uploadFile(supervisionId, vm.files[supervisionKey], vm.fileDescriptions[supervisionKey]);
        };

        // Dynamically appends more file inputs
        vm.multiFileIndex = [];
        vm.addNewFileInput = function(fileTypeKey, supervisionKey) {
            if (!(supervisionKey in vm.multiFileIndex)){
                vm.multiFileIndex[supervisionKey] = {};
            }
            if (!(fileTypeKey in vm.multiFileIndex[supervisionKey])){
                vm.multiFileIndex[supervisionKey][fileTypeKey] = [];
            }
            var newItemNo = (vm.multiFileIndex[supervisionKey][fileTypeKey].length == 0 ? 0 : vm.multiFileIndex[supervisionKey][fileTypeKey][vm.multiFileIndex[supervisionKey][fileTypeKey].length-1] + 1);
            vm.multiFileIndex[supervisionKey][fileTypeKey].push(newItemNo);

            console.log(vm.multiFileIndex);
        };

        vm.removeFileInput = function(index, id, fileTypeKey, filesKey) {
            vm.multiFileIndex[filesKey][fileTypeKey].splice(index, 1);

            // Don't forget to remove file registered for the input
            if (filesKey in vm.files){
                delete vm.files[filesKey][id.concat(index)];
            }
        };

        vm.uploadApplication = uploadApplication;

        function uploadApplication(){
            Application.uploadApplication(true, vm.application, vm.files['creator'], vm.fileDescriptions, vm.temporarySupervisors).then(uploadSuccess, uploadError);

            function uploadSuccess() {
                window.location = 'application/new';
            }

            function uploadError(status) {
                console.error('Upload failed: ' + status);
            }
        }
    }
})();