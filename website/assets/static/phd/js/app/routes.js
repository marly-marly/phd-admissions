
(function () {
    'use strict';

    angular
        .module('routes')
        .config(config);

    config.$inject = ['$routeProvider'];

    function config($routeProvider) {
        $routeProvider.when('/register', {
            controller: 'RegisterController',
            controllerAs: 'vm',
            templateUrl: '/static/phd/js/app/components/authentication/register.html',
            activeTab: 'register'
        }).when('/login', {
            controller: 'LoginController',
            controllerAs: 'vm',
            templateUrl: '/static/phd/js/app/components/authentication/login.html',
            activeTab: 'login'
        }).when('/application/new', {
            controller: 'ApplicationController',
            controllerAs: 'vm',
            templateUrl: '/static/phd/js/app/components/application/application.html',
            activeTab: 'application/new'
        }).otherwise({
            redirectTo: '/home'
        });
    }
})();