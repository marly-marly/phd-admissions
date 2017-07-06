
(function () {
    'use strict';

    angular
        .module('phd.admin.services')
        .factory('Admin', Admin);

    Admin.$inject = ['$http'];

    function Admin($http) {

        var Admin = {
            getAllStaffMembers: getAllStaffMembers,
            changeRoles: changeRoles,
            getAllAcademicYears: getAllAcademicYears,
            uploadNewAcademicYear: uploadNewAcademicYear,
            updateAcademicYear: updateAcademicYear,
            markAcademicYearDefault: markAcademicYearDefault,
            getAllTags: getAllTags,
            addNewTag: addNewTag,
            updateTag: updateTag,
            deleteTag: deleteTag,
            syncStaff: syncStaff
        };

        return Admin;

        function getAllStaffMembers(){
            return $http.get('/api/applications/admin/staff/');
        }

        function changeRoles(newUserRoles){
            return $http.post('/api/applications/admin/staff_roles/', {new_user_roles: newUserRoles})
        }

        function getAllAcademicYears(){
            return $http.get('/api/applications/admin/academic_year/');
        }

        function uploadNewAcademicYear(academic_year){
            return $http.post('/api/applications/admin/academic_year/', academic_year);
        }

        function updateAcademicYear(academic_year){
            return $http.put("/api/applications/admin/academic_year/", {id: academic_year.id, academic_year: academic_year});
        }

        function markAcademicYearDefault(academic_year){
            return $http.put("/api/applications/admin/academic_year/", {id: academic_year.id, academic_year: {default: true}});
        }

        function getAllTags(){
            return $http.get('/api/applications/admin/tags/');
        }

        function addNewTag(newTag){
            return $http.post('/api/applications/admin/tags/', newTag);
        }

        function updateTag(tag){
            return $http.put('/api/applications/admin/tags/', {id: tag.id, tag: tag});
        }

        function deleteTag(id){
            return $http.delete('/api/applications/admin/tags/', {data: {id: id}})
        }

        function syncStaff(){
            return $http.post('/api/applications/users/sync_staff/');
        }
    }
})();