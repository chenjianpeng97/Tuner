# Examples

## Example 1: Single feature

Input requirement:
"As a shopper, I want to save items for later so I can buy them after comparing prices. Only logged-in users can save items."

Output:
Suggested save path: `features/save_for_later.feature`

```gherkin
Feature: Save for later
  As a shopper
  I want to save items for later
  So that I can buy them after comparing prices

  Background:
    Given a product "Noise Cancelling Headphones" exists

  Scenario: Save an item for later
    Given I am an authenticated shopper
    When I save "Noise Cancelling Headphones" for later
    Then the item is listed in my saved items

  Rule: Only authenticated shoppers can save items
    Example: Reject saving when not logged in
      Given I am not authenticated
      When I save "Noise Cancelling Headphones" for later
      Then the save request is rejected
```

Dry run:
`behave features/save_for_later.feature --dry-run`

## Example 2: Feature with sub-requirements

Input requirement:
"Add project management. Projects have members. Only project members can assign tasks. Task assignment should warn when a member already has 5 active tasks."

Output:
Suggested save path: `features/project_management/assignment_rules.feature`

```gherkin
Feature: Task assignment rules
  As a project manager
  I want task assignment to respect membership and workload
  So that assignment is valid and risks are visible

  Background:
    Given a project "Apollo" exists
    And a member "Alex" belongs to "Apollo"

  Rule: Only members can be assigned tasks
    Example: Reject assignment for non-members
      Given a user "Stranger" is not a member of "Apollo"
      When I assign task "Implement login" to "Stranger"
      Then the assignment is rejected

  Rule: Warn on high workload
    Example: Allow assignment but warn when workload is high
      Given "Alex" has 5 active tasks
      When I assign task "Implement login" to "Alex"
      Then the assignment succeeds
      And a warning "High workload" is emitted
```

Dry run:
`behave features/project_management/assignment_rules.feature --dry-run`
