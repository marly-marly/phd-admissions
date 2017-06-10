
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
            Application.postComment(vm.supervision.id, vm.supervisorComment).then(function(response){
                var newComment = response.data;
                vm.supervision.comments.push(newComment);
                vm.supervisorComment = "";

                toastr.success("Comment was successfully posted!");
            }, displayErrorMessage);
        };

        function displayErrorMessage(data){
            toastr.error(data.data.error, data.statusText + " " + data.status)
        }
    }
})();