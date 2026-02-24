# OpenAPI Regeneration Procedure

## Trigger
Regenerate OpenAPI artifacts whenever any API contract behavior changes for this feature.

## Steps
1. Update route/controller schemas and request/response models under backend presentation layer.
2. Run project OpenAPI export script:
   - `python backend/scripts/gen_openapi.py`
3. Ensure `docs/openapi.json` reflects latest backend contract.
4. Regenerate/sync frontend typed artifacts from `docs/openapi.json`.
5. Re-run impacted stage tests:
   - `uv run behave --stage http ./features/spreadsheet_platform/*.feature`
   - `uv run behave --stage http ./features/requirement_templates/*.feature`

## Validation Checklist
- Contract paths and schemas align with `specs/001-spreadsheet-project-management/contracts/spreadsheet-project-management.openapi.yaml`.
- Frontend API wrappers compile against regenerated types.
- No stale schema mismatch in CI/local validation.
