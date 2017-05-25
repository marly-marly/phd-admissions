
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
            Application.postComment(supervisionId, vm.supervisorComment).then(function(response){
                var newComment = response.data;
                vm.supervision.comments.push(newComment);
                toastr.success("Comment was successfully posted!");
            });
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
        };

        vm.removeFileInput = function(index, id) {
            vm.multiFileIndex.splice(index, 1);

            // Don't forget to remove file registered for the input
            delete vm.newFiles[id.concat(index)];
            delete vm.fileDescriptions[id.concat(index)];
        };

        function removeFileInputByFileId(fileId){
            var indexOfLastUnderscore = fileId.lastIndexOf("_");
            var fileInputId = Number(fileId.substring(indexOfLastUnderscore+1, fileId.length));

            vm.multiFileIndex.splice(fileInputId, 1);
            delete vm.newFiles[fileId];
            delete vm.fileDescriptions[fileId];
        }

        // Uploads a specific file corresponding to the given ID, from newFiles, to a specific supervision
        vm.uploadFile = function(fileId){
            Application.uploadFile(vm.supervision.id, vm.newFiles[fileId], fileId, vm.fileDescriptions[fileId]).then(
                function success(response){

                    // Update view-model variables
                    var documentations = response.data["documentations"];
                    if (typeof vm.supervisionFiles === "undefined"){
                        vm.supervisionFiles = documentations;
                    }else{
                        vm.supervisionFiles = vm.supervisionFiles.concat(documentations);
                    }

                    removeFileInputByFileId(fileId);

                    // Toast
                    var toastMessage = "";
                    for (var i=0; i<documentations.length; i++){
                        toastMessage += "- " + documentations[i]["file_name"];
                    }
                    toastr.success(toastMessage, "Successfully uploaded:")
                },

                function error(data){
                    toastr.error(data.data.error, data.statusText + " " + data.status)
                }
            );
        };

        // Removes a specific file from the server
        vm.deleteFile = function(fileId){
            Application.deleteFile(fileId).then(
                function success(){
                    for (var i = 0; i < vm.supervisionFiles.length; i++){
                        if (vm.supervisionFiles[i]["id"] === fileId){
                            vm.supervisionFiles.splice(i, 1);
                            break;
                        }
                    }

                    toastr.success("File successfully removed!")
                }, function error(data){
                    toastr.error(data.data.error, data.statusText + " " + data.status)
                }
            )
        };

        vm.updateSupervision = function(data){

            var supervisionId = data.id;
            Application.updateSupervision(supervisionId, {acceptance_condition: vm.supervision.acceptance_condition, recommendation: vm.supervision.recommendation});
            uploadAllFiles(supervisionId);
        };

        // Uploads all newFiles corresponding to a specific supervision
        function uploadAllFiles(supervisionId){
            Application.uploadFile(supervisionId, vm.newFiles, vm.fileDescriptions);
        }
    }
})();