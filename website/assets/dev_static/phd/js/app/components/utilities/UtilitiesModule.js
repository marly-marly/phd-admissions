
(function () {
    'use strict';

    angular
        .module('phd.utilities', [
            'phd.utilities.directives',
            'phd.utilities.services',
            'phd.utilities.CaseFilter',
            'phd.utilities.filters'
        ]);

    angular
        .module('phd.utilities.directives', []);

    angular
        .module('phd.utilities.services', []);

    angular
        .module('phd.utilities.CaseFilter', []);

    angular
        .module('phd.utilities.filters', []);
})();