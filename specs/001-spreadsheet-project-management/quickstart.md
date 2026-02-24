# Quickstart — Spreadsheet-based Project Management

## Goal
Validate feature delivery in two phases with constitution-aligned gates:
1. Standard spreadsheet demo capability first.
2. Project-management preset extension second.

## Prerequisites
- Workspace synced (`uv sync --all-packages --all-groups`)
- Backend and frontend dependencies installed
- Database/service prerequisites available per project environment

## Phase 1: Standard online spreadsheet demo
1. Start from feature branch `001-spreadsheet-project-management`.
2. Implement/verify generic spreadsheet operations:
   - Create/read/update/delete rows/cells
   - Apply/clear filters
   - Deterministic behavior for concurrent updates
3. Run stage-first validation:
   - `uv run behave --stage http ./features/spreadsheet_platform/*.feature`
   - `uv run pytest backend/tests -k spreadsheet`
   - (Optional targeted UI flow) `uv run behave --stage ui ./features/spreadsheet_platform.feature`
4. Gate check:
   - All phase-1 acceptance scenarios pass (SC-003 prerequisite)
   - No contract drift between endpoint behavior and OpenAPI source

## Phase 2: Project-management preset extension
1. Instantiate/verify preset tables built on phase-1 capability.
2. Validate drill-down, requirement relationship maintenance, and asset/statistics behavior.
3. Run stage-first validation:
   - `uv run behave --stage http ./features/requirement_templates/*.feature`
   - `cd backend && uv run pytest tests/app/integration/test_requirement_drilldown_linking.py tests/app/integration/test_create_product_requirement.py tests/app/integration/test_requirement_statistics.py -q`
   - `uv run behave --stage ui ./features/user.feature` (or targeted preset UI scenarios)
4. Gate check:
   - P2/P3 scenarios pass
   - Statistics and relationship behavior satisfy FR-010~FR-013 and SC-004/SC-005

## Verified commands snapshot
- `uv run behave --stage http ./features/requirement_templates/product_requirement_list_template.feature ./features/requirement_templates/unified_customer_requirement_template.feature`
- `uv run behave --stage http ./features/requirement_templates/requirement_asset_management_template.feature ./features/requirement_templates/status_and_progress_template.feature`
- `cd backend && APP_ENV=local uv run python scripts/gen_openapi.py`

## Contract Update Workflow
When API behavior changes:
1. Update backend contract definitions and route behavior.
2. Regenerate/export `docs/openapi.json`.
3. Regenerate frontend typed artifacts/mocks from OpenAPI.
4. Re-run impacted stage tests before merge.

## Merge Readiness Checklist
- Traceability: changed behaviors map to spec user stories/FRs.
- Stage tests: relevant `http`/`ui`/`pytest` suites are green.
- Clean architecture: no boundary violations introduced.
- Incremental delivery: phase gates respected (phase 2 never merged before phase 1 gate).