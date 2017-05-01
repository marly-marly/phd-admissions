
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

        function uploadApplication(isNew, application) {
            return $http.post('/api/applications/application/', {
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
            });
        }

        function getApplicationFieldChoices(){
            return $http.get('/api/applications/choices/application/');
        }
    }
})();