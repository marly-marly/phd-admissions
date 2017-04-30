
(function () {
    'use strict';

    angular
        .module('phd.home.controllers')
        .controller('IndexController', IndexController);

    IndexController.$inject = ['$scope'];

    function IndexController($scope) {
        var vm = this;

        activate();

        function activate() {
        }
    }
})();