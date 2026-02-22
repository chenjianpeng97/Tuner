---
name: http-stage-behave-testing
description: Implement Behave HTTP-stage step definitions that test presentation-layer controllers in isolation. Use when turning Gherkin feature files into runnable tests that exercise FastAPI routes with mocked Dishka DI (no database, auth infra, or external services required).
---

# HTTP-Stage Behave Testing

## Overview

Test HTTP controller orchestration in isolation by replacing all Dishka-injected interactors and handlers with `AsyncMock` instances, running requests through FastAPI's `TestClient`, and asserting on HTTP status codes and response bodies.

This approach verifies:
- Controller routing and request deserialization.
- `error_map` exception-to-HTTP-status-code translation.
- Response body format for error and success cases.
- Middleware behaviour (e.g. `ASGIAuthMiddleware` cookie handling).

It does **not** test business logic, database access, or external services.

## Key Files

| File | Purpose |
|---|---|
| `features/<name>.feature` | Gherkin scenarios (domain language) |
| `features/mock_app.py` | `MockRegistry` + `_MockProvider` + `create_test_app()` |
| `features/http_environment.py` | Behave `--stage http` hooks (`before_all`, `before_scenario`, `after_scenario`) |
| `features/http_steps/step_<name>.py` | Step definitions (Given/When/Then) |

## Workflow

1. **Write or receive the `.feature` file.**
   - Place it under `features/`.
   - Follow rule-based structure (`Feature → Rule → Scenario → Given/When/Then`).

2. **Create or extend `features/mock_app.py`.**
   - Define `MockRegistry` with one `AsyncMock` attribute per Dishka-provided interactor/handler.
   - Define `_MockProvider(Provider)` with one `@provide` method per type, returning the corresponding mock from the registry.
   - Define `create_test_app(registry)` that builds a `FastAPI` app with production routes and middleware but a mocked DI container.

   ```python
   class MockRegistry:
       def __init__(self) -> None:
           self._init_mocks()

       def _init_mocks(self) -> None:
           self.create_user: AsyncMock = AsyncMock()
           # ... one attribute per interactor/handler

       def reset_all(self) -> None:
           self._init_mocks()

   class _MockProvider(Provider):
       scope = Scope.REQUEST

       def __init__(self, registry: MockRegistry) -> None:
           super().__init__()
           self._r = registry

       @provide
       def create_user_interactor(self) -> CreateUserInteractor:
           return self._r.create_user  # type: ignore[return-value]
       # ... one @provide per type

   def create_test_app(registry: MockRegistry) -> FastAPI:
       app = FastAPI()
       app.add_middleware(ASGIAuthMiddleware)
       app.include_router(create_root_router())
       container = make_async_container(_MockProvider(registry))
       setup_dishka(container, app)
       return app
   ```

3. **Create or extend `features/http_environment.py`.**
   - Add `features/` and `backend/src` to `sys.path` so both `mock_app` and `app.*` resolve.
   - `before_all`: instantiate `MockRegistry` and `create_test_app(mocks)`, store on `context`.
   - `before_scenario`: call `mocks.reset_all()`, initialise empty state dicts, create a fresh `TestClient(context.app)`.
   - `after_scenario`: close the `TestClient`.

   ```python
   def before_all(context):
       context.mocks = MockRegistry()
       context.app = create_test_app(context.mocks)

   def before_scenario(context, scenario):
       context.mocks.reset_all()
       context.users = {}
       context.response = None
       context.client = TestClient(context.app)

   def after_scenario(context, scenario):
       if (client := getattr(context, "client", None)):
           client.close()
   ```

4. **Implement step definitions under `features/http_steps/`.**

   Follow the three-phase pattern:

   - **Given** — record scenario state only (populate `context.users`, `context.current_username`, etc.). No HTTP calls, no mock configuration.
   - **When** — configure mock behaviour, then fire the HTTP request:
     - Error scenario: set `context.mocks.<interactor>.execute.side_effect = <DomainException>(...)`.
     - Success scenario: set `context.mocks.<interactor>.execute.return_value = <value>`.
     - Send request via `context.client.post(...)`, `context.client.put(...)`, etc.
     - For protected endpoints, pass `cookies=AUTH_COOKIES` where `AUTH_COOKIES = {"access_token": "fake-test-token"}`.
   - **Then** — assert on `context.response.status_code` and optionally `context.response.json()`.

   Use constants for status codes (sourced from the controller's `error_map`):
   ```python
   STATUS_CONFLICT = HTTPStatus.CONFLICT        # 409
   STATUS_UNAUTHORIZED = HTTPStatus.UNAUTHORIZED # 401
   STATUS_NO_CONTENT = HTTPStatus.NO_CONTENT     # 204
   ```

   API paths mirror the router prefix hierarchy:
   ```python
   API_USERS = "/api/v1/users/"
   API_LOGIN = "/api/v1/account/login"
   API_USER_ACTIVATION = "/api/v1/users/{user_id}/activation"
   ```

5. **Dry-run to verify step matching, then execute.**
   ```bash
   behave --stage http --dry-run
   behave --stage http
   ```

## Adding a New Controller to the Test Suite

1. Add an `AsyncMock` attribute to `MockRegistry._init_mocks()`.
2. Add a `@provide` method to `_MockProvider` returning the new type from the registry.
3. Import the relevant domain/infra exceptions in `step_<name>.py`.
4. Write Given/When/Then steps following the three-phase pattern.
5. Look up the controller's `error_map` to determine the expected HTTP status codes.

## Discovering Mock Targets

To identify what types need mocking:

1. Read the Dishka providers in `app/setup/ioc/` — each `@provide` method declares a return type.
2. Read each controller function signature — `FromDishka[<Type>]` parameters are the injection points.
3. Only mock the types actually injected into controllers (interactors, handlers, query services). Do **not** mock ports (gateways, flushers, identity providers) — those are internal to the interactors.

## Guardrails

- Mock at the **interactor/handler boundary**, not at the port/gateway level. The presentation layer only sees interactors.
- Do **not** test business logic in HTTP steps — that belongs in unit tests under `tests/app/unit/`.
- Keep step definitions thin: Given records state, When configures mock and fires request, Then asserts response.
- Import domain exceptions and infrastructure constants from production code — do not duplicate error strings.
- API path constants in step files must match the router prefix hierarchy exactly.
- One `MockRegistry` per app; call `reset_all()` in `before_scenario` to ensure scenario isolation.

## Review Checklist

- Every Dishka-injected type used by tested controllers has a corresponding `MockRegistry` attribute and `_MockProvider` method.
- Step definitions import domain exceptions and infrastructure constants from production modules.
- `before_scenario` resets mocks and creates a fresh `TestClient`.
- Status code assertions reference the controller's `error_map`, not hard-coded guesses.
- `behave --stage http --dry-run` shows all steps matched with no undefined steps.
- `behave --stage http` passes with 0 failures.
