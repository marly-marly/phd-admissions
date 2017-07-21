(function () {
    'use strict';

    angular
        .module('phd.email.directives')
        .directive('emailSenderModal', emailSenderModal);

    function emailSenderModal() {

        return {
            controller: 'EmailSenderModalController',
            controllerAs: 'vm',
            restrict: 'E',
            scope: {
                supervision: '=',
                emailContent: '='
            },
            bindToController: true,
            templateUrl: '/static/phd/js/app/components/email/email-sender-modal.html'
        };
    }
})();