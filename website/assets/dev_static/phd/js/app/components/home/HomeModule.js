
(function () {
    'use strict';

    angular
        .module('phd.home', [
            'phd.home.controllers',
            'phd.home.services'
        ]);

    angular
        .module('phd.home.controllers', ['ngRoute']);

    angular
        .module('phd.home.services', []);
})();