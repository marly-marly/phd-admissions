(function () {
    'use strict';

    angular
        .module('phd.application.directives')
        .directive('supervisorRecommendationModal', supervisorRecommendationModal);

    function supervisorRecommendationModal() {

        return {
            controller: 'SupervisorRecommendationModalController',
            controllerAs: 'vm',
            restrict: 'E',
            scope: {
                recommendedSupervisors: "=",
                addSupervisor: '&',
                currentAcademicYear: "=",
                tagWordsForRecommendation: "="
            },
            bindToController: true,
            templateUrl: '/static/phd/js/app/components/application/supervisor-recommendation-modal.html'
        };
    }
})();