
(function () {
    'use strict';

    angular
        .module('phd.navbar.directives')
        .directive('navbar', navbar);

    function navbar() {

        return {
            controller: 'NavbarController',
            controllerAs: 'vm',
            restrict: 'E',
            scope: {
                posts: '='
            },
            templateUrl: '/static/phd/js/app/components/navbar/navbar.html'
        };
    }
})();