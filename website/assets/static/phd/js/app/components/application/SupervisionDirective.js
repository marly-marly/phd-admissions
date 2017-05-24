(function () {
    'use strict';

    angular
        .module('phd.application.directives')
        .directive('supervision', supervision);

    function supervision() {

        return {
            controller: 'SupervisionController',
            controllerAs: 'vm',
            restrict: 'E',
            scope: {
                supervision: '=',
                applicationFieldChoices: '=',
                supervisionFiles: '='
            },
            bindToController: true,
            templateUrl: '/static/phd/js/app/components/application/supervision.html'
        };
    }
})();