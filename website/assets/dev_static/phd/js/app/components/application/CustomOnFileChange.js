(function () {
    'use strict';

    angular
        .module('phd.application.directives')
        .directive('customOnFileChange', customOnFileChange);

    function customOnFileChange() {

        return {
            restrict: 'A',
            link: function (scope, element, attrs) {
                var onChangeHandler = scope.$eval(attrs.customOnFileChange);
                element.bind('change', onChangeHandler);
            }
        };
    }
})();