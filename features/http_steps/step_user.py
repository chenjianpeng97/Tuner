"""
HTTP-stage step definitions for ``user.feature``.

Tests the **presentation layer in isolation** — mock interactors / handlers
are configured per-step to return success or raise domain exceptions, then
the controller's HTTP status codes and response bodies are verified.

What is tested
~~~~~~~~~~~~~~
* Controller routing and request deserialization.
* ``error_map`` exception → HTTP status code translation.
* Response body format for error cases.

References to production code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* ``UsernameAlreadyExistsError`` – domain exception
* ``AuthenticationError`` – infrastructure auth exception
* ``AUTH_ACCOUNT_INACTIVE`` – infrastructure constant
* Status codes are sourced from each controller's ``error_map``.
"""

from __future__ import annotations

import dataclasses
import uuid
from http import HTTPStatus

from behave import given, then, when

from app.application.commands.create_user import CreateUserResponse
from app.domain.enums.user_role import UserRole
from app.domain.exceptions.user import UsernameAlreadyExistsError
from app.infrastructure.auth.exceptions import AuthenticationError
from app.infrastructure.auth.handlers.constants import AUTH_ACCOUNT_INACTIVE
from app.infrastructure.auth.handlers.log_in import LogInRequest
from app.presentation.http.controllers.users.create_user import (
    CreateUserRequestPydantic,
)

# ---------------------------------------------------------------------------
# Expected HTTP status codes (from presentation-layer error_map)
# ---------------------------------------------------------------------------
STATUS_CONFLICT: int = HTTPStatus.CONFLICT  # 409
STATUS_UNAUTHORIZED: int = HTTPStatus.UNAUTHORIZED  # 401
STATUS_NO_CONTENT: int = HTTPStatus.NO_CONTENT  # 204

# ---------------------------------------------------------------------------
# API paths (mirror the router prefix hierarchy)
# ---------------------------------------------------------------------------
API_USERS = "/api/v1/users/"
API_LOGIN = "/api/v1/account/login"
API_USER_ACTIVATION = "/api/v1/users/{user_id}/activation"

# Dummy cookie to satisfy ``Security(APIKeyCookie)`` on protected endpoints.
AUTH_COOKIES: dict[str, str] = {"access_token": "fake-test-token"}


# ===================================================================
# Given – record scenario state (no HTTP calls, no mock configuration)
# ===================================================================
@given('an existing user with username "{username}"')
def given_existing_user(context, username):
    """Record that *username* already exists (for duplicate-check scenarios)."""
    context.users[username] = {"id": str(uuid.uuid4()), "is_active": True}
    context.current_username = username


@given('a deactivated user with username "{username}"')
def given_deactivated_user(context, username):
    """Record a deactivated user."""
    context.users[username] = {"id": str(uuid.uuid4()), "is_active": False}
    context.current_username = username


@given('an active user with username "{username}"')
def given_active_user(context, username):
    """Record an active user."""
    context.users[username] = {"id": str(uuid.uuid4()), "is_active": True}
    context.current_username = username


# ===================================================================
# When – configure mock, then fire the HTTP request
# ===================================================================
@when('an actor creates a user with username "{username}"')
def when_actor_creates_user(context, username):
    """``POST /api/v1/users/`` — admin endpoint.

    If *username* was recorded in a Given step the mock raises
    ``UsernameAlreadyExistsError`` which the controller's error_map
    translates to **409 Conflict**.
    """
    mocks = context.mocks
    if username in context.users:
        mocks.create_user.execute.side_effect = UsernameAlreadyExistsError(
            username,
        )
    else:
        mocks.create_user.execute.return_value = CreateUserResponse(
            id=uuid.uuid4(),
        )

    request_body = CreateUserRequestPydantic(
        username=username,
        password="testpass1",
        role=UserRole.USER,
    )
    context.response = context.client.post(
        API_USERS,
        json=request_body.model_dump(mode="json"),
        cookies=AUTH_COOKIES,
    )
    context.current_username = username


@when("the user attempts to authenticate")
def when_user_attempts_auth(context):
    """``POST /api/v1/account/login`` — public endpoint.

    If the current user is deactivated the mock raises
    ``AuthenticationError(AUTH_ACCOUNT_INACTIVE)`` which the controller's
    error_map translates to **401 Unauthorized**.
    """
    mocks = context.mocks
    username = context.current_username
    user_info = context.users[username]

    if not user_info["is_active"]:
        mocks.log_in.execute.side_effect = AuthenticationError(
            AUTH_ACCOUNT_INACTIVE,
        )

    request_body = LogInRequest(username=username, password="testpass1")
    context.response = context.client.post(
        API_LOGIN,
        json=dataclasses.asdict(request_body),
    )


@when("an authorized actor activates the user")
def when_authorized_activates(context):
    """``PUT /api/v1/users/{user_id}/activation`` — admin endpoint."""
    context.mocks.activate_user.execute.return_value = None

    user_id = context.users[context.current_username]["id"]
    url = API_USER_ACTIVATION.format(user_id=user_id)
    context.response = context.client.put(url, cookies=AUTH_COOKIES)


@when("an authorized actor deactivates the user")
def when_authorized_deactivates(context):
    """``DELETE /api/v1/users/{user_id}/activation`` — admin endpoint."""
    context.mocks.deactivate_user.execute.return_value = None

    user_id = context.users[context.current_username]["id"]
    url = API_USER_ACTIVATION.format(user_id=user_id)
    context.response = context.client.delete(url, cookies=AUTH_COOKIES)


# ===================================================================
# Then – assert on HTTP responses
# ===================================================================
@then('the request is rejected with a "user already exists" error')
def then_request_rejected_duplicate(context):
    """``UsernameAlreadyExistsError`` → **409** (create_user error_map)."""
    assert context.response.status_code == STATUS_CONFLICT, (
        f"Expected {STATUS_CONFLICT}, got {context.response.status_code}: "
        f"{context.response.text}"
    )
    body = context.response.json()
    assert "already exists" in body.get("error", "").lower(), (
        f"Error body missing domain message: {body}"
    )


@then("the authentication is denied")
def then_authentication_denied(context):
    """``AuthenticationError`` → **401** (log_in error_map).

    Verifies the response body contains the ``AUTH_ACCOUNT_INACTIVE``
    constant from the infrastructure layer.
    """
    assert context.response.status_code == STATUS_UNAUTHORIZED, (
        f"Expected {STATUS_UNAUTHORIZED}, got {context.response.status_code}: "
        f"{context.response.text}"
    )
    body = context.response.json()
    assert AUTH_ACCOUNT_INACTIVE in body.get("error", ""), (
        f"Expected '{AUTH_ACCOUNT_INACTIVE}' in error, got: {body}"
    )


@then("the user becomes active")
def then_user_becomes_active(context):
    """Activation endpoint returns **204 No Content** on success."""
    assert context.response.status_code == STATUS_NO_CONTENT, (
        f"Expected {STATUS_NO_CONTENT}, got {context.response.status_code}: "
        f"{context.response.text}"
    )


@then("the user becomes deactivated")
def then_user_becomes_deactivated(context):
    """Deactivation endpoint returns **204 No Content** on success."""
    assert context.response.status_code == STATUS_NO_CONTENT, (
        f"Expected {STATUS_NO_CONTENT}, got {context.response.status_code}: "
        f"{context.response.text}"
    )
