Feature: Spreadsheet concurrency and idempotent writes
    Write operations enforce version checks and idempotency protections.

    Background:
        Given a project "P1" exists
        And a spreadsheet table "T1" exists in project "P1"

    Rule: Write operations require expected_version validation
        Scenario: Reject stale write with version conflict
            Given table "T1" current version is 5
            When an actor updates row "R1" with expected_version 4
            Then the write is rejected with a version conflict
            And table "T1" data remains unchanged

        Scenario: Accept write with matched expected_version
            Given table "T1" current version is 5
            When an actor updates row "R1" with expected_version 5
            Then the write succeeds
            And table "T1" version becomes 6

    Rule: Batch and upload operations support idempotency keys
        Scenario: Retry same batch request without duplicate effects
            Given no request has used idempotency key "idem-123"
            When an actor submits a batch write with idempotency key "idem-123"
            And the actor retries the same batch write with idempotency key "idem-123"
            Then the second request reuses the first result
            And no duplicate row or duplicate mutation is produced
