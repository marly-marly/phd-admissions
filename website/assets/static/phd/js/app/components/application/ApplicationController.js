
(function () {
    'use strict';

    angular
        .module('phd.application.controllers')
        .controller('ApplicationController', ApplicationController);

    ApplicationController.$inject = ['$scope', 'Application'];

    function ApplicationController($scope, Application) {
        var vm = this;
        vm.application = {};
        vm.application.supervisors = [];

        // Register new files
        var files = {};
        $scope.setFiles = function(element) {
            $scope.$apply(function(scope) {
                var element_id = element.id;
                var element_files = element.files;
                if (element_files.length == 0){
                    if (element_id in files){
                        delete files[element_id];
                    }
                }else{
                    files[element_id] = element_files[0];
                }
                console.log(files);
            });
        };

        // Dynamically append file inputs
        vm.additionals = [];
        vm.addNewAdditional = function() {
            var newItemNo = (vm.additionals.length == 0 ? 0 : vm.additionals[vm.additionals.length-1] + 1);
            vm.additionals.push(newItemNo);
        };

        vm.removeAdditional = function(index, id) {
            vm.additionals.splice(index, 1);
            delete files[id];
            console.log(id);
        };

        vm.uploadApplication = uploadApplication;

        Application.getApplicationFieldChoices().then(function(response){
            vm.applicationFieldChoices = response.data;
        });

        function uploadApplication(){
            Application.uploadApplication(true, vm.application, files).then(uploadSuccess, uploadError);

            function uploadSuccess() {
                window.location = 'application/new';
            }

            function uploadError(status) {
                console.error('Upload failed: ' + status);
            }
        }
    }
})();