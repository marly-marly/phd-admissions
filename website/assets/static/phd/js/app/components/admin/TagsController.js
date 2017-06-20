
(function () {
    'use strict';

    angular
        .module('phd.admin.controllers')
        .controller('TagsController', TagsController);

    TagsController.$inject = ['$location', 'Admin', 'Authentication', '$filter'];

    function TagsController($location, Admin, Authentication, $filter) {

        // If the user is not authenticated, they should not be here.
        if (!Authentication.isAuthenticated()) {
            $location.url('/login');
            return;
        }

        var vm = this;
        vm.tags = [];
        Admin.getAllTags().then(function success(response){
            vm.tags = response.data.tags;
        }, displayErrorMessage);

        vm.newTag = undefined;
        vm.addNewTag = function(){
            Admin.addNewTag(vm.newTag).then(function success(response){
                vm.newTag = undefined;
                var newTag = response.data.tag;
                vm.tags.push(newTag);

                toastr.success("Successfully added new tag '" + newTag.name + "'")
            }, displayErrorMessage)
        };

        vm.removeTag = function(tag){
            Admin.deleteTag(tag.id).then(function success(){
                tag.editable = false;
                // Update tags
                vm.tags = vm.tags.filter(function(obj ) {
                    return obj.id !== tag.id;
                });
                toastr.success("Removed.");
            }, displayErrorMessage)
        };

        vm.updateTag = function(tag){
            Admin.updateTag(tag).then(function success(){
                tag.editable = false;
                toastr.success("Saved!");
            }, displayErrorMessage)
        };

        vm.editTag = function(tag){
            tag.editable = true;
        };

        vm.closeEditTag = function(tag){
            tag.editable = false;
        };

        function displayErrorMessage(data){
            toastr.error(data.data.error, data.statusText + " " + data.status)
        }
    }
})();