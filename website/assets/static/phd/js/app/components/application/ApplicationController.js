
(function () {
    'use strict';

    angular
        .module('phd.application.controllers')
        .controller('ApplicationController', ApplicationController);

    ApplicationController.$inject = ['$scope', 'Application', '$routeParams'];

    function ApplicationController($scope, Application, $routeParams) {
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
                vm.creatorSupervision = response.data["application"]["supervisions"].filter(function(obj ) {
                    return obj.creator;
                })[0];
                console.log(vm.creatorSupervision);

                vm.creatorFiles = {
                    "APPLICATION_FORM": undefined,
                    "RESEARCH_SUMMARY": undefined,
                    "REFERENCES": [],
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
                console.log(vm.creatorFiles);
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
                if (element_files.length == 0){
                    if (element_id in files[key]){
                        delete files[key][element_id];
                    }
                }else{
                    if (!(key in files)){
                        files[key] = {};
                    }
                    files[key][element_id] = element_files[0];
                }
            });
        };

        // Remove files from the server
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

        vm.uploadFile = function(supervisionId, filesKey){
            Application.uploadFile(supervisionId, files[filesKey], vm.fileDescriptions);
        };

        // Dynamically append additional material files
        vm.additionals = [];
        vm.addNewAdditional = function() {
            var newItemNo = (vm.additionals.length == 0 ? 0 : vm.additionals[vm.additionals.length-1] + 1);
            vm.additionals.push(newItemNo);
        };

        vm.removeAdditional = function(index, id, filesKey) {
            vm.additionals.splice(index-1, 1);
            delete files[filesKey][id.concat(index)];
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