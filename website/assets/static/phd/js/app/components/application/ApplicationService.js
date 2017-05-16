
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
            deleteFile: deleteFile,
            uploadFile: uploadFile
        };

        return Application;

        function uploadApplication(isNew, application, files, supervisors) {
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
                registry_comment: application.registry_comment || ""
            };

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
            return $http.get('/api/applications/additionals/application/');
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

        function uploadFile(supervisionId, files){
            return $http({
                method: 'POST',
                url: "/api/applications/file/",
                headers: {'Content-Type': undefined},
                transformRequest: function (data) {

                    // FormData is required in order to send both regular fields AND files to the back-end
                    var formData = new FormData();
                    formData.append("supervision_id", angular.toJson(data["model"]));

                    var files = data["files"];
                    for (var key in files) {
                        if (files.hasOwnProperty(key)) {
                            formData.append(key, files[key]);
                        }
                    }
                    formData.append(key, files[key]);

                    return formData;
                },
                data: {model: supervisionId, files: files}
            })
        }

        function deleteFile(fileId){
            return $http.delete('/api/applications/file/', {params: {file_id: fileId}})
        }
    }
})();