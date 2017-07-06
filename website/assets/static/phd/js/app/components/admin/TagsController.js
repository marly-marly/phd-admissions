
(function () {
    'use strict';

    angular
        .module('phd.admin.controllers')
        .controller('TagsController', TagsController);

    TagsController.$inject = ['$location', 'Admin', 'Authentication', 'Application', 'Toast'];

    function TagsController($location, Admin, Authentication, Application, Toast) {

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

        }, Toast.showHttpError);

        Application.getAllAcademicYears().then(function success (response) {
            var academicYears = response.data.academic_years;
            vm.currentAcademicYear = Application.findDefaultAcademicYear(academicYears);
        }, Toast.showHttpError);

        vm.newTag = undefined;
        vm.addNewTag = function(){
            Admin.addNewTag(vm.newTag).then(function success(response){
                vm.newTag = undefined;
                var newTag = response.data.tag;
                vm.tags.push(newTag);

                Toast.showSuccess("Successfully added new tag '" + newTag.name + "'")
            }, Toast.showHttpError)
        };

        vm.removeTag = function(tag){
            Admin.deleteTag(tag.id).then(function success(){
                tag.editable = false;
                // Update tags
                vm.tags = vm.tags.filter(function(obj ) {
                    return obj.id !== tag.id;
                });
                Toast.showSuccess("Removed.");
            }, Toast.showHttpError)
        };

        vm.updateTag = function(tag){
            Admin.updateTag(tag).then(function success(){
                tag.editable = false;
                Toast.showSuccess("Saved!");
            }, Toast.showHttpError)
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
    }
})();