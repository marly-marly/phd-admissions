
(function () {
    'use strict';

    angular
        .module('phd.application.controllers')
        .controller('ApplicationController', ApplicationController);

    ApplicationController.$inject = ['$location', '$cookies', 'Application', '$routeParams', 'Authentication', '$q', 'Admin', 'Toast'];

    function ApplicationController($location, $cookies, Application, $routeParams, Authentication, $q, Admin, Toast) {

        // If the user is not authenticated, they should not be here.
        if (!Authentication.isAuthenticated()) {
            $location.url('/login');
            return;
        }

        var vm = this;

        var applicationID = $routeParams.id;
        vm.newApplication = typeof applicationID === "undefined";
        vm.application = {};
        vm.newFilesIndex = {};
        vm.currentTag = undefined;
        vm.application.tag_words = [];
        vm.addCurrentTag = function(){
            if (vm.newApplication){
                if (vm.application.tag_words.indexOf(vm.currentTag) > -1){
                    Toast.showInfo(vm.currentTag + " already exists as a tag.")
                }else{
                    vm.application.tag_words.push(vm.currentTag);
                    vm.currentTag = undefined;
                }
            }else{
                Application.addTagToApplication(vm.application.id, vm.currentTag).then(function success(response){
                    vm.application.tags.push(response.data.tag);
                    vm.currentTag = undefined;

                    Toast.showSuccess("Added!");
                }, Toast.showHttpError)
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
                    Toast.showSuccess("Tag removed!")
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
        var applicationFieldChoicesPromise = Application.getCheckboxMultipleChoices().then(function(response){
            vm.applicationFieldChoices = response.data;
        });

        // Fill list of supervisor usernames
        vm.currentlySelectedSupervisor = undefined;
        Application.getSupervisorStaff().then(function(response){
            vm.supervisors = response.data;
        });

        // Fill list of available academic years
        var academicYearsPromise = Application.getAllAcademicYears().then(function success(response){
            vm.academicYears = response.data.academic_years;

            // Find default academic year
            vm.application.academic_year = Application.findDefaultAcademicYear(vm.academicYears);
        }, Toast.showHttpError);

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

            // TODO: check dirty, ask for confirm

            vm.editable = false;
            vm.application = angular.copy(temporaryApplication);

            // Whenever we assign vm.application, we need the appropriate academic year object reference.
            vm.application.academic_year = Application.findDefaultAcademicYear(vm.academicYears);
        };

        vm.updateApplication = function(){
            Application.updateApplication(vm.application).then(function(){
                vm.editable = false;
                Toast.showSuccess("Application saved!");
            }, Toast.showHttpError)
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
                        if (vm.supervisorSupervisions[key]["supervisor"]["username"] === vm.currentlySelectedSupervisor.username){
                            supervisionExists = true;
                            break;
                        }
                    }
                }

                // Attempt to add the supervisor on the back-end
                if (!supervisionExists){
                    Application.addSupervision(applicationID, vm.currentlySelectedSupervisor.username).then(function success(response){
                        var newSupervision = response.data;
                        vm.supervisorSupervisions.push(newSupervision);

                        Toast.showSuccess(newSupervision.supervisor.username + ' was added as a supervisor!');
                    }, Toast.showHttpError)
                }else{
                    Toast.showInfo(vm.currentlySelectedSupervisor.username + ' is already a supervisor!');
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

                Toast.showSuccess(newSupervision.supervisor.username + ' was added as an administrator!');
            }, Toast.showHttpError)
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
                Toast.showSuccess('Supervisor was successfully removed!');
            }, Toast.showHttpError)
        };

        vm.uploadNewApplication = uploadNewApplication;

        vm.deleteApplication = function(){
            Application.deleteApplication(vm.application["id"]).then(function success(){
                Toast.showSuccess("Application successfully deleted!");
                $location.url('/search');

            }, Toast.showHttpError)
        };

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
                        counter++;
                    }
                }
            }

            var temporarySupervisorNames = [];
            for (i=0; i< vm.temporarySupervisors.length; i++){
                temporarySupervisorNames.push(vm.temporarySupervisors[i].username);
            }

            Application.uploadApplication(vm.application, newFilesMap, newFileDescriptions, temporarySupervisorNames).then(uploadSuccess, Toast.showHttpError);

            function uploadSuccess(response) {
                Toast.showSuccess("Successfully uploaded new application!");
                var newApplicationid = response.data["id"];
                var newApplicationRegistryRef = response.data["registry_ref"];
                $location.path('application/edit/' + newApplicationid.toString() + "/" + newApplicationRegistryRef.toString());
            }
        }
    }
})();