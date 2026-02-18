---
name: backend-feature-implementation
description: End-to-end workflow for implementing backend features in this FastAPI clean-architecture repository. Use when turning requirements into coordinated changes across domain, application, infrastructure, and presentation layers, and when orchestrating layer-specific implementation skills.
---

# Backend Feature Implementation

## Overview

Translate a feature request into concrete code changes across layers while preserving clean architecture boundaries and the repository conventions shown in backend/README.md and the user management example.

## Workflow

1. Read requirements and map them to behavior.
	- Identify commands (writes) and queries (reads), actors, and permissions.
	- Note invariants and domain rules vs input validation.

2. Review local conventions and examples.
	- Read backend/README.md for layer responsibilities and dependency rules.
	- Use user management as the reference flow: domain/services/user.py, application/commands/create_user.py, application/queries/list_users.py, presentation/http/controllers/users/create_user.py.

3. Split work by layer and call sub-skills.
	- Domain rules, entities, value objects, and domain services: use the domain-layer-implementation skill.
	- Interactors, ports, DTOs, transactions, and authorization: use the application-layer-implementation skill.
	- Infrastructure adapters (data mappers, readers, auth adapters): use the infrastructure-layer-implementation skill.
	- Presentation controllers, request models, and error maps: use the presentation-layer-implementation skill.
	- Tests: use the backend-testing skill for unit/integration/performance coverage.

4. Implement infrastructure and presentation wiring.
	- Add or update ports in application/common/ports as needed.
	- Add adapters in infrastructure/adapters and handlers in infrastructure/auth where required.
	- Add controllers and request models in presentation/http/controllers.
	- Register providers in setup/ioc/domain.py and setup/ioc/application.py.

5. Validate error flow and contracts.
	- Ensure domain and application exceptions are mapped to HTTP errors in controllers.
	- Keep Pydantic models in presentation only; keep domain/application framework-free.

6. Add tests or update existing ones.
	- Prefer unit tests for domain rules and application interactors; add integration tests if infrastructure behavior is new.

## Output Checklist

- Domain: entities, value objects, enums, exceptions, services, and ports if needed.
- Application: request/response DTOs, interactors or query services, port interfaces, authorization checks, transaction and flush handling.
- Infrastructure: adapters for ports, data mappers/readers, auth adapters, database models or mappings.
- Presentation: HTTP controllers, request schema models, error maps.
- Wiring: providers in setup/ioc, router registration if new endpoints are added.

## Guardrails

- Keep dependency direction: inner layers must not import outer layers.
- Put business rule validation in domain/application, not in controllers.
- Use value objects to validate domain types early and consistently.
- Prefer TypedDict for response contracts, dataclass for request contracts.
