---
name: domain-layer-implementation
description: Implement domain layer components in this repository. Use when defining entities, value objects, enums, domain services, exceptions, and domain ports while keeping business rules independent from frameworks and infrastructure.
---

# Domain Layer Implementation

## Overview

Model business rules and invariants as domain types and services, keeping the domain layer framework-agnostic and stable.

## Workflow

1. Extract domain concepts and invariants from requirements.
	- Identify entities (identity), value objects (no identity), and domain services.
	- Decide which rules are invariants vs procedural policies.

2. Create or update value objects.
	- Put validation and normalization in the value object constructor.
	- Example: domain/value_objects/username.py.

3. Create or update entities.
	- Keep entity fields typed with value objects and enums.
	- Example: domain/entities/user.py.

4. Add domain services for behavior that does not belong to a single entity.
	- Example: domain/services/user.py for user creation, password operations, and role/activation changes.

5. Define ports for external capabilities.
	- Use domain/ports for dependencies like ID generators or hashing.
	- Examples: domain/ports/user_id_generator.py, domain/ports/password_hasher.py.

6. Add domain exceptions and enums.
	- Keep errors specific and raised only when invariants are violated.
	- Examples: domain/exceptions/user.py, domain/enums/user_role.py.

## Guardrails

- Do not import infrastructure, FastAPI, SQLAlchemy, or other frameworks in domain.
- Prefer rich value objects to keep validation local and consistent.
- Keep async only where a port requires it; pure domain logic stays synchronous.
- Use domain exceptions instead of HTTP errors or database exceptions.

## Review Checklist

- Entities and value objects use domain types and enforce invariants.
- Domain services only depend on other domain types and ports.
- Ports represent external effects and have no concrete implementations here.
- Exceptions map to violated rules, not infrastructure failures.
