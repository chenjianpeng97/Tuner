Feature: Dynamic spreadsheet platform capability
    The platform provides reusable online spreadsheet primitives.
    It is independent from requirement-management business semantics.

    Rule: External APIs are centered on spreadsheet atomic operations
        Scenario: Use table and view primitives without business coupling
            Given a project "P1" exists
            And no requirement template is instantiated for "P1"
            When an actor creates a spreadsheet table for "P1"
            And the actor creates a grid view on that table
            Then the table and view are available as generic spreadsheet resources
            And no requirement-specific fixed schema is required

    Rule: Spreadsheet instances belong to project context
        Scenario: Create a spreadsheet instance from a template key in a project
            Given a project "P1" exists
            And a spreadsheet template key "generic_matrix" is available
            When an actor creates a spreadsheet instance in project "P1" with template key "generic_matrix"
            Then the spreadsheet instance is created under project "P1"
            And the instance can be queried by project scope
