Feature: Status and progress template rule
    Customer requirements maintain status, progress, and audit records.

    Background:
        Given a project "P1" has instantiated template "project_tracking_view"
        And customer requirement "CR-1" exists in project "P1"

    Rule: Status labels are project-configurable with extensible defaults
        Scenario: Use default status labels
            Given project "P1" status labels are not customized
            When an actor queries available status labels
            Then labels include "待确认", "内部已确认", "待外部确认"

        Scenario: Extend status labels by project setting
            Given project "P1" adds status label "开发中"
            When an actor queries available status labels
            Then label "开发中" is included

    Rule: Status transition has no fixed path constraint
        Scenario: Switch status freely between labels
            Given customer requirement "CR-1" current status is "待确认"
            When an actor updates status to "待外部确认"
            Then status update succeeds
            When the actor updates status to "内部已确认"
            Then status update succeeds

    Rule: Progress is shown by planned start and planned end
        Scenario: Show progress in list or board representation
            Given customer requirement "CR-1" has planned start "2026-03-01"
            And customer requirement "CR-1" has planned end "2026-03-10"
            When an actor queries progress overview
            Then progress data is available for list or board presentation

    Rule: Every status update must be auditable
        Scenario: Persist updater and update time for each status change
            Given actor "u-admin" updates status of "CR-1"
            When the status change is persisted
            Then the record stores last_updated_at
            And the record stores last_updated_by
            And a status-change log entry stores operator "u-admin"
