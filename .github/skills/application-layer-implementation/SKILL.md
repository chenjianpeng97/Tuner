---
name: application-layer-implementation
description: Implement application layer interactors, query services, ports, and DTOs in this repository. Use when orchestrating domain logic, authorization, transactions, and data access via ports, while keeping the application layer framework-agnostic.
---

# Application Layer Implementation

## Overview

Build application-level use case handlers that coordinate domain logic, authorization, and persistence through ports.

## Workflow

1. Identify use cases as commands or queries.
	- Commands change state; queries are optimized reads.
	- Examples: application/commands/create_user.py, application/queries/list_users.py.

2. Define request and response DTOs.
	- Use dataclass with slots for request input.
	- Use TypedDict for responses that cross layer boundaries.

3. Implement interactor or query service.
	- Validate permissions using application/common/services/authorization.
	- Use current user via application/common/services/current_user.
	- Call domain services and ports, not infrastructure.

4. Use ports for external effects.
	- Command side: application/common/ports/user_command_gateway, flusher, transaction_manager.
	- Query side: application/common/ports/user_query_gateway.

5. Control transactions and error flow.
	- Flush, handle expected domain errors, then commit.
	- Keep infrastructure exceptions in the signature for controllers to map.

6. Register providers in IoC.
	- Update setup/ioc/application.py with new interactors, query services, and port bindings.

## Guardrails

- Do not import FastAPI, SQLAlchemy, or other infrastructure frameworks.
- Use domain value objects for validation and normalization.
- Keep interactors stateless and independently callable.
- Avoid interactor-to-interactor calls; extract shared logic into services if needed.

## Review Checklist

- DTOs are plain and serializable.
- Authorization happens before sensitive operations.
- Ports express dependencies; implementations live in infrastructure.
- Transaction boundaries are clear and consistent.
