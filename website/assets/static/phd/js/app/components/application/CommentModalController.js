
(function () {
    'use strict';

    angular
        .module('phd.application.controllers')
        .controller('CommentModalController', CommentModalController);

    CommentModalController.$inject = ['$scope', 'Application'];

    function CommentModalController($scope, Application) {
        var vm = this;

        vm.supervisorComment = "";

        vm.postComment = function(){
            var supervisionId = typeof vm.supervision === "undefined" ? undefined : vm.supervision.id;
            Application.postComment(vm.applicationId, supervisionId, vm.supervisorComment).then(function(response){
                vm.supervision = response.data;
                vm.supervisorComment = "";

                toastr.success("Comment was successfully posted!");
            }, displayErrorMessage);
        };

        function displayErrorMessage(data){
            toastr.error(data.data.error, data.statusText + " " + data.status)
        }
    }
})();