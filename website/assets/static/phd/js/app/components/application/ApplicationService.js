
(function () {
    'use strict';

    angular
        .module('phd.application.services')
        .factory('Application', Application);

    Application.$inject = ['$http'];

    function Application($http) {

        var Application = {
            uploadApplication: uploadApplication,
            getApplicationFieldChoices: getApplicationFieldChoices
        };

        return Application;

        function uploadApplication(isNew, application, files) {
            var application_data = {
                new: isNew,
                registry_ref: application.registryRef,
                surname: application.surname,
                forename: application.forename,
                possible_funding: application.possibleFunding,
                funding_status: application.fundingStatus,
                origin: application.origin,
                student_type: application.studentType,
                supervisors: application.supervisors,
                research_subject: application.researchSubject || "",
                registry_comment: application.registryComment || ""
            };

            return $http({
                method: 'POST',
                url: "/api/applications/application/",
                headers: { 'Content-Type': undefined },
                transformRequest: function (data) {

                    // FormData is required in order to send both regular fields AND files to the back-end
                    var formData = new FormData();
                    formData.append("application",  angular.toJson(data["model"]));

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
    }
})();