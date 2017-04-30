
(function () {
    'use strict';

    angular
        .module('phd.application', [
            'phd.application.controllers',
            'phd.application.services'
        ]);

    angular
        .module('phd.application.controllers', ['ngRoute']);

    angular
        .module('phd.application.services', []);
})();