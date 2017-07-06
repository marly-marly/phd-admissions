
(function () {
    'use strict';

    angular
        .module('phd.authentication', [
            'phd.authentication.controllers',
            'phd.authentication.services'
        ]);

    angular
        .module('phd.authentication.controllers', []);

    angular
        .module('phd.authentication.services', ['ngCookies']);
})();