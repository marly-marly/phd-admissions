
(function () {
    'use strict';

    angular
        .module('phd.email.controllers')
        .controller('EmailTemplateController', EmailTemplateController);

    EmailTemplateController.$inject = ['$location', 'Authentication', 'Toast', '$scope', 'taOptions', 'taRegisterTool', 'Application', 'Email'];

    function EmailTemplateController($location, Authentication, Toast, $scope, taOptions, taRegisterTool, Application, Email) {

        // If the user is not authenticated, they should not be here.
        if (!Authentication.isAuthenticated()) {
            $location.url('/login');
            return;
        }

        var vm = this;

        Email.getEmailTemplate().then(function success(response){
            vm.emailContent = response.data.value;
        }, Toast.showHttpError);

        vm.updateEmailContent = function(){
            Email.updateEmailTemplate(vm.emailContent).then(function success(){

                // Set the form to be shown as unedited
                $scope.emailTemplateForm.$setPristine();
                Toast.showSuccess("Saved!")
            }, Toast.showHttpError)
        };

        vm.emailContentChanged = function(){
            return !!$scope.emailTemplateForm.$dirty;
        };

        var toolbarInserts = ["registry_ref", "surname", "forename", "research_subject", "administrator_comment",
                 "phd_admission_tutor_comment", "supervisor_first_name", "supervisor_last_name", "application_link"];
        // Check if we already added our custom controls
        if (taOptions.toolbar.length <= 4){

            taOptions.toolbar.push([]);

            for (var i=0; i<toolbarInserts.length; i++){
                (function(){
                    var fieldName = toolbarInserts[i];
                    var prettyFieldName = Application.snakeCaseToPretty(fieldName);

                    taRegisterTool(fieldName, {
                        buttontext: prettyFieldName,
                        iconclass: undefined,
                        tooltiptext: "Insert " + prettyFieldName,
                        action: function(){
                            this.$editor().wrapSelection('insertHTML', '{{' + fieldName + '}}');
                        }
                    });
                })();
            }

            // Add the button to the default toolbar definition
            taOptions.toolbar[taOptions.toolbar.length-1].push('colourRed');
        }

        vm.taToolbar = [['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'pre', 'quote'],
                        ['bold', 'italics', 'underline', 'strikeThrough', 'ul', 'ol', 'redo', 'undo', 'clear'],
                        ['justifyLeft', 'justifyCenter', 'justifyRight', 'indent', 'outdent'],
                        ['html','insertLink', 'wordcount', 'charcount'],
                        toolbarInserts];

        vm.getEmailPreview = function(){
            Email.getEmailPreview(vm.emailContent, undefined).then(function success(response){
                vm.emailPreview = response.data;
            }, Toast.showHttpError)
        };
    }
})();