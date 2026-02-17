Feature: User management authorization
  Authorization rules for user creation and activation.

  Rule: Actors can only create users with lower roles
    Scenario: Create a lower-role user
      Given an actor with role "manager"
      And the role hierarchy allows "manager" to create "staff"
      When the actor creates a user with role "staff"
      Then the user is created

    Scenario: Reject creating a same or higher role user
      Given an actor with role "manager"
      And the role hierarchy does not allow "manager" to create "manager"
      When the actor creates a user with role "manager"
      Then the request is rejected for insufficient permissions

  Rule: Only actors who control the user role can activate or deactivate users
    Scenario: Activate a lower-role user
      Given an actor with role "admin"
      And the role hierarchy allows "admin" to control "manager"
      And a deactivated user with role "manager"
      When the actor activates the user
      Then the user becomes active

    Scenario: Reject activation without control permission
      Given an actor with role "manager"
      And the role hierarchy does not allow "manager" to control "admin"
      And a deactivated user with role "admin"
      When the actor activates the user
      Then the request is rejected for insufficient permissions

    Scenario: Deactivate a lower-role user
      Given an actor with role "admin"
      And the role hierarchy allows "admin" to control "manager"
      And an active user with role "manager"
      When the actor deactivates the user
      Then the user becomes deactivated
