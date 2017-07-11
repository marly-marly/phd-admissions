(function () {
    'use strict';

    angular
        .module('phd.application.directives')
        .directive('emailSenderModal', emailSenderModal);

    function emailSenderModal() {

        return {
            controller: 'EmailTemplateController',
            controllerAs: 'vm',
            restrict: 'E',
            scope: {
                supervision: '='
            },
            bindToController: true,
            templateUrl: '/static/phd/js/app/components/application/email-sender-modal.html'
        };
    }
})();