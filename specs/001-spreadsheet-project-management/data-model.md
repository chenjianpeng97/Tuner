# Data Model — Spreadsheet-based Project Management

## Entity: SpreadsheetInstance
- Purpose: A project-scoped spreadsheet container instantiated either as generic demo table or from a preset template.
- Fields:
  - `id` (string, required, unique)
  - `project_id` (string, required, indexed)
  - `template_key` (string, optional for pure generic demo)
  - `name` (string, required)
  - `mode` (enum: `generic_demo` | `project_management_preset`)
  - `created_at` / `updated_at` (datetime, required)
- Validation rules:
  - `project_id` must exist in project context.
  - `mode=project_management_preset` requires valid preset `template_key`.

## Entity: TableColumn
- Purpose: Defines column schema for a spreadsheet instance.
- Fields:
  - `id`, `spreadsheet_id`, `key`, `label`, `data_type`, `position`, `is_filterable`
- Validation rules:
  - `key` unique per `spreadsheet_id`.
  - `position` must be non-negative and unique in table ordering.

## Entity: TableRow
- Purpose: Represents one row record in the spreadsheet.
- Fields:
  - `id`, `spreadsheet_id`, `row_index`, `created_at`, `updated_at`
- Validation rules:
  - `row_index` unique per `spreadsheet_id`.

## Entity: CellValue
- Purpose: Stores value at row-column intersection.
- Fields:
  - `id`, `spreadsheet_id`, `row_id`, `column_id`, `value`, `value_type`, `revision`
- Validation rules:
  - (`row_id`, `column_id`) unique.
  - `value_type` compatible with referenced column `data_type`.

## Entity: FilterPreset
- Purpose: Represents user-applied query condition set for generic/preset tables.
- Fields:
  - `id`, `spreadsheet_id`, `conditions` (list), `is_active`, `applied_by`, `applied_at`
- Validation rules:
  - Conditions must reference existing filterable columns.

## Entity: CustomerRequirement
- Purpose: Customer-facing requirement/matter represented in preset tables.
- Fields:
  - `id`, `project_id`, `title`, `description`, `labels`, `status`, `progress`
- Validation rules:
  - Labels determine decomposable vs non-decomposable behavior.

## Entity: ProductRequirement
- Purpose: Decomposed requirement under customer requirement context.
- Fields:
  - `id`, `project_id`, `customer_requirement_id`, `module`, `submodule`, `level`, `content`
- Validation rules:
  - Must reference existing `customer_requirement_id` in same project.

## Entity: RequirementAsset
- Purpose: File/asset linked to requirement context or project scope.
- Fields:
  - `id`, `project_id`, `name`, `type`, `customer_requirement_id?`, `product_requirement_id?`
- Validation rules:
  - Asset belongs to exactly one project.
  - Requirement links optional; unlinked assets still valid at project level.

## Entity: RequirementRelation
- Purpose: Tracks many-to-many and derived links for requirement drill-down and statistics.
- Fields:
  - `id`, `project_id`, `customer_requirement_id`, `product_requirement_id`, `relation_type`
- Validation rules:
  - Prevent duplicate relation tuples.

## Relationships
- `SpreadsheetInstance` 1..* `TableColumn`
- `SpreadsheetInstance` 1..* `TableRow`
- `TableRow` 1..* `CellValue`
- `TableColumn` 1..* `CellValue`
- `SpreadsheetInstance` 0..* `FilterPreset`
- `CustomerRequirement` 1..* `ProductRequirement`
- `CustomerRequirement` *..* `ProductRequirement` via `RequirementRelation` (business rule supports multiple mappings)
- `CustomerRequirement` 0..* `RequirementAsset`
- `ProductRequirement` 0..* `RequirementAsset`

## State Transitions

### Spreadsheet write consistency
- `pending_write` → `committed` → `observable`
- Constraint: successful write must become observable to subsequent reads in near real time.

### Requirement decomposition eligibility
- `non_decomposable` ↔ `decomposable`
- Transition driver: label/rule changes at project scope.
- Constraint: drill-down allowed only in `decomposable` state.

### Requirement progress
- `not_started` → `in_progress` → `blocked`/`done` (project-configurable labels may extend this set)
- Constraint: transition path remains flexible but auditable in history.