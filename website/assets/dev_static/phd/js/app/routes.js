
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
        }).when('/statistics', {
            controller: 'StatisticsController',
            controllerAs: 'vm',
            templateUrl: '/static/phd/js/app/components/statistics/statistics.html'
        }).when('/admin/staff_roles', {
            controller: 'StaffController',
            controllerAs: 'vm',
            templateUrl: '/static/phd/js/app/components/admin/staff_roles.html'
        }).when('/admin/academic_years', {
            controller: 'AcademicYearController',
            controllerAs: 'vm',
            templateUrl: '/static/phd/js/app/components/admin/academic_years.html'
        }).when('/admin/tags', {
            controller: 'TagsController',
            controllerAs: 'vm',
            templateUrl: '/static/phd/js/app/components/admin/tags.html'
        }).when('/admin/email', {
            controller: 'EmailTemplateController',
            controllerAs: 'vm',
            templateUrl: '/static/phd/js/app/components/email/email_template.html'
        }).otherwise({
            redirectTo: '/home'
        });
    }
})();