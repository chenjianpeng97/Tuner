# Tasks: Spreadsheet-based Project Management

**Input**: Design documents from `/specs/001-spreadsheet-project-management/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: This feature explicitly requires complete testing and stage-gated delivery. Test tasks are included and must be executed failing-first before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare baseline scaffolding and traceability for phased delivery

- [ ] T001 Create traceability map from spec stories/FRs to test artifacts in specs/001-spreadsheet-project-management/traceability.md
- [ ] T002 Define initial task execution runbook baseline for this feature in specs/001-spreadsheet-project-management/quickstart.md
- [ ] T003 [P] Add feature-level backend unit-test package placeholder in backend/tests/app/unit/application/spreadsheet_project_management/__init__.py
- [ ] T004 [P] Add feature-level frontend service placeholder in frontend/src/features/spreadsheet-project-management/api/index.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared contracts and architecture plumbing that MUST be ready before user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Finalize planning contract endpoints and schemas in specs/001-spreadsheet-project-management/contracts/spreadsheet-project-management.openapi.yaml
- [ ] T006 Define OpenAPI regeneration procedure and touched outputs in specs/001-spreadsheet-project-management/openapi-regeneration.md
- [ ] T007 [P] Add backend route registration skeleton for spreadsheet project management in backend/src/app/presentation/http/controllers/spreadsheet_project_management_router.py
- [ ] T008 [P] Add application-layer port interfaces for spreadsheet/table operations in backend/src/app/application/common/ports/spreadsheet_gateway.py
- [ ] T009 [P] Add application-layer port interfaces for requirement preset/statistics operations in backend/src/app/application/common/ports/requirement_template_gateway.py
- [ ] T010 Add DI wiring placeholders for new gateways/controllers in backend/src/app/setup/ioc/provider_registry.py and backend/src/app/setup/ioc/application.py
- [ ] T011 Add baseline HTTP-stage smoke scenario for this feature slice in features/demo/generic_components_smoke.feature

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Deliver standard online spreadsheet demo (Priority: P1) 🎯 MVP

**Goal**: Ship generic near-real-time spreadsheet CRUD + filtering demo independent of requirement business semantics

**Independent Test**: Run spreadsheet platform HTTP stage + backend tests and verify CRUD/filter scenarios pass without requirement-template dependencies

### Tests for User Story 1 (failing-first required) ⚠️

- [ ] T012 [P] [US1] Add HTTP-stage scenarios for demo CRUD and filter behavior in features/spreadsheet_platform/table_instance_and_structure.feature
- [ ] T013 [P] [US1] Add HTTP-stage scenarios for idempotent/concurrent write visibility in features/spreadsheet_platform/concurrency_and_idempotency.feature
- [ ] T014 [P] [US1] Add backend integration tests for spreadsheet CRUD use cases in backend/tests/app/integration/test_spreadsheet_crud.py
- [ ] T015 [P] [US1] Add backend integration tests for generic filtering behavior in backend/tests/app/integration/test_spreadsheet_filtering.py

### Implementation for User Story 1

- [ ] T016 [P] [US1] Implement spreadsheet instance/table entities and invariants in backend/src/app/domain/entities/spreadsheet.py
- [ ] T017 [P] [US1] Implement row/cell value entities and revision rules in backend/src/app/domain/entities/spreadsheet_cell.py
- [ ] T018 [P] [US1] Implement filter value objects and predicates in backend/src/app/domain/value_objects/spreadsheet_filter.py
- [ ] T019 [US1] Implement spreadsheet write commands (create/update/delete) in backend/src/app/application/commands/manage_spreadsheet.py
- [ ] T020 [US1] Implement spreadsheet read queries (list/filter) in backend/src/app/application/queries/filter_rows.py
- [ ] T021 [US1] Implement infrastructure persistence adapter for spreadsheet data in backend/src/app/infrastructure/persistence_sqla/adapters/spreadsheet_gateway.py
- [ ] T022 [US1] Implement HTTP controllers for spreadsheet CRUD/filter endpoints in backend/src/app/presentation/http/controllers/spreadsheet_controller.py
- [ ] T023 [US1] Add request/response schemas and validation for spreadsheet endpoints in backend/src/app/presentation/http/schemas/spreadsheet_schema.py
- [ ] T024 [US1] Update OpenAPI export to include spreadsheet demo endpoints in docs/openapi.json
- [ ] T025 [US1] Add frontend API client wrappers for generic spreadsheet demo endpoints in frontend/src/features/spreadsheet-project-management/api/spreadsheetClient.ts

**Checkpoint**: User Story 1 is independently functional, testable, and demo-ready

---

## Phase 4: User Story 2 - Apply project-management preset templates (Priority: P2)

**Goal**: Add project-management preset tables and drill-down workflow on top of US1 standard capability

**Independent Test**: Instantiate preset table, create requirement records, drill down to product requirements, and verify relation auto-maintenance

### Tests for User Story 2 (failing-first required) ⚠️

- [ ] T026 [P] [US2] Add HTTP-stage scenarios for preset instantiation in features/requirement_templates/product_requirement_list_template.feature
- [ ] T027 [P] [US2] Add HTTP-stage scenarios for decomposable drill-down behavior in features/requirement_templates/unified_customer_requirement_template.feature
- [ ] T028 [P] [US2] Add backend integration tests for requirement relation auto-linking in backend/tests/app/integration/test_requirement_drilldown_linking.py
- [ ] T051 [P] [US2] Add HTTP/integration tests for product requirement creation in scoped context in backend/tests/app/integration/test_create_product_requirement.py

### Implementation for User Story 2

- [ ] T029 [P] [US2] Implement customer/product requirement entities and decomposition rules in backend/src/app/domain/entities/requirement.py
- [ ] T030 [US2] Implement preset instantiation command using standard spreadsheet capability in backend/src/app/application/commands/instantiate_requirement_presets.py
- [ ] T031 [US2] Implement drill-down query and decomposition eligibility checks in backend/src/app/application/queries/drilldown_requirement.py
- [ ] T052 [US2] Implement product requirement creation command in backend/src/app/application/commands/create_product_requirement.py
- [ ] T032 [US2] Implement infrastructure adapter for requirement relation persistence in backend/src/app/infrastructure/persistence_sqla/adapters/requirement_template_gateway.py
- [ ] T033 [US2] Implement HTTP controllers for preset instantiate and drill-down endpoints in backend/src/app/presentation/http/controllers/requirement_template_controller.py
- [ ] T034 [US2] Add schemas for preset and drill-down request/response contracts in backend/src/app/presentation/http/schemas/requirement_template_schema.py
- [ ] T053 [US2] Add dedicated HTTP handler + schema mapping for create-product-requirement endpoint in backend/src/app/presentation/http/controllers/requirement_template_controller.py and backend/src/app/presentation/http/schemas/requirement_template_schema.py
- [ ] T035 [US2] Add frontend API wrappers for preset and drill-down flows in frontend/src/features/spreadsheet-project-management/api/requirementPresetClient.ts
- [ ] T036 [US2] Regenerate OpenAPI and synchronize typed artifacts for preset/drill-down contracts in docs/openapi.json

**Checkpoint**: User Stories 1 and 2 both work independently; US2 strictly reuses US1 core semantics

---

## Phase 5: User Story 3 - View requirement asset and progress outcomes (Priority: P3)

**Goal**: Provide requirement/project-level statistics and progress outcomes with deduplication and unlinked-asset support

**Independent Test**: Query requirement and project statistics and verify counts/branch rules match feature scenarios

### Tests for User Story 3 (failing-first required) ⚠️

- [ ] T037 [P] [US3] Add HTTP-stage scenarios for asset counting and dedup rules in features/requirement_templates/requirement_asset_management_template.feature
- [ ] T038 [P] [US3] Add HTTP-stage scenarios for status/progress outcomes in features/requirement_templates/status_and_progress_template.feature
- [ ] T039 [P] [US3] Add backend integration tests for statistics aggregation rules in backend/tests/app/integration/test_requirement_statistics.py

### Implementation for User Story 3

- [ ] T040 [P] [US3] Implement requirement asset and statistics domain objects in backend/src/app/domain/entities/requirement_asset.py
- [ ] T041 [US3] Implement requirement/project statistics query service in backend/src/app/application/queries/query_requirement_statistics.py
- [ ] T042 [US3] Implement infrastructure aggregation queries for requirement statistics in backend/src/app/infrastructure/persistence_sqla/adapters/requirement_statistics_gateway.py
- [ ] T054 [US3] Implement configurable status/progress label management command/query and persistence mapping in backend/src/app/application/commands/manage_status_labels.py, backend/src/app/application/queries/list_status_labels.py, and backend/src/app/infrastructure/persistence_sqla/adapters/requirement_statistics_gateway.py
- [ ] T043 [US3] Implement HTTP statistics endpoint and response mapping in backend/src/app/presentation/http/controllers/requirement_statistics_controller.py
- [ ] T044 [US3] Add statistics request/response schemas in backend/src/app/presentation/http/schemas/requirement_statistics_schema.py
- [ ] T045 [US3] Add frontend API wrapper for statistics endpoint in frontend/src/features/spreadsheet-project-management/api/requirementStatisticsClient.ts
- [ ] T046 [US3] Regenerate OpenAPI and synchronize typed artifacts for statistics endpoint in docs/openapi.json

**Checkpoint**: All user stories are independently functional and testable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cross-story hardening

- [ ] T047 [P] Finalize feature documentation delta and usage notes in specs/001-spreadsheet-project-management/quickstart.md
- [ ] T048 Execute full staged validation commands and capture results in specs/001-spreadsheet-project-management/validation-report.md
- [ ] T049 [P] Clean up duplicate paths/schemas and align contract docs in specs/001-spreadsheet-project-management/contracts/spreadsheet-project-management.openapi.yaml
- [ ] T050 Re-run constitution compliance checklist before merge in specs/001-spreadsheet-project-management/checklists/requirements.md
- [ ] T055 Capture phase-1 mandatory acceptance suite pass artifact (100% gate) in specs/001-spreadsheet-project-management/validation-report.md
- [ ] T056 Capture phase-1 write-visibility latency p95 metric evidence in specs/001-spreadsheet-project-management/validation-report.md
- [ ] T057 Capture phase-1 first-save success-rate (>=95%) metric evidence in specs/001-spreadsheet-project-management/validation-report.md
- [ ] T058 Capture pilot evaluator confirmation evidence for SC-005 in specs/001-spreadsheet-project-management/validation-report.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: Depend on Foundational completion
  - US1 (P1) first for MVP and as dependency baseline
  - US2 (P2) depends on US1 core capability
  - US3 (P3) depends on US2 requirement relations and US1 data foundations
- **Polish (Phase 6)**: Depends on all selected user stories complete

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2; no dependency on other user stories
- **US2 (P2)**: Starts after US1 checkpoint (reuses standard spreadsheet capability)
- **US3 (P3)**: Starts after US2 checkpoint (consumes requirement relation context)

### Within Each User Story

- Test tasks MUST be written and run failing-first before implementation tasks
- Domain/model tasks before application interactors
- Application interactors before presentation controllers
- Presentation contracts before OpenAPI regeneration and frontend API wrappers

### Parallel Opportunities

- Setup tasks marked `[P]` can run in parallel
- Foundational tasks T007/T008/T009 can run in parallel after T005-T006
- US1 domain tasks T016/T017/T018 can run in parallel
- US2 test tasks T026/T027/T028/T051 can run in parallel
- US3 test tasks T037/T038/T039 can run in parallel

---

## Parallel Example: User Story 1

```bash
# Parallel test authoring (failing-first):
T012 + T013 + T014 + T015

