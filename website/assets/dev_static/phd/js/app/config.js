(function () {
    'use strict';

    angular
        .module('config')
        .config(config);

    config.$inject = ['$locationProvider'];

    // Enable HTML 5 routing
    function config($locationProvider) {
        $locationProvider.html5Mode(true);
        $locationProvider.hashPrefix('!');
    }
})();