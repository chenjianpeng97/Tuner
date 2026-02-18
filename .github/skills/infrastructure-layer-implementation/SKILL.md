---
name: infrastructure-layer-implementation
description: Implement infrastructure adapters and services in this repository. Use when wiring ports to concrete implementations (database, auth, hashing, IO), mapping persistence models, and adding infrastructure exceptions or handlers while keeping the core layers untouched.
---

# Infrastructure Layer Implementation

## Overview

Build concrete adapters for application and domain ports, handle integration details, and keep infrastructure code isolated from the core.

## Workflow

1. Identify required ports from the application or domain layer.
	- Command side uses data mappers and flusher; query side uses readers.
	- Auth uses access revokers and identity providers.

2. Implement adapters.
	- Add adapters under app/infrastructure/adapters for persistence and IO.
	- Add auth-related adapters under app/infrastructure/auth/adapters.
	- Ensure each adapter implements a specific port from application/common/ports or domain/ports.

3. Map storage models to domain types.
	- Keep SQLAlchemy or external SDK specifics inside infrastructure.
	- Translate raw data into value objects and entities before returning to the application layer.

4. Define infrastructure exceptions.
	- Use infrastructure exceptions to represent integration failures (database unavailable, hasher busy).
	- Re-raise domain-specific errors only when constraints enforce domain rules.

5. Register adapters in IoC.
	- Bind adapters to ports in setup/ioc/application.py or setup/ioc/domain.py.

## Guardrails

- Do not import infrastructure into application or domain.
- Keep external SDKs, SQLAlchemy models, and FastAPI dependencies here.
- Ensure adapters return domain types or query models, not ORM entities.
- Keep side effects localized to adapter methods.

## Review Checklist

- All ports have concrete implementations in infrastructure.
- Adapters translate data at the boundary and hide implementation details.
- Exceptions are layered (infrastructure vs domain) and are mapped by controllers.
- IoC providers are updated to bind ports to adapters.
