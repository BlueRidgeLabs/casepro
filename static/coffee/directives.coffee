#============================================================================
# Directives
#============================================================================
directives = angular.module('cases.directives', [])


#----------------------------------------------------------------------------
# A contact reference which displays a popover when hovered over
#----------------------------------------------------------------------------
directives.directive('cpContact', () ->
  return {
    restrict: 'E',
    scope: {contact: '=', fields: '='},
    templateUrl: '/partials/directive_contact.html',
    controller: ['$scope', 'ContactService', ($scope, ContactService) ->
      $scope.fetched = false
      $scope.popoverIsOpen = false
      $scope.popoverTemplateUrl = '/partials/popover_contact.html'

      $scope.openPopover = () ->
        $scope.popoverIsOpen = true

        if not $scope.fetched
          ContactService.fetch($scope.contact.id).then((contact) ->
            $scope.contact = contact
            $scope.fetched = true
          )

      $scope.closePopover = () ->
        $scope.popoverIsOpen = false
    ]
  }
)

#----------------------------------------------------------------------------
# A contact field value
#----------------------------------------------------------------------------
directives.directive('cpFieldvalue', () ->
  return {
    restrict: 'E',
    scope: {contact: '=', field: '='},
    template: '[[ value ]]',
    controller: ['$scope', '$filter', ($scope, $filter) ->
      raw = $scope.contact.fields[$scope.field.key]

      if raw
        if $scope.field.value_type == 'N'
          $scope.value = $filter('number')(raw)
        else if $scope.field.value_type == 'D'
          $scope.value = $filter('date')(raw, 'mediumDate')
        else
          $scope.value = raw
      else
        $scope.value = '--'
    ]
  }
)

directives.directive('cpAlert', -> {
  restrict: 'E',
  transclude: true,
  scope: {type: '@'},
  templateUrl: '/sitestatic/templates/alert.html'
})


directives.directive('cpCaseNotifications', -> {
  templateUrl: '/sitestatic/templates/case-notifications.html',
  scope: {notifications: '='}
})

#=====================================================================
# Pod directive
#=====================================================================
directives.directive('cpPod', -> {
  templateUrl: -> '/sitestatic/templates/pod.html'
})
