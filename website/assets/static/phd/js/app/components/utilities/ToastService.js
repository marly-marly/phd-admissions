
(function () {
    'use strict';

    angular
        .module('phd.utilities.services')
        .factory('Toast', Toast);

    Toast.$inject = [];

    function Toast() {

        return {
            showHttpError: showHttpError,
            showSuccess: showSuccess,
            showSuccessAsHtml: showSuccessAsHtml,
            showInfo: showInfo
        };

        function showHttpError(data){
            toastr.error(data.data.error, data.statusText + " " + data.status)
        }

        function showSuccess(message){
            toastr.success(message)
        }

        function showSuccessAsHtml(message){
            toastr.options.escapeHtml = false;
            toastr.success(message)
        }

        function showInfo(message){
            toastr.info(message)
        }
    }
})();