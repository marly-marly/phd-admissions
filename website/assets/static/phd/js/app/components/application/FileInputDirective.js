(function () {
    'use strict';

    angular
        .module('phd.application.directives')
        .directive('fileInput', fileInput);

    function fileInput() {

        return {
            controller: 'FileInputController',
            controllerAs: 'vm',
            restrict: 'E',
            scope: {
                isAdmin: '=',
                newApplication: '=',
                accessToken: '=',
                supervisionId: '=',
                fileType: '@',
                fileTypeReadable: '@',
                existingFiles: '=',
                hideFileTypeColumn: '@',
                singleInput: '@'
            },
            bindToController: true,
            templateUrl: '/static/phd/js/app/components/application/file-input.html'
        };
    }
})();