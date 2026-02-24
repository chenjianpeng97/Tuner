Feature: Demo generic spreadsheet components smoke
    Developers can quickly verify baseline spreadsheet capabilities with a plain online table demo flow.

    @smoke @http
    Scenario: Create a plain online table without template in demo module
        Given demo project "P-DEMO" exists
        When a developer creates plain table "Demo Board" in demo project "P-DEMO" with columns "Name", "Owner", "Status"
        Then the demo plain table is created successfully
        And the demo request dispatches spreadsheet command "create_plain_table"
