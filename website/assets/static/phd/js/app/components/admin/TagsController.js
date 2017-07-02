
(function () {
    'use strict';

    angular
        .module('phd.admin.controllers')
        .controller('TagsController', TagsController);

    TagsController.$inject = ['$location', 'Admin', 'Authentication', 'Application'];

    function TagsController($location, Admin, Authentication, Application) {

        // If the user is not authenticated, they should not be here.
        if (!Authentication.isAuthenticated()) {
            $location.url('/login');
            return;
        }

        var vm = this;

        vm.tags = [];
        Application.getAllTagsWithCounts().then(function success(response){
            var tagsMap = response.data;
            var item;
            for (var tag in tagsMap) {
                item = {};
                item.name = tag;
                if (tagsMap.hasOwnProperty(tag)){
                    item.id = tagsMap[tag].id;
                    item.count = tagsMap[tag].count;
                }

                vm.tags.push(item);
            }

        }, displayErrorMessage);

        Application.getAllAcademicYears().then(function success (response) {
            var academicYears = response.data.academic_years;
            vm.currentAcademicYear = Application.findDefaultAcademicYear(academicYears);
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

        var tempTagMap = {};
        vm.editTag = function(tag){
            tempTagMap[tag.id] = angular.copy(tag);
            tag.editable = true;
        };

        vm.closeEditTag = function(tag){
            tag.editable = false;
            angular.copy(tempTagMap[tag.id], tag);
        };

        function displayErrorMessage(data){
            toastr.error(data.data.error, data.statusText + " " + data.status)
        }
    }
})();