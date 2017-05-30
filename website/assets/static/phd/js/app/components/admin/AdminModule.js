
(function () {
    'use strict';

    angular
        .module('phd.admin', [
            'phd.admin.controllers',
            'phd.admin.services'
        ]);

    angular
        .module('phd.admin.controllers', ['ngRoute']);

    angular
        .module('phd.admin.services', []);
})();