
(function () {
    'use strict';

    angular
        .module('phd.application.controllers')
        .controller('FileInputController', FileInputController);

    FileInputController.$inject = ['$scope', 'Application'];

    function FileInputController($scope, Application) {
        var vm = this;

        if (angular.isUndefined(vm.hideFileTypeColumn)){
            vm.hideFileTypeColumn = false;
        }

        if (angular.isUndefined(vm.singleInput)){
            vm.singleInput = false;
        }

        if (angular.isUndefined(vm.newFilesIndex)){
            vm.newFilesIndex = {};
        }

        vm.maximumNumberOfFilesReached = (vm.singleInput && (vm.existingFiles.length !== 0 ||
                                                          (vm.newFilesIndex.hasOwnProperty(vm.fileType) && vm.newFilesIndex[vm.fileType].length !== 0)));

        // Register new files selected by the user
        vm.registerFile = function(event){
            var files = event.target.files;
            var fileIndex = Number(event.target.id);

            // If no file is selected, and there was one selected before, then remove the old one
            if (files.length == 0){
                vm.newFilesIndex[vm.fileType][fileIndex]["file"] = undefined;
            }else{
                // Overwrite/add the new one
                vm.newFilesIndex[vm.fileType][fileIndex]["file"] = files[0];
            }

            // This lets someone select the same file again in the same input field
            event.target.value = "";

            // This fires the binding update cycle for the UI
            $scope.$apply();
        };

        // Cancels the file selection
        vm.cancelFileSelection = function(index){
            vm.newFilesIndex[vm.fileType][index]['file'] = undefined;
        };

        // Uploads all newFiles corresponding to a specific supervision
        vm.uploadFile = function(index){
            Application.uploadFile(vm.supervisionId, vm.newFilesIndex[vm.fileType][index].file, vm.fileType + "_" + index, vm.newFilesIndex[vm.fileType][index].description).then(
                function success(response){

                    // Update view-model variables
                    var documentations = response.data["documentations"];
                    if (typeof vm.existingFiles === "undefined"){
                        vm.existingFiles = documentations;
                    }else{
                        vm.existingFiles = vm.existingFiles.concat(documentations);
                    }

                    // Remove uploaded file from the temporary storage
                    vm.newFilesIndex[vm.fileType].splice(index, 1);

                    // Toast
                    var toastMessage = "";
                    for (var i=0; i<documentations.length; i++){
                        toastMessage += "- " + documentations[i]["file_name"] + "<br>";
                    }
                    toastr.options.escapeHtml = false;
                    toastr.success(toastMessage, "Successfully uploaded:")
                },displayErrorMessage
            );
        };

        // Removes a specific file from the server
        vm.deleteFile = function(fileId){
            Application.deleteFile(fileId).then(
                function success(){
                    for (var i = 0; i < vm.existingFiles.length; i++){
                        if (vm.existingFiles[i]["id"] === fileId){
                            vm.existingFiles.splice(i, 1);
                            break;
                        }
                    }

                    toastr.success("File successfully removed!")
                },displayErrorMessage
            )
        };

        // Dynamically appends more file inputs
        vm.addNewFileInput = function() {

            // Initialise the appropriate array for new files
            if (!(vm.fileType in vm.newFilesIndex)){
                vm.newFilesIndex[vm.fileType] = [];
            }

            vm.newFilesIndex[vm.fileType].push({
                file: undefined,
                description: ""
            });
        };

        vm.removeFileInput = function(index) {
            vm.newFilesIndex[vm.fileType].splice(index, 1);
        };

        function displayErrorMessage(data){
            toastr.error(data.data.error, data.statusText + " " + data.status)
        }
    }
})();