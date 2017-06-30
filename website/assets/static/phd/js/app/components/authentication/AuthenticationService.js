
(function () {
    'use strict';

    angular
        .module('phd.authentication.services')
        .factory('Authentication', Authentication);

    Authentication.$inject = ['$cookies', '$http'];

    function Authentication($cookies, $http) {

        var Authentication = {
            getAuthenticatedAccount: getAuthenticatedAccount,
            isAuthenticated: isAuthenticated,
            login: login,
            logout: logout,
            setAuthenticatedAccount: setAuthenticatedAccount,
            unauthenticate: unauthenticate
        };

        return Authentication;

        function login(username, password) {
            return $http.post('/api/auth/login/', {
                username: username,
                password: password
            }).then(loginSuccessFn, loginErrorFn);

            function loginSuccessFn(data) {
                var statusCode = data.status;
                // Check http status return
                if (statusCode.toString().charAt(0) != "2") {
                    alert('Please input a correct password');
                } else {
                    var response = data.data;
                    Authentication.setAuthenticatedAccount(response.token, response.username, response.user_role);
                    window.location = 'home';
                }
            }

            function loginErrorFn(data) {
                toastr.error(data.data.error, data.statusText + " " + data.status)
            }
        }

        function logout() {
            Authentication.unauthenticate();
        }

        function getAuthenticatedAccount() {
            if (!$cookies.get('username')) {
                return null;
            }

            return {username: $cookies.get('username'),
                    userRole: $cookies.get('user_role')};
        }

        function isAuthenticated() {
            return !!$cookies.get('token');
        }

        function setAuthenticatedAccount(token, username, user_role) {

            // Set the expiration to 6 months
            var now = new Date();
            var expiry = new Date(now.getFullYear(), now.getMonth()+6, now.getDate());

            // Store the token
            $cookies.put('token', token,{
              expires: expiry
            });

            // Set the token as a header
            $http.defaults.headers.common['Authorization'] = 'JWT ' + token;

            // Store the username
            $cookies.put('username', username,{
              expires: expiry
            });

            // Store the user-role
            $cookies.put('user_role', user_role,{
              expires: expiry
            });
        }

        function unauthenticate() {
            delete $cookies.remove('token');
            delete $cookies.remove('username');

            window.location = 'home';
        }
    }
})();