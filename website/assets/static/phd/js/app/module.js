angular
    .module('phdAdmissionsApp', []);

(function () {
    'use strict';

    angular
        .module('phdAdmissionsApp', [
            'routes',
            'config',
            'phd.authentication',
            'phd.navbar',
            'phd.home',
            'phd.application',
            'phd.search',
            'tableSort',
            'ngAnimate',
            'ui.bootstrap',
            'ngSanitize',
            'mwl.confirm'
        ]);

    angular
        .module('routes', ['ngRoute']);

    angular
        .module('config', []);

    angular
        .module('phdAdmissionsApp')
        .factory('httpRequestInterceptor', httpRequestInterceptor)
        .config(function($httpProvider) {
            $httpProvider.interceptors.push('httpRequestInterceptor');
        })
        .run(run);

    run.$inject = ['$http'];

    function run($http) {
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
        $http.defaults.xsrfCookieName = 'csrftoken';
    }

    function httpRequestInterceptor($cookies, $q) {
        return {
            request: function (config) {

                var token = $cookies.get('token');
                if (typeof token !== "undefined"){
                    config.headers['Authorization'] = 'JWT ' + token;
                }

                return config;
            },

            requestError: function(rejection) {
                return $q.reject(rejection);
            },

            response: function(res) {
                return res;
            },

            responseError: function(rejection) {
                return $q.reject(rejection);
            }
        }
    }
})();