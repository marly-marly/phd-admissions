
(function () {
    'use strict';

    angular
        .module('phd.home.services')
        .factory('Home', Home);

    Home.$inject = ['$http'];

    function Home($http) {
        return {}
    }
})();