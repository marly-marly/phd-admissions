(function () {
    'use strict';

    angular
        .module('phd.email.directives')
        .directive('emailPreviewModal', emailPreviewModal);

    function emailPreviewModal() {

        return {
            controller: 'EmailPreviewModalController',
            controllerAs: 'vm',
            restrict: 'E',
            scope: {
                emailPreview: '='
            },
            bindToController: true,
            templateUrl: '/static/phd/js/app/components/email/email-preview-modal.html'
        };
    }
})();