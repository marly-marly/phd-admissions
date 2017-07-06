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
                newApplication: '=',
                accessToken: '=',
                supervisionId: '=',
                fileType: '@',
                fileTypeReadable: '@',
                existingFiles: '=',
                hideFileTypeColumn: '@',
                singleInput: '@',
                newFilesIndex: '=?', // This variable is optional
                allowedToAddFile: '='
            },
            bindToController: true,
            templateUrl: '/static/phd/js/app/components/application/file-input.html'
        };
    }
})();