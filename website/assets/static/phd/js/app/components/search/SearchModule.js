
(function () {
    'use strict';

    angular
        .module('phd.search', [
            'phd.search.controllers',
            'phd.search.services'
        ]);

    angular
        .module('phd.search.controllers', ['ngRoute']);

    angular
        .module('phd.search.services', []);
})();