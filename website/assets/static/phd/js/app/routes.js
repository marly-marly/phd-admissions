
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
            templateUrl: '/static/phd/js/app/components/authentication/register.html'
        }).when('/login', {
            controller: 'LoginController',
            controllerAs: 'vm',
            templateUrl: '/static/phd/js/app/components/authentication/login.html'
        }).when('/application/new', {
            controller: 'ApplicationController',
            controllerAs: 'vm',
            templateUrl: '/static/phd/js/app/components/application/application.html'
        }).when('/application/edit/:id/:registryRef', {
            controller: 'ApplicationController',
            controllerAs: 'vm',
            templateUrl: '/static/phd/js/app/components/application/application.html'
        }).when('/home', {
            controller: 'IndexController',
            controllerAs: 'vm',
            templateUrl: '/static/phd/js/app/components/home/home.html'
        }).when('/search', {
            controller: 'SearchController',
            controllerAs: 'vm',
            templateUrl: '/static/phd/js/app/components/search/search.html',
            reloadOnSearch: false
        }).when('/admin', {
            controller: 'AdminController',
            controllerAs: 'vm',
            templateUrl: '/static/phd/js/app/components/admin/admin.html'
        }).otherwise({
            redirectTo: '/home'
        });
    }
})();