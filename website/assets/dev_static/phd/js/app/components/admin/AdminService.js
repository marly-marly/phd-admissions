
(function () {
    'use strict';

    angular
        .module('phd.admin.services')
        .factory('Admin', Admin);

    Admin.$inject = ['$http'];

    function Admin($http) {

        return {
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

        function getAllStaffMembers(){
            return $http.get('/api/auth/all_staff/');
        }

        function changeRoles(newUserRoles){
            return $http.post('/api/auth/staff_roles/', {new_user_roles: newUserRoles})
        }

        function getAllAcademicYears(){
            return $http.get('/api/phd/admin/academic_year/');
        }

        function uploadNewAcademicYear(academic_year){
            return $http.post('/api/phd/admin/academic_year/', academic_year);
        }

        function updateAcademicYear(academic_year){
            return $http.put("/api/phd/admin/academic_year/", {id: academic_year.id, academic_year: academic_year});
        }

        function markAcademicYearDefault(academic_year){
            return $http.put("/api/phd/admin/academic_year/", {id: academic_year.id, academic_year: {default: true}});
        }

        function getAllTags(){
            return $http.get('/api/phd/admin/tags/');
        }

        function addNewTag(newTag){
            return $http.post('/api/phd/admin/tags/', newTag);
        }

        function updateTag(tag){
            return $http.put('/api/phd/admin/tags/', {id: tag.id, tag: tag});
        }

        function deleteTag(id){
            return $http.delete('/api/phd/admin/tags/', {data: {id: id}})
        }

        function syncStaff(){
            return $http.post('/api/auth/sync_staff/');
        }
    }
})();