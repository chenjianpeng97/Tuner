---
name: presentation-layer-implementation
description: Implement presentation layer controllers and request models in this repository. Use when adding HTTP routes, validation schemas, error maps, and controller wiring that adapts external requests to application interactors.
---

# Presentation Layer Implementation

## Overview

Add HTTP controllers and request models that validate inputs, call interactors or query services, and map errors to HTTP responses.

## Workflow

1. Locate the controller area.
	- Use app/presentation/http/controllers for routers grouped by context.
	- Follow the pattern in users/create_user.py and account/change_password.py.

2. Define request models.
	- Use Pydantic models for request validation and OpenAPI schema.
	- Keep models frozen and minimal; avoid business rules.

3. Create the router function.
	- Use ErrorAwareRouter and error maps for domain and infrastructure exceptions.
	- Use @inject and FromDishka for dependency injection.
	- Use Security(cookie_scheme) for authenticated endpoints.

4. Map request to application DTOs.
	- Convert Pydantic input to application dataclass request objects.
	- Return TypedDict response from interactor or query service.

5. Register routers.
	- Add router to the appropriate module so it gets included in app setup.

## Guardrails

- Keep controllers thin: validation and translation only.
- Do not import SQLAlchemy models or infrastructure adapters.
- Keep exception-to-HTTP mapping in controllers, not in core layers.
- Do not embed business rules in Pydantic validators.

## Review Checklist

- Request/response mapping is explicit and minimal.
- Error map covers domain and infrastructure exceptions.
- Authorization errors map to 403, authentication to 401, validation to 400 or 422.
- Controllers call only application interactors or query services.
