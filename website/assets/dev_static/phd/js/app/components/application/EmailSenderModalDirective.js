(function () {
    'use strict';

    angular
        .module('phd.application.directives')
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
            templateUrl: '/static/phd/js/app/components/application/email-sender-modal.html'
        };
    }
})();