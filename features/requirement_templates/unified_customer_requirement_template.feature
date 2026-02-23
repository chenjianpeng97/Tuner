Feature: Unified customer requirement entity template rule
    Requirements and matters are represented as one customer requirement entity.

    Background:
        Given a project "P1" has instantiated template "project_tracking_view"

    Rule: A single customer requirement entity distinguishes type by labels
        Scenario: Mark a record as R&D requirement
            Given customer requirement "CR-1" exists
            When an actor adds label "研发需求" to "CR-1"
            Then "CR-1" is treated as a requirement eligible for decomposition

        Scenario: Mark a record as matter-only item
            Given customer requirement "CR-2" exists
            When an actor adds label "事项" to "CR-2"
            Then "CR-2" is treated as a tracked matter item

    Rule: Only R&D requirements can drill down into product requirement decomposition
        Scenario: Allow drill-down for R&D requirement
            Given customer requirement "CR-1" is labeled "研发需求"
            When an actor requests drill-down for "CR-1"
            Then the request is accepted and opens product requirement context

        Scenario: Reject drill-down for matter-only item
            Given customer requirement "CR-2" is labeled "事项"
            When an actor requests drill-down for "CR-2"
            Then the request is rejected for unsupported decomposition type
