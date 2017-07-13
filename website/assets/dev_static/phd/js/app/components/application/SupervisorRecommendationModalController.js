
(function () {
    'use strict';

    angular
        .module('phd.application.controllers')
        .controller('SupervisorRecommendationModalController', SupervisorRecommendationModalController);

    SupervisorRecommendationModalController.$inject = ['$httpParamSerializer'];

    function SupervisorRecommendationModalController($httpParamSerializer) {
        var vm = this;

        vm.tagsQueryString = function(){
            return $httpParamSerializer({tags: vm.tagWordsForRecommendation});
        }
    }
})();