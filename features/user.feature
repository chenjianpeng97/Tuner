Feature: User management
  The system manages user creation and activation state.

  Rule: Username must be unique
    Scenario: Reject creating a user with a duplicate username
      Given an existing user with username "alice"
      When an actor creates a user with username "alice"
      Then the request is rejected with a "user already exists" error

  Rule: User activation affects login
    Scenario: Deactivated users cannot authenticate
      Given a deactivated user with username "bob"
      When the user attempts to authenticate
      Then the authentication is denied

  Rule: Users can be activated or deactivated
    Scenario: Activate a deactivated user
      Given a deactivated user with username "carol"
      When an authorized actor activates the user
      Then the user becomes active

    Scenario: Deactivate an active user
      Given an active user with username "dave"
      When an authorized actor deactivates the user
      Then the user becomes deactivated
