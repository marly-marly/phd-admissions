
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
            deleteAcademicYear: deleteAcademicYear,
            markAcademicYearDefault: markAcademicYearDefault
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

        function deleteAcademicYear(id){
            return $http.delete('/api/applications/admin/academic_year/', {params: {id: id}})
        }
    }
})();