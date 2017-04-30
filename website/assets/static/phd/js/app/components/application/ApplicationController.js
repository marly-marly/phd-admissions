
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

        vm.uploadApplication = uploadApplication;

        function uploadApplication(){
            Application.uploadApplication(true, vm.application).then(uploadSuccess, uploadError);

            function uploadSuccess() {
                window.location = 'application/new';
            }

            function uploadError(status) {
                console.error('Upload failed: ' + status);
            }
        }
    }
})();