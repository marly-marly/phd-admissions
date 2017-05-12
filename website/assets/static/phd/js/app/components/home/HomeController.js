
(function () {
    'use strict';

    angular
        .module('phd.home.controllers')
        .controller('IndexController', IndexController);

    IndexController.$inject = ['$scope', 'Home'];

    function IndexController($scope, Home) {
        var vm = this;

        Home.getStatistics().then(function(response){
            vm.numberOfApplications = response.data["number_of_applications"];
        });

    }
})();