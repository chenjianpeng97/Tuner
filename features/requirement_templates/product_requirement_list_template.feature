Feature: Product requirement list template
    The product requirement template models hierarchical requirements with module ownership.

    Background:
        Given a project "P1" has instantiated template "product_requirement_list"
        And table "product_requirement_list" exists in project "P1"

    Rule: Requirement hierarchy levels are project-configurable with default and extended ranges
        Scenario: Use default hierarchy levels
            Given project "P1" hierarchy settings are not customized
            When an actor queries hierarchy columns
            Then the table contains "L1", "L2", "L3"

        Scenario: Extend hierarchy levels up to L9
            Given project "P1" configures hierarchy levels to "L1" through "L9"
            When an actor updates template instance columns by project settings
            Then the table contains hierarchy columns from "L1" to "L9"

    Rule: Module and submodule ownership is always visible in fixed left-side fields
        Scenario: Keep module fields as fixed columns
            When an actor queries column layout metadata
            Then fields "模块" and "子模块" are marked as fixed-left columns

    Rule: Drill-down context filters product requirements by customer requirement
        Scenario: Query only requirements associated with current customer requirement
            Given customer requirement context "CR-1" is active
            When an actor queries product requirements in drill-down context
            Then all returned product requirements are associated with customer_requirement_id "CR-1"

    Rule: Creating a product requirement in drill-down context auto-creates association
        Scenario: Auto-link on create within drill-down context
            Given customer requirement context "CR-1" is active
            When an actor creates product requirement "PR-100" in current context
            Then product requirement "PR-100" is created
            And association between "CR-1" and "PR-100" is created

    Rule: Customer requirements and product requirements are many-to-many and can be manually maintained
        Scenario: Manually link and unlink without deleting product requirement
            Given product requirement "PR-200" exists
            And customer requirement "CR-2" exists
            When an actor manually links "CR-2" with "PR-200"
            Then the association exists
            When the actor cancels association between "CR-2" and "PR-200"
            Then the association is removed
            And product requirement "PR-200" still exists
