
(function () {
    'use strict';

    angular
        .module('phd.email.services')
        .factory('Email', Email);

    Email.$inject = ['$http'];

    function Email($http) {

        return {
            getEmailTemplate: getEmailTemplate,
            updateEmailTemplate: updateEmailTemplate,
            getEmailPreview: getEmailPreview,
            getGeneratedEmailPreview: getGeneratedEmailPreview,
            sendEmail: sendEmail
        };

        function getEmailTemplate(){
            return $http.get('/api/phd/admin/email/');
        }

        function updateEmailTemplate(value){
            return $http.put('/api/phd/admin/email/', {value: value});
        }

        function getEmailPreview(emailTemplate, supervisionId){
            return $http.post('/api/phd/admin/email_preview/', {email_template: emailTemplate, supervision_id: supervisionId});
        }

        function getGeneratedEmailPreview(supervisionId){
            return $http.get('/api/phd/admin/email_preview/', {params: {supervision_id: supervisionId}});
        }

        function sendEmail(emailTemplate, supervisionId, template){
            return $http.post('/api/phd/admin/email_send/', {email_template: emailTemplate, supervision_id: supervisionId, template: template});
        }
    }
})();