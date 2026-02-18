---
name: backend-testing
description: Add and run backend tests for this repository. Use when writing unit, integration, or performance tests under backend/tests, or when running pytest and coverage via the Makefile targets.
---

# Backend Testing

## Overview

Add tests that follow the existing pytest structure and run them with Makefile targets for pytest and coverage.

## Test Structure

- Unit tests: tests/app/unit/{domain,application,infrastructure,setup}
- Integration tests: tests/app/integration
- Performance tests: tests/app/performance (use markers like slow)
- Factories and helpers: tests/app/unit/factories

## Workflow

1. Choose the test type and location.
	- Domain rules: tests/app/unit/domain
	- Application services: tests/app/unit/application
	- Infrastructure adapters: tests/app/unit/infrastructure
	- Config/setup: tests/app/unit/setup
	- Cross-boundary behavior: tests/app/integration

2. Follow existing pytest patterns.
	- Use pytest.mark.asyncio for async functions.
	- Use pytest.mark.parametrize for rule matrices.
	- Use factories for consistent value objects and entities.

3. Assert domain invariants and error behavior.
	- Example: value object validation raises DomainTypeError.
	- Example: domain services raise RoleAssignmentNotPermittedError for invalid roles.

4. Keep infrastructure tests focused on adapter behavior.
	- Use markers like slow for heavy hashing or IO.
	- Verify adapters implement port expectations and return domain types.

5. Run tests using Makefile targets.
	- Unit tests: make code.test (pytest -v)
	- Coverage: make code.cov (coverage run -m pytest; coverage combine; coverage report)
	- Coverage HTML: make code.cov.html (coverage html)

## Guardrails

- Keep tests aligned with layer boundaries.
- Prefer factories instead of hand-built domain types.
- Use stable assertions on domain errors rather than error strings.

## Review Checklist

- New behavior has unit coverage at its layer.
- Async tests include pytest.mark.asyncio.
- Performance-heavy tests are marked slow.
- Coverage targets run without importing infrastructure into core tests.