# Parallel domain modeling:
T016 + T017 + T018
```

---

## Parallel Example: User Story 2

```bash
# Parallel test authoring:
T026 + T027 + T028 + T051

# After tests exist, parallelizable modeling + gateway prep:
T029 + T032
```

---

## Parallel Example: User Story 3

```bash
# Parallel test authoring:
T037 + T038 + T039

# Parallel model/query foundation:
T040 + T042
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2
2. Complete Phase 3 (US1)
3. Validate US1 independently via stage tests and backend integration
4. Demo/release MVP baseline capability

### Incremental Delivery

1. Setup + Foundational → shared baseline ready
2. Deliver US1 → validate independently → demo
3. Deliver US2 → validate independently → demo
4. Deliver US3 → validate independently → demo

### Parallel Team Strategy

1. Team completes Setup + Foundational together
2. Then split by story slice:
   - Engineer A: US1 core
   - Engineer B: US2 preset/drill-down (after US1 checkpoint)
   - Engineer C: US3 statistics (after US2 checkpoint)

---

## Notes

- `[P]` tasks touch separate files with no direct dependency on unfinished tasks
- `[USx]` labels ensure strict requirement/story traceability
- Keep OpenAPI regeneration tasks in the same story where contracts change
- Keep phase gates strict: phase 2 business customization never precedes US1 readiness
