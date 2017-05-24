
(function () {
    'use strict';

    angular
        .module('phd.application.controllers')
        .controller('SupervisionController', SupervisionController);

    SupervisionController.$inject = ['$scope', '$cookies', 'Application'];

    function SupervisionController($scope, $cookies, Application) {
        var vm = this;
        vm.fileDescriptions = {};
        vm.supervisorComment = "";

        vm.postComment = function(supervisionId){
            Application.postComment(supervisionId, vm.supervisorComment);
        };

        // Removes a specific file from the server
        vm.deleteFile = function(fileId){
            Application.deleteFile(fileId).then(function(response){
                for (var i = 0; i++; i < vm.creatorSupervisionFiles.length){
                    if (vm.creatorSupervisionFiles[i]["id"] === fileId){
                        vm.creatorSupervisionFiles.splice(i, 1);
                        break;
                    }
                }
            })
        };

        // Register new newFiles
        vm.newFiles = {};
        $scope.setFiles = function(element) {
            $scope.$apply(function(scope) {
                var element_id = element.id;
                var element_files = element.files;

                // If not file selected, and there was one selected before, then remove the old one
                if (element_files.length == 0){
                    if (element_id in vm.newFiles){
                        delete vm.newFiles[element_id];
                    }
                }else{
                    // Otherwise overwrite/add the new one
                    vm.newFiles[element_id] = element_files[0];
                }
            });
        };

        vm.multiFileIndex = [];
        vm.addNewFileInput = function() {
            var newItemNo = (vm.multiFileIndex.length == 0 ? 0 : vm.multiFileIndex[vm.multiFileIndex.length-1] + 1);
            vm.multiFileIndex.push(newItemNo);

            console.log(vm.multiFileIndex);
        };

        vm.removeFileInput = function(index, id) {
            vm.multiFileIndex.splice(index, 1);

            // Don't forget to remove file registered for the input
            delete vm.newFiles[id.concat(index)];
        };

        vm.updateSupervision = function(data){

            var supervisionId = data.id;
            Application.updateSupervision(supervisionId, {acceptance_condition: vm.supervision.acceptance_condition, recommendation: vm.supervision.recommendation});
            uploadFile(supervisionId);
        };

        // Uploads all newFiles corresponding to a specific supervision
        function uploadFile(supervisionId){
            Application.uploadFile(supervisionId, vm.newFiles, vm.fileDescriptions);
        }
    }
})();