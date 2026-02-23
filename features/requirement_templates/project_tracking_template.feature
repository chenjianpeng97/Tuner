Feature: Project tracking view template
    The project tracking template carries customer requirements and related design/test information.

    Background:
        Given a project "P1" has instantiated template "project_tracking_view"
        And table "project_tracking" exists in project "P1"

    Rule: The template must include baseline columns and extensible schedule columns
        Scenario: Validate default and extensible columns
            When an actor queries column definitions of table "project_tracking"
            Then the table contains columns "需求", "设计", "测试"
            And the table supports schedule columns "预计开始", "预计结束"

    Rule: Requirement cells support summary and detail display
        Scenario: View requirement summary and detail
            Given customer requirement "CR-1" content is recorded in column "需求"
            When an actor queries summary projection for "CR-1"
            Then the response includes summary text
            When the actor queries detail projection for "CR-1"
            Then the response includes full requirement content

    Rule: Drill-down to product requirements must carry customer requirement context
        Scenario: Open product requirement list by requirement context
            Given customer requirement "CR-1" exists in table "project_tracking"
            When an actor drills down from customer requirement "CR-1"
            Then the target product requirement query is scoped by customer_requirement_id "CR-1"

    Rule: Return-flow statistics show design and test counts for current customer requirement scope
        Scenario: Show associated design and test totals after return from drill-down
            Given customer requirement "CR-1" is associated with product requirements
            And assets are attached across "CR-1" and its associated product requirements
            When an actor queries tracking statistics for customer requirement "CR-1"
            Then the design count equals all design assets under "CR-1" plus associated product requirements
            And the test count equals all test assets under "CR-1" plus associated product requirements

    Rule: Tag-based statistics support multi-tag assets
        Scenario: Aggregate by asset tags in tracking view
            Given assets in project "P1" contain tags "DDL", "自动化测试", "冒烟设计"
            And one asset has multiple tags
            When an actor queries tracking statistics grouped by tags
            Then the response includes per-tag counts in project context

    Rule: Statistics include uploaded assets not yet associated with requirements
        Scenario: Show unassociated asset count in project tracking view
            Given project "P1" contains uploaded assets without requirement association
            When an actor queries project tracking summary cards
            Then the response includes count "unassociated_assets"
