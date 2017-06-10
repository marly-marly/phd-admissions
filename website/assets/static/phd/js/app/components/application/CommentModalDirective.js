(function () {
    'use strict';

    angular
        .module('phd.application.directives')
        .directive('commentModal', commentModal);

    function commentModal() {

        return {
            controller: 'CommentModalController',
            controllerAs: 'vm',
            restrict: 'E',
            scope: {
                supervision: '='
            },
            bindToController: true,
            templateUrl: '/static/phd/js/app/components/application/comment-modal.html'
        };
    }
})();