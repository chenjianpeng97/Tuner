Feature: Requirement management template capability
    Requirement management is delivered as business templates on top of spreadsheet primitives.

    Rule: Project tracking and product requirement list are template-level constructs
        Scenario: Discover requirement templates for instantiation
            Given a project "P1" exists
            When an actor queries available requirement templates
            Then the response includes template "project_tracking_view"
            And the response includes template "product_requirement_list"
            And both templates are provided as business templates rather than platform fixed models

    Rule: Template instances are created from platform capabilities with project parameters
        Scenario: Instantiate product requirement template with hierarchy settings
            Given project "P1" sets hierarchy levels as "L1", "L2", "L3", "L4"
            When an actor instantiates template "product_requirement_list" for project "P1"
            Then a spreadsheet instance is created for project "P1"
            And the instance contains hierarchy columns aligned with the project settings
