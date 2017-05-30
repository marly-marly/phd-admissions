
(function () {
    'use strict';

    angular
        .module('phd.admin.services')
        .factory('Admin', Admin);

    Admin.$inject = ['$http'];

    function Admin($http) {

        var Admin = {
            getAllStaffMembers: getAllStaffMembers,
            changeRoles: changeRoles
        };

        return Admin;

        function getAllStaffMembers(){
            return $http.get('/api/applications/admin/staff/');
        }

        function changeRoles(newUserRoles){
            return $http.post('/api/applications/admin/staff_roles/', {new_user_roles: newUserRoles})
        }
    }
})();