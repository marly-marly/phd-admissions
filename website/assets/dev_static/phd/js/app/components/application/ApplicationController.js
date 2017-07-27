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

        // Decide between new/existing application
        var applicationID = $routeParams.id;
        vm.newApplication = typeof applicationID === "undefined";

        // By default every new application is editable
        vm.editable = vm.newApplication;
        vm.newFilesIndex = {};

        Admin.getAllTags().then(function success(response) {
            vm.allTags = response.data.tags;
        });

        vm.application = {};
        vm.application.possible_funding = [];
        vm.selectedPossibleFunding = {};
        vm.recommendedSupervisors = [];
        vm.togglePossibleFunding = function (key) {
            if (key in vm.selectedPossibleFunding) {
                vm.selectedPossibleFunding[key] = !vm.selectedPossibleFunding[key];
            } else {
                vm.selectedPossibleFunding[key] = true;
            }

            if (vm.selectedPossibleFunding[key]) {
                vm.application.possible_funding.push(key);
            } else {
                for (var i = vm.application.possible_funding.length - 1; i >= 0; i--) {
                    if (vm.application.possible_funding[i] === key) {
                        vm.application.possible_funding.splice(i, 1);
                        break;
                    }
                }
            }
        };

        vm.application.supervisors = [];

        // User account details
        vm.access_token = $cookies.get('token');
        var userDetails = Authentication.getAuthenticatedAccount();
        if (userDetails != undefined) {
            var userRole = userDetails.userRole;
            vm.isAdmin = userRole === 'ADMIN';
            vm.username = userDetails.username;
        }

        // Populate checkboxes
        var applicationFieldChoicesPromise = Application.getCheckboxMultipleChoices().then(function (response) {
            vm.applicationFieldChoices = response.data;
        });

        // Fill list of supervisor usernames (this will include administrators as well)
        vm.currentlySelectedSupervisor = undefined;
        Admin.getAllStaffMembers().then(function (response) {
            vm.supervisors = response.data;
        });

        // Fill list of available academic years
        var academicYearsPromise = Application.getAllAcademicYears().then(function success(response) {
            vm.academicYears = response.data.academic_years;

            // Find default academic year
            vm.currentAcademicYear = Application.findDefaultAcademicYear(vm.academicYears);
            vm.application.academic_year = vm.currentAcademicYear;
        }, Toast.showHttpError);

        vm.creatorSupervisionFiles = {
            "APPLICATION_FORM": [],
            "RESEARCH_SUMMARY": [],
            "REFERENCE": [],
            "ADDITIONAL_MATERIAL": []
        };

        // Setup for editing
        if (!vm.newApplication) {
            var existingApplicationPromise = Application.getExistingApplication(applicationID).then(function (response) {
                vm.application = response.data["application"];

                // For easier UI-binding, we store the "creator", the "supervisor", and the "admin" supervision details separately
                vm.creatorSupervision = response.data["creator_supervision"];
                vm.adminSupervisions = response.data["admin_supervisions"];
                vm.supervisorSupervisions = response.data["supervisor_supervisions"];
                vm.supervisorSupervisionFiles = response.data["supervisor_supervision_files"];
                var creatorSupervisionFiles = response.data["creator_supervision_files"];

                // The following line guarantees we haven't lost any properties of the object.
                Object.assign(vm.creatorSupervisionFiles, creatorSupervisionFiles);
            });

            // After both requests have ended
            $q.all([academicYearsPromise, existingApplicationPromise]).then(function () {
                // Select existing academic year of the application
                for (var i = 0; i < vm.academicYears.length; i++) {
                    if (vm.academicYears[i].id == vm.application.academic_year.id) {
                        vm.application.academic_year = vm.academicYears[i];
                        break;
                    }
                }
            });

            $q.all([applicationFieldChoicesPromise, existingApplicationPromise]).then(function () {
                // Select existing possible funding
                for (var i = 0; i < vm.application.possible_funding.length; i++) {
                    vm.selectedPossibleFunding[vm.application.possible_funding[i]] = true;
                }
            });
        }

        var temporaryApplication = undefined;
        vm.enableEdit = function () {
            temporaryApplication = angular.copy(vm.application);
            vm.editable = true;
        };

        vm.disableEdit = function () {

            // TODO: check dirty, ask for confirm

            vm.editable = false;
            vm.application = angular.copy(temporaryApplication);

            // Whenever we assign vm.application, we need the appropriate academic year object reference.
            vm.application.academic_year = Application.findDefaultAcademicYear(vm.academicYears);
        };

        vm.updateApplication = function () {
            Application.updateApplication(vm.application).then(function () {
                vm.editable = false;
                Toast.showSuccess("Application saved!");
            }, Toast.showHttpError)
        };

        vm.taToolbar = [['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'pre', 'quote'],
            ['bold', 'italics', 'underline', 'strikeThrough', 'ul', 'ol', 'redo', 'undo', 'clear'],
            ['justifyLeft', 'justifyCenter', 'justifyRight', 'indent', 'outdent'],
            ['html', 'insertLink', 'wordcount', 'charcount']];

        vm.currentTag = undefined;
        vm.application.tag_words = [];
        vm.addCurrentTag = function () {

            // Check if tag is empty
            if (typeof vm.currentTag === "undefined" || !vm.currentTag.replace(/\s/g, '').length) {
                Toast.showInfo("Empty tag cannot be added.");
                return;
            }

            // Add / Upload tag
            var tagExists = false;
            if (vm.newApplication) {
                // Check if tag already exists
                tagExists = tagExists || vm.application.tag_words.indexOf(vm.currentTag) > -1;
                if (tagExists){
                    Toast.showInfo(vm.currentTag + " already exists as a tag.");
                    return;
                }

                // Add
                vm.application.tag_words.push(vm.currentTag);
                vm.currentTag = undefined;
            } else {
                // Check if tag already exists
                tagExists = vm.application.tags.some(function (el) {
                    return el.name === vm.currentTag;
                });
                if (tagExists){
                    Toast.showInfo(vm.currentTag + " already exists as a tag.");
                    return
                }

                // Upload
                Application.addTagToApplication(vm.application.id, vm.currentTag).then(function success(response) {
                    vm.application.tags.push(response.data.tag);
                    vm.currentTag = undefined;

                    Toast.showSuccess("Added!");
                }, Toast.showHttpError)
            }
        };

        vm.removeTag = function (tag) {
            if (vm.newApplication) {
                vm.application.tag_words = vm.application.tag_words.filter(function (word) {
                    return word !== tag;
                });
            } else {
                Application.deleteTagFromApplication(tag.id, vm.application.id).then(function success() {
                    vm.application.tags = vm.application.tags.filter(function (obj) {
                        return obj.id !== tag.id;
                    });
                    Toast.showSuccess("Tag removed!")
                });
            }
        };

        // These temporary supervisors later need to be persisted with the new application
        vm.temporarySupervisors = [];
        vm.addCurrentlySelectedSupervisor = function () {
            vm.addSupervisor(vm.currentlySelectedSupervisor);
            vm.currentlySelectedSupervisor = undefined;
        };

        vm.addSupervisor = function (supervisor) {
            if (vm.newApplication) {

                // Add to a temporary list of supervisors that will be submitted with the application
                if (vm.temporarySupervisors.indexOf(supervisor) == -1 && typeof supervisor !== "undefined") {
                    vm.temporarySupervisors.push(supervisor);

                    // Update supervisor recommendation
                    vm.recommendedSupervisors = vm.recommendedSupervisors.filter(function (obj) {
                        return obj.username !== supervisor.username;
                    });
                }
            } else {

                // Check if supervisor is already added
                var supervisionExists = false;
                for (var key in vm.supervisorSupervisions) {
                    if (vm.supervisorSupervisions.hasOwnProperty(key)) {
                        if (vm.supervisorSupervisions[key]["supervisor"]["username"] === supervisor.username) {
                            supervisionExists = true;
                            break;
                        }
                    }
                }

                // Attempt to add the supervisor on the back-end
                if (!supervisionExists) {
                    Application.addSupervision(applicationID, supervisor.username).then(function success(response) {
                        var newSupervision = response.data;
                        vm.supervisorSupervisions.push(newSupervision);

                        // Update supervisor recommendation
                        vm.recommendedSupervisors = vm.recommendedSupervisors = vm.recommendedSupervisors.filter(function (obj) {
                            return obj.username !== newSupervision.supervisor.username;
                        });

                        Toast.showSuccess(newSupervision.supervisor.username + ' was added as a supervisor!');
                    }, Toast.showHttpError)
                } else {
                    Toast.showInfo(supervisor.username + ' is already a supervisor!');
                }
            }
        };

        vm.removeTemporarySupervisor = function (supervisor) {
            var supervisorIndex = vm.temporarySupervisors.indexOf(supervisor);
            if (supervisorIndex != -1) {
                vm.temporarySupervisors.splice(supervisorIndex, 1);
            }
        };

        // Takes both tag objects and tag names
        vm.refreshRecommendedSupervisors = function (tags, tag_words) {
            tags = tags ? tags : [];
            tag_words = tag_words ? tag_words : [];
            vm.tagWordsForRecommendation = tag_words;
            for (var i = 0; i < tags.length; i++) {
                tag_words.push(tags[i].name);
            }

            Application.getRecommendedSupervisors(tag_words).then(function success(response) {
                // Filter out supervisors who have already been added
                vm.recommendedSupervisors = response.data;
                var existingSupervisors = angular.copy(vm.temporarySupervisors);
                for (var key in vm.supervisorSupervisions) {
                    if (vm.supervisorSupervisions.hasOwnProperty(key)) {
                        existingSupervisors.push(vm.supervisorSupervisions[key]["supervisor"])
                    }
                }

                for (var i = 0; i < existingSupervisors.length; i++) {
                    vm.recommendedSupervisors = vm.recommendedSupervisors.filter(function (obj) {
                        return obj.username !== existingSupervisors[i].username;
                    });
                }

            }, Toast.showHttpError);
        };

        vm.addAdminSupervision = function () {
            Application.addSupervision(applicationID, userDetails.username, "ADMIN").then(function success(response) {
                var newSupervision = response.data;
                vm.adminSupervisions.push(newSupervision);

                Toast.showSuccess(newSupervision.supervisor.username + ' was added as an administrator!');
            }, Toast.showHttpError)
        };

        vm.myAdminSupervisionExists = function () {
            if (typeof vm.adminSupervisions === "undefined") {
                return true;
            }
            for (var i = 0; i < vm.adminSupervisions.length; i++) {
                if (vm.adminSupervisions[i].supervisor.username === vm.username) {
                    return true;
                }
            }

            return false;
        };

        vm.deleteSupervision = function (supervisionId) {
            Application.deleteSupervision(supervisionId).then(function success() {

                // Update supervisions
                vm.supervisorSupervisions = vm.supervisorSupervisions.filter(function (obj) {
                    return obj.id !== supervisionId;
                });
                vm.adminSupervisions = vm.adminSupervisions.filter(function (obj) {
                    return obj.id !== supervisionId;
                });
                Toast.showSuccess('Supervisor was successfully removed!');
            }, Toast.showHttpError)
        };

        vm.uploadNewApplication = uploadNewApplication;

        vm.deleteApplication = function () {
            Application.deleteApplication(vm.application["id"]).then(function success() {
                Toast.showSuccess("Application successfully deleted!");
                $location.url('/search');

            }, Toast.showHttpError)
        };

        function uploadNewApplication() {
            var newFilesMap = {};
            var newFileDescriptions = {};
            for (var key in vm.newFilesIndex) {
                if (vm.newFilesIndex.hasOwnProperty(key)) {
                    var newFilesList = vm.newFilesIndex[key];
                    var counter = 0;
                    for (var i = 0; i < newFilesList.length; i++) {
                        var currentFileDetails = newFilesList[i];
                        if (typeof currentFileDetails.file === "undefined") {
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
            for (i = 0; i < vm.temporarySupervisors.length; i++) {
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