
(function () {
    'use strict';

    angular
        .module('phd.application.services')
        .factory('Application', Application);

    Application.$inject = ['$http'];

    function Application($http) {

        return {
            uploadApplication: uploadApplication,
            updateApplication: updateApplication,
            getCheckboxMultipleChoices: getCheckboxMultipleChoices,
            getExistingApplication: getExistingApplication,
            getSupervisorUsernames: getSupervisorUsernames,
            getSupervisorStaff: getSupervisorStaff,
            addSupervision: addSupervision,
            deleteSupervision: deleteSupervision,
            updateSupervision: updateSupervision,
            deleteFile: deleteFile,
            uploadFiles: uploadFile,
            uploadFile: uploadFile,
            deleteApplication: deleteApplication,
            getAllAcademicYears: getAllAcademicYears,
            findDefaultAcademicYear: findDefaultAcademicYear,
            getAllTagsWithCounts: getAllTagsWithCounts,
            addTagToApplication: addTagToApplication,
            deleteTagFromApplication: deleteTagFromApplication,
            allocateSupervision: allocateSupervision,
            deAllocateSupervision: deAllocateSupervision,
            getApplicationFields: getApplicationFields,
            snakeCaseToPretty: snakeCaseToPretty,
            getRecommendedSupervisors: getRecommendedSupervisors
        };

        function uploadApplication(application, files, fileDescriptions, supervisors) {
            // TODO: generalise
            var application_data = {
                registry_ref: application.registry_ref,
                surname: application.surname,
                forename: application.forename,
                gender: application.gender,
                possible_funding: application.possible_funding,
                funding_status: application.funding_status,
                origin: application.origin,
                student_type: application.student_type,
                supervisors: supervisors,
                research_subject: application.research_subject || "",
                administrator_comment: application.administrator_comment || "",
                phd_admission_tutor_comment: application.phd_admission_tutor_comment || "",
                file_descriptions: fileDescriptions,
                academic_year_id: application.academic_year.id,
                tag_words: application.tag_words
            };

            if (application.status !== null){
                application_data.status = application.status;
            }else{
                application_data.status = "PENDING";
            }

            return $http({
                method: 'POST',
                url: "/api/phd/application/",
                headers: { 'Content-Type': undefined },
                transformRequest: function (data) {

                    // FormData is required in order to send both regular fields AND files to the back-end
                    var formData = new FormData();
                    formData.append("application", angular.toJson(data["model"]));

                    var files = data["files"];
                    for (var key in files) {
                        if (files.hasOwnProperty(key)) {
                            formData.append(key, files[key]);
                        }
                    }
                    formData.append(key, files[key]);

                    return formData;
                },
                data: { model: application_data, files: files }
            });
        }

        function updateApplication(application) {
            var application_data = {
                registry_ref: application.registry_ref,
                surname: application.surname,
                forename: application.forename,
                gender: application.gender,
                possible_funding: application.possible_funding,
                funding_status: application.funding_status,
                origin: application.origin,
                student_type: application.student_type,
                status: application.status,
                research_subject: application.research_subject || "",
                administrator_comment: application.administrator_comment || "",
                phd_admission_tutor_comment: application.phd_admission_tutor_comment || "",
                academic_year_id: application.academic_year.id
            };

            return $http.put("/api/phd/application/", {id: application.id, application: application_data});
        }

        function getCheckboxMultipleChoices(){
            return $http.get('/api/phd/application/field_choices/');
        }

        function getExistingApplication(id){
            return $http.get('/api/phd/application/', {params: {id: id}});
        }

        function getSupervisorUsernames(){
            return $http.get('/api/auth/supervisor/');
        }

        function getSupervisorStaff(){
            return $http.get('/api/auth/supervisor_staff/')
        }

        function addSupervision(applicationId, supervisor, type){
            return $http.post('/api/phd/supervision/', {id: applicationId, supervisor: supervisor, supervision_type: type})
        }

        function deleteSupervision(supervisionId){
            return $http.delete('/api/phd/supervision/', {data: {supervision_id: supervisionId}})
        }

        function updateSupervision(supervisionId, supervision){
            return $http.put('/api/phd/supervision/', {supervision_id: supervisionId, supervision: supervision})
        }

        function uploadFiles(supervisionId, files, fileDescriptions){
            return $http({
                method: 'POST',
                url: "/api/phd/file/",
                headers: {'Content-Type': undefined},
                transformRequest: function (data) {

                    // FormData is required in order to send both regular fields AND files to the back-end
                    var formData = new FormData();
                    formData.append("details", angular.toJson(data["model"]));

                    var files = data["files"];
                    for (var key in files) {
                        if (files.hasOwnProperty(key)) {
                            formData.append(key, files[key]);
                        }
                    }

                    return formData;
                },
                data: {model: {supervision_id: supervisionId, file_descriptions: fileDescriptions}, files: files}
            })
        }

        function uploadFile(supervisionId, file, fileId, fileDescription){
            var newFileDescriptions = {};
            newFileDescriptions[fileId] = fileDescription;

            return $http({
                method: 'POST',
                url: "/api/phd/file/",
                headers: {'Content-Type': undefined},
                transformRequest: function (data) {

                    // FormData is required in order to send both regular fields AND files to the back-end
                    var formData = new FormData();
                    formData.append("details", angular.toJson(data["model"]));
                    formData.append(fileId, data["file"]);

                    return formData;
                },
                data: {model: {supervision_id: supervisionId, file_descriptions: newFileDescriptions}, file: file}
            })
        }

        function deleteFile(fileId){
            return $http.delete('/api/phd/file/', {data: {file_id: fileId}})
        }

        function deleteApplication(applicationId){
            return $http.delete('/api/phd/application/', {data: {id: applicationId}})
        }

        function getAllAcademicYears(){
            return $http.get('/api/phd/admin/academic_year/');
        }

        function getAllTagsWithCounts(){
            return $http.get('/api/phd/application/tags/');
        }

        function addTagToApplication(applicationId, tagName){
            return $http.post('/api/phd/application/tags/', {application_id: applicationId, name: tagName})
        }

        function deleteTagFromApplication(tagId, applicationId) {
            return $http.delete('/api/phd/application/tags/', {data: {application_id: applicationId, tag_id: tagId}})
        }

        function allocateSupervision(supervisionId){
            return $http.post('/api/phd/supervision_allocation/', {supervision_id: supervisionId})
        }

        function deAllocateSupervision(supervisionId) {
            return $http.delete('/api/phd/supervision_allocation/', {data: {supervision_id: supervisionId}})
        }

        function findDefaultAcademicYear(academicYears){
            var defaultAcademicYear;
            for (var i=0; i<academicYears.length; i++){
                if (academicYears[i].default){
                    defaultAcademicYear = academicYears[i];
                    break;
                }
            }

            return defaultAcademicYear;
        }

        function getApplicationFields(){
            return $http.get('/api/phd/application/fields/');
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

        function getRecommendedSupervisors(tags){
            return $http.get('/api/phd/recommended_supervisors/', {params: {tags: tags}});
        }
    }
})();