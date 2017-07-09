
(function () {
    'use strict';

    angular
        .module('phd.utilities.directives')
        .directive('enterDirective', enterDirective);

    enterDirective.$inject = ['$http'];

    function enterDirective($http) {

        return {
            link: function (scope, element, attrs) {
                $(element).keypress(function (e) {
                    if (e.keyCode == 13) {
                        e.preventDefault();
                        console.log("Enter pressed " + element.val())
                    }
                });
            }
        };
    }
})();