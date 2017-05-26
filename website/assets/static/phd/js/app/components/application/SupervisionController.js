
(function () {
    'use strict';

    angular
        .module('phd.application.controllers')
        .controller('SupervisionController', SupervisionController);

    SupervisionController.$inject = ['$scope', '$cookies', 'Application'];

    function SupervisionController($scope, $cookies, Application) {
        var vm = this;
        vm.supervisorComment = "";

        vm.postComment = function(supervisionId){
            Application.postComment(supervisionId, vm.supervisorComment).then(function(response){
                var newComment = response.data;
                vm.supervision.comments.push(newComment);

                toastr.success("Comment was successfully posted!");
            });
        };

        $scope.setFiles = function(element) {
            $scope.$apply(function(scope) {
                var fileIndex = Number(element.name);
                var elementFiles = element.files;

                // If no file is selected, and there was one selected before, then eliminate the old one
                if (elementFiles.length == 0){
                    vm.newFilesIndex[fileIndex].file = undefined;
                }else{
                    // Overwrite/add the new one
                    vm.newFilesIndex[fileIndex].file = elementFiles[0];
                }
            });
        };

        vm.newFilesIndex = [];
        vm.addNewFileInput = function() {
            vm.newFilesIndex.push({
                file: undefined,
                description: ""
            });
        };

        vm.removeFileInput = function(index) {
            vm.newFilesIndex.splice(index, 1);
        };

        // Uploads a specific file corresponding to the given ID, from newFiles, to a specific supervision
        vm.uploadFile = function(index){
            Application.uploadFile(vm.supervision.id, vm.newFilesIndex[index].file, "ADDITIONAL_MATERIAL_" + index, vm.newFilesIndex[index].description).then(
                function success(response){

                    // Update view-model variables
                    var documentations = response.data["documentations"];
                    if (typeof vm.supervisionFiles === "undefined"){
                        vm.supervisionFiles = documentations;
                    }else{
                        vm.supervisionFiles = vm.supervisionFiles.concat(documentations);
                    }

                    vm.removeFileInput(index);

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
    }
})();