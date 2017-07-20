
(function () {
    'use strict';

    angular
        .module('phd.application.controllers')
        .controller('EmailSenderModalController', EmailSenderModalController);

    EmailSenderModalController.$inject = ['$location', 'Admin', 'Authentication', 'Toast'];

    function EmailSenderModalController($location, Admin, Authentication, Toast) {

        // If the user is not authenticated, they should not be here.
        if (!Authentication.isAuthenticated()) {
            $location.url('/login');
            return;
        }

        var vm = this;

        vm.taToolbar = [['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'pre', 'quote'],
                        ['bold', 'italics', 'underline', 'strikeThrough', 'ul', 'ol', 'redo', 'undo', 'clear'],
                        ['justifyLeft', 'justifyCenter', 'justifyRight', 'indent', 'outdent'],
                        ['html','insertLink', 'wordcount', 'charcount']];

        vm.sendEmail = function(){
            Admin.sendEmail(vm.emailContent, vm.supervision.id, false).then(function success(){
                Toast.showSuccess("Email sent to " + vm.supervision.supervisor.first_name + " " + vm.supervision.supervisor.last_name + "!");
            }, Toast.showHttpError)
        }
    }
})();