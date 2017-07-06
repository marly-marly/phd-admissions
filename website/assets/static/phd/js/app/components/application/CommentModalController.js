
(function () {
    'use strict';

    angular
        .module('phd.application.controllers')
        .controller('CommentModalController', CommentModalController);

    CommentModalController.$inject = ['Application', 'Toast'];

    function CommentModalController(Application, Toast) {
        var vm = this;

        vm.supervisorComment = "";

        vm.postComment = function(){
            var supervisionId = typeof vm.supervision === "undefined" ? undefined : vm.supervision.id;
            Application.postComment(vm.applicationId, supervisionId, vm.supervisorComment).then(function(response){
                vm.supervision = response.data;
                vm.supervisorComment = "";

                Toast.showSuccess("Comment was successfully posted!");
            }, Toast.showHttpError);
        };
    }
})();