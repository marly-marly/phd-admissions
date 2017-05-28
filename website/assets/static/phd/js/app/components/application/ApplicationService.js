
(function () {
    'use strict';

    angular
        .module('phd.application.services')
        .factory('Application', Application);

    Application.$inject = ['$http'];

    function Application($http) {

        var Application = {
            uploadApplication: uploadApplication,
            getApplicationFieldChoices: getApplicationFieldChoices,
            getExistingApplication: getExistingApplication,
            getSupervisorUsernames: getSupervisorUsernames,
            addSupervision: addSupervision,
            deleteSupervision: deleteSupervision,
            updateSupervision: updateSupervision,
            deleteFile: deleteFile,
            uploadFiles: uploadFile,
            uploadFile: uploadFile,
            postComment: postComment
        };

        return Application;

        function uploadApplication(isNew, application, files, fileDescriptions, supervisors) {
            var application_data = {
                new: isNew,
                registry_ref: application.registry_ref,
                surname: application.surname,
                forename: application.forename,
                possible_funding: application.possible_funding,
                funding_status: application.funding_status,
                origin: application.origin,
                student_type: application.student_type,
                supervisors: supervisors,
                research_subject: application.research_subject || "",
                registry_comment: application.registry_comment || "",
                file_descriptions: fileDescriptions
            };

            if (application.status !== null){
                application_data.status = application.status;
            }else{
                application_data.status = "PENDING";
            }

            return $http({
                method: 'POST',
                url: "/api/applications/application/",
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

        function getApplicationFieldChoices(){
            return $http.get('/api/applications/newFilesIndex/application/');
        }

        function getExistingApplication(id){
            return $http.get('/api/applications/application/', {params: {id: id}});
        }

        function getSupervisorUsernames(){
            return $http.get('/api/applications/supervisor/');
        }

        function addSupervision(applicationId, supervisor){
            return $http.post('/api/applications/supervision/', {action: "ADD", id: applicationId, supervisor: supervisor})
        }

        function deleteSupervision(supervisionId){
            return $http.post('/api/applications/supervision/', {action: "DELETE", supervision_id: supervisionId})
        }

        function postComment(supervisionId, comment){
            return $http.post('/api/applications/comment/', {supervision_id: supervisionId, content: comment})
        }

        function updateSupervision(supervisionId, supervision){
            return $http.put('/api/applications/supervision/', {supervision_id: supervisionId, supervision: supervision})
        }

        function uploadFiles(supervisionId, files, fileDescriptions){
            return $http({
                method: 'POST',
                url: "/api/applications/file/",
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
                url: "/api/applications/file/",
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
            return $http.delete('/api/applications/file/', {params: {file_id: fileId}})
        }
    }
})();