
(function () {
    'use strict';

    angular
        .module('phd.statistics', [
            'phd.statistics.controllers',
            'phd.statistics.services'
        ]);

    angular
        .module('phd.statistics.controllers', ['chart.js']);

    angular
        .module('phd.statistics.services', []);
})();