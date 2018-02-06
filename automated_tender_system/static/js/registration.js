/**
 * Created by mandeev on 19/3/17.
 */

var app5 = angular.module('app5', []);

app5.controller('userCtrl',['$scope', function($scope) {

  $scope.user= [{
    cName: "",
    l_ID: "",
    pwd: "",
    cpwd: "",
    cAddr: ""
  }];

  $scope.saveUser = function(userInfo) {
    if($scope.form_reg.$valid) {
      $scope.user.push({
        cName: userInfo.cName, l_ID: userInfo.l_ID, pwd: userInfo.pwd, cpwd: userInfo.cpwd, cAddr: userInfo.cAddr
      });
      console.log('User Saved');
    } else {
      console.log('Error : Couldn\'t Save User');
    }
 }

     $scope.numOnlyRegex = /^\d+$/;
    $scope.alpOnlyRegex = /^[a-zA-Z\s]*$/;

}]);            
