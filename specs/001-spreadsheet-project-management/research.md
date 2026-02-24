# Phase 0 Research — Spreadsheet-based Project Management

## Decision 1: Deliver in two gated phases (standard spreadsheet first)
- Decision: Implement phase-1 generic spreadsheet demo (near real-time CRUD + filtering + full acceptance pass) before any requirement-management presets.
- Rationale: This matches spec delivery boundary and constitution principle V (incremental delivery). It reduces business-coupled rework risk and creates reusable platform capability.
- Alternatives considered:
  - Build business presets first: rejected because it couples business rules to unverified core table behavior.
  - Build both phases in one batch: rejected because failures become harder to isolate and rollback.

## Decision 2: Keep spreadsheet capability business-agnostic at core layer
- Decision: Core table/domain behavior remains generic; project-management semantics are implemented as template presets and orchestration rules in phase 2.
- Rationale: Preserves clean architecture boundaries and ensures core spreadsheet module can support other demos/use-cases.
- Alternatives considered:
  - Add requirement-specific fields directly into core spreadsheet entities: rejected due to loss of reusability and boundary leakage.

## Decision 3: Define near real-time behavior via deterministic write/read consistency
- Decision: Treat near real-time as successful write result immediately observable on subsequent reads and stage tests, with deterministic result ordering under concurrent updates.
- Rationale: This is testable in current architecture without introducing transport-specific assumptions in spec artifacts.
- Alternatives considered:
  - Mandate websocket push as hard requirement: rejected at planning stage because transport can vary while behavior contract remains stable.
  - Ignore concurrency semantics: rejected because edge cases already require deterministic behavior.

## Decision 4: Filter model stays generic and composable
- Decision: Filter behavior is defined on generic table records with apply/clear semantics and no business-field hard dependency.
- Rationale: Supports phase-1 demo validation and reuse by phase-2 preset tables.
- Alternatives considered:
  - Hardcode requirement-specific filter schema in phase 1: rejected because it violates phase separation.

## Decision 5: Contract-first updates drive downstream artifacts
- Decision: Any API-affecting change updates OpenAPI source and regenerates `docs/openapi.json`, then frontend types/mocks are synchronized.
- Rationale: Enforces constitution principle II and avoids backend/frontend contract drift.
- Alternatives considered:
  - Update only backend route code and postpone contract export: rejected because typed frontend integration would drift.

## Decision 6: Stage-first testing sequence and merge gates
- Decision: Use failing-first stage tests in order: `behave --stage http` for orchestration, targeted `behave --stage ui` for user flow, `pytest` for backend logic; phase-2 merge gate depends on phase-1 100% acceptance pass.
- Rationale: Aligns with constitution principle III and spec SC-003.
- Alternatives considered:
  - Unit tests only: rejected because this feature requires behavior-stage contract validation.
  - UI-first only: rejected because backend contract/orchestration regressions could be missed.
