Feature: Spreadsheet asset attachment and generic statistics
    Assets can be uploaded, bound, copied, and counted in project context.

    Background:
        Given a project "P1" exists
        And a spreadsheet table "T1" exists in project "P1"

    Rule: Asset upload must be scoped by project
        Scenario: Upload asset in project context
            When an actor uploads asset "设计说明-v1.md" into project "P1"
            Then the asset is stored with project_id "P1"

    Rule: Assets can be uploaded first and bound later
        Scenario: Bind an existing uploaded asset to a table cell
            Given asset "A1" already exists in project "P1"
            When an actor binds asset "A1" to table "T1" row "R1" column "需求"
            Then the binding is created for that cell

    Rule: Asset copy supports follow relationship and branch detachment
        Scenario: Create follow copy and then detach as branch
            Given parent asset "A-parent" exists in project "P1"
            When an actor copies "A-parent" to create "A-child" with follow mode enabled
            Then "A-child" is linked as a follow copy of "A-parent"
            When the actor detaches "A-child" from follow mode
            Then "A-child" becomes an independent branch asset

    Rule: Generic statistics include unbound assets
        Scenario: Count uploaded assets without table association
            Given project "P1" has uploaded assets with no table binding
            When an actor queries project-level asset statistics
            Then the response includes the count of unbound assets
