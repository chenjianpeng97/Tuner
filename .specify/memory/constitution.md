<!--
Sync Impact Report
- Version change: template-initial → 1.0.0
- Modified principles:
	- Placeholder Principle 1 → I. Requirements-to-Behavior Traceability
	- Placeholder Principle 2 → II. Contract-First API & Typed Frontend Integration
	- Placeholder Principle 3 → III. Test-First by Stage (NON-NEGOTIABLE)
	- Placeholder Principle 4 → IV. Clean Architecture Boundary Integrity
	- Placeholder Principle 5 → V. Incremental Delivery, Verification, and Git Discipline
- Added sections:
	- Engineering Constraints
	- Delivery Workflow & Quality Gates
- Removed sections:
	- None
- Templates requiring updates:
	- ✅ updated: .specify/templates/plan-template.md
	- ✅ updated: .specify/templates/spec-template.md
	- ✅ updated: .specify/templates/tasks-template.md
	- ⚠ pending: .specify/templates/commands/*.md (directory not present in repository)
	- ✅ updated: README.md (onboarding reference to constitution)
- Follow-up TODOs:
	- None
-->

# Tuner Constitution

## Core Principles

### I. Requirements-to-Behavior Traceability
Every feature MUST start from explicit requirements in `docs/requirements.md` (or approved
equivalent), then be decomposed into executable behavior in `features/*.feature` before coding.
Implementation tasks MUST map back to scenarios and acceptance criteria, and changes that are not
traceable to a requirement MUST be rejected.

Rationale: This project exists to manage requirements-to-delivery flow; traceability is the core
product value and cannot be optional.

### II. Contract-First API & Typed Frontend Integration
Backend presentation contracts MUST be defined before cross-layer implementation, and OpenAPI MUST
be exported to `docs/openapi.json` when contract changes occur. Frontend API models MUST be
generated from OpenAPI artifacts; handwritten duplicate request/response types are not allowed.
Mock services MUST preserve the same endpoint contracts and error model as production APIs.

Rationale: A single contract source prevents backend/frontend drift and enables independent, safe
parallel delivery.

### III. Test-First by Stage (NON-NEGOTIABLE)
Work MUST follow a test-first sequence at the appropriate stage: behavior scenarios first,
`behave --stage http` orchestration tests for controller/API behavior, UI-stage tests for frontend
acceptance flows, and backend unit/integration tests for domain/application/infrastructure logic.
Code MAY be merged only after applicable stage tests are green.

Rationale: The repository adopts BDD and clean-architecture TDD to validate behavior before
implementation details.

### IV. Clean Architecture Boundary Integrity
Backend code MUST preserve domain, application, infrastructure, and presentation boundaries.
Business rules MUST live in domain/application layers, presentation MUST orchestrate without domain
logic leakage, and infrastructure MUST implement ports without changing core business semantics.
Cross-layer shortcuts that bypass ports or collapse boundaries MUST not be introduced.

Rationale: Architectural boundaries are required for long-term maintainability, testability, and
safe refactoring.

### V. Incremental Delivery, Verification, and Git Discipline
Delivery MUST proceed in small, independently verifiable increments (MVP-first by user story).
Each increment MUST include validation evidence (tests or contract checks) and MUST be recorded
with Conventional Commit messages. Feature/fix branches are REQUIRED for substantive changes; merge
to `main` requires passing relevant tests.

Rationale: Small verified increments reduce rollback risk and preserve an auditable delivery trail.

## Engineering Constraints

- Python backend and React frontend MUST stay contract-compatible through OpenAPI-driven artifacts.
- Authentication flows MUST align with cookie-based auth behavior and server-side authority checks.
- Error responses exposed to clients MUST keep a stable `{ "error": "..." }` contract unless a
	versioned API change is approved.
- New dependencies SHOULD be introduced only when existing stack capabilities are insufficient, and
	the decision MUST be documented in the plan/research artifacts.
- Generated files (e.g., OpenAPI-derived types) MUST be regenerated as part of contract changes.

## Delivery Workflow & Quality Gates

1. Clarify requirements and confirm acceptance scenarios.
2. Produce or update `.feature` files before implementation.
3. Define/adjust HTTP contracts and export `docs/openapi.json`.
4. Implement and pass `behave --stage http` tests for controller orchestration.
5. Implement frontend against generated schema and aligned mocks.
6. Complete backend domain/application/infrastructure implementation with tests.
7. Run relevant test suites (at minimum impacted stage tests) before merge.

Review checklist (required for PR approval):
- Traceability from changed code to requirements/scenarios is explicit.
- Architecture boundaries are respected.
- Contract changes include OpenAPI and generated type updates.
- Applicable tests pass and failure cases are covered.
- Commit history follows Conventional Commits and reflects logical increments.

## Governance

- Authority: This constitution supersedes conflicting local workflow notes for engineering process
	and quality gates.
- Amendment process: Any amendment MUST include (a) rationale, (b) impacted templates/docs,
	(c) migration guidance for in-flight work, and (d) version bump justification.
- Versioning policy:
	- MAJOR: Incompatible governance changes, principle removals, or redefinitions.
	- MINOR: New principle/section or materially expanded mandatory guidance.
	- PATCH: Clarifications, wording improvements, typo/non-semantic edits.
- Compliance review: Every plan, spec, and task set MUST include an explicit constitution check.
	PR reviews MUST block merges that violate non-negotiable principles.
- Operational guidance reference: onboarding and day-to-day workflow docs MUST point to this file
	as the source of process truth.

**Version**: 1.0.0 | **Ratified**: 2026-02-24 | **Last Amended**: 2026-02-24
