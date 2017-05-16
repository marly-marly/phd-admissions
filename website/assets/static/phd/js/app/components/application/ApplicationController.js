
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
        var newApplication = typeof applicationID === "undefined";

        // New else Edit
        if (newApplication){
            vm.application = {};
            vm.application.supervisors = [];
        }else{
            Application.getExistingApplication(applicationID).then(function(response){
                vm.application = response.data["application"];
                vm.application.supervisors = [];
                vm.existingSupervisors = response.data["application"]["supervisions"];
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
                if (newApplication){
                    // Needs to be persisted with the new application
                    vm.temporarySupervisors.push(vm.currentlySelectedSupervisor);
                }else{
                    Application.addSupervision(applicationID, vm.currentlySelectedSupervisor).then(function(response){
                        vm.existingSupervisors.push(response.data);
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
                vm.existingSupervisors = vm.existingSupervisors.filter(function( obj ) {
                    return obj.id !== supervisionId;
                });
            })
        };

        // Register new files
        var files = {};
        $scope.setFiles = function(element) {
            $scope.$apply(function(scope) {
                var element_id = element.id;
                var element_files = element.files;
                if (element_files.length == 0){
                    if (element_id in files){
                        delete files[element_id];
                    }
                }else{
                    files[element_id] = element_files[0];
                }
            });
        };

        // Dynamically append additional material files
        vm.additionals = [];
        vm.addNewAdditional = function() {
            var newItemNo = (vm.additionals.length == 0 ? 0 : vm.additionals[vm.additionals.length-1] + 1);
            vm.additionals.push(newItemNo);
        };

        vm.removeAdditional = function(index, id) {
            vm.additionals.splice(index, 1);
            delete files[id];
        };

        vm.uploadApplication = uploadApplication;

        function uploadApplication(){
            Application.uploadApplication(true, vm.application, files, vm.temporarySupervisors).then(uploadSuccess, uploadError);

            function uploadSuccess() {
                window.location = 'application/new';
            }

            function uploadError(status) {
                console.error('Upload failed: ' + status);
            }
        }
    }
})();