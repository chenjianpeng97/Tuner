"""
UI-stage step definitions for ``user.feature``.

Implements the **same** Gherkin steps as ``http_steps/step_user.py`` but
drives a real browser via Playwright + Page Objects.  Run with::

    uv run behave --stage ui

Prerequisites:
  1. Backend running (``cd backend && make up APP_ENV=local``)
  2. Frontend running (``cd frontend && pnpm dev:api``)
  3. A seeded ``super_admin / admin123`` account in the database
  4. Playwright browsers installed (``playwright install chromium``)

All user creation uses a default password (``DEFAULT_PASSWORD``) unless
the scenario provides one explicitly.
"""

from __future__ import annotations

from playwright.sync_api import expect
from test_config import DEFAULT_TIMEOUT_MS, SHORT_TIMEOUT_MS

from behave import given, then, when

from pages.sign_in_page import SignInPage
from pages.users_page import UsersPage
from pages.nav_bar import NavBar
from pages.notifications_page import NotificationsPage

# Default password used when the feature file doesn't specify one.
DEFAULT_PASSWORD = "testpass1"


# ===================================================================
# Helpers — lazily create page objects once per scenario
# ===================================================================


def _sign_in_page(context) -> SignInPage:
    if not hasattr(context, "_sign_in_page"):
        context._sign_in_page = SignInPage(context.page, context.base_url)
    return context._sign_in_page


def _users_page(context) -> UsersPage:
    if not hasattr(context, "_users_page"):
        context._users_page = UsersPage(context.page, context.base_url)
    return context._users_page


def _nav_bar(context) -> NavBar:
    if not hasattr(context, "_nav_bar"):
        context._nav_bar = NavBar(context.page)
    return context._nav_bar


def _ensure_admin_on_users_page(context) -> None:
    """Log in as admin (if needed) and navigate to /users."""
    # Each scenario starts with a fresh browser context, so always log in.
    sign_in = _sign_in_page(context)
    sign_in.navigate()
    sign_in.login(context.admin_username, context.admin_password)
    context.page.wait_for_url(
        lambda url: "/sign-in" not in url, timeout=DEFAULT_TIMEOUT_MS
    )

    users = _users_page(context)
    users.navigate()
    users.expect_visible()


def _create_user_via_ui(
    context, username: str, password: str = DEFAULT_PASSWORD
) -> None:
    """Create a user through the Add User dialog."""
    users = _users_page(context)
    users.create_user(username, password)
    # Wait for the success toast or capture failure state for debugging
    notifications = NotificationsPage(context.page)
    success_toast = notifications.locator(role="status", toast_type="success")
    error_toast = notifications.locator(role="alert", toast_type="error")
    try:
        success_toast.first.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
    except Exception:
        # Save debug artifacts: screenshot + page HTML
        import os

        os.makedirs("artifacts", exist_ok=True)
        safe_name = (
            context.scenario.name.replace(" ", "_").replace("/", "_")
            if hasattr(context, "scenario")
            else "scenario"
        )
        screenshot_path = f"artifacts/{safe_name}.png"
        html_path = f"artifacts/{safe_name}.html"
        try:
            context.page.screenshot(path=screenshot_path, full_page=True)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(context.page.content())
        except Exception:
            pass

        # If an error toast is visible, inspect it. If it's a duplicate-user
        # message treat the step as idempotent (user already exists) — this
        # keeps the Given step stable when the test DB already contains the
        # user. For other errors, fail and include artifacts.
        try:
            if error_toast.first.is_visible():
                text = error_toast.first.inner_text()
                if "already exists" in text:
                    # Ensure the row is present and continue without raising.
                    users.expect_user_row(username)
                    # If the Add User dialog remained open (duplicate error),
                    # close it so subsequent steps can interact normally.
                    try:
                        dialog_close = context.page.locator("[data-slot='dialog-close']")
                        if dialog_close.first.is_visible():
                            dialog_close.first.click()
                    except Exception:
                        pass
                    return
                raise AssertionError(f"Create user failed: error toast visible: {text}")
        except Exception:
            pass

        raise AssertionError(
            f"Create user did not show success toast within timeout. Artifacts: {screenshot_path}, {html_path}"
        )

    # Allow the table to refresh after invalidation
    users.expect_user_row(username)


# ===================================================================
# Given
# ===================================================================


@given('an existing user with username "{username}"')
def given_existing_user(context, username):
    """Create *username* via the UI so it exists for subsequent steps."""
    _ensure_admin_on_users_page(context)
    _create_user_via_ui(context, username)
    context.current_username = username


@given('a deactivated user with username "{username}"')
def given_deactivated_user(context, username):
    """Create *username*, then deactivate via the row‐action menu."""
    _ensure_admin_on_users_page(context)
    _create_user_via_ui(context, username)

    users = _users_page(context)
    users.open_row_menu(username)
    users.click_row_action("Deactivate")

    # Wait for the deactivation success toast
    notifications = NotificationsPage(context.page)
    notifications.wait_for_toast(
        "deactivated", role="status", timeout=DEFAULT_TIMEOUT_MS
    )
    context.current_username = username


@given('an active user with username "{username}"')
def given_active_user(context, username):
    """Create *username* — new users are active by default."""
    _ensure_admin_on_users_page(context)
    _create_user_via_ui(context, username)
    context.current_username = username


# ===================================================================
# When
# ===================================================================


@when('an actor creates a user with username "{username}"')
def when_actor_creates_user(context, username):
    """Try to create *username* via the Add User dialog.

    If the user already exists, the backend returns a conflict error
    which the UI shows as an error toast.
    """
    # Ensure we are on the users page (admin should already be logged in
    # from the Given step, but navigate just in case).
    users = _users_page(context)
    if "/users" not in context.page.url:
        users.navigate()
        users.expect_visible()
    users.create_user(username, DEFAULT_PASSWORD)
    context.current_username = username


@when("the user attempts to authenticate")
def when_user_attempts_auth(context):
    """Sign out admin, then try to sign in as the current scenario user."""
    username = context.current_username

    # Sign out admin first
    _nav_bar(context).sign_out()
    context.page.wait_for_url(lambda url: "/sign-in" in url, timeout=DEFAULT_TIMEOUT_MS)

    # Try to sign in as the test user
    sign_in = _sign_in_page(context)
    sign_in.login(username, DEFAULT_PASSWORD)


@when("an authorized actor activates the user")
def when_authorized_activates(context):
    """Click Activate in the row menu for the current user."""
    username = context.current_username
    users = _users_page(context)

    # Make sure we're on the users page
    if "/users" not in context.page.url:
        users.navigate()
        users.expect_visible()

    users.open_row_menu(username)
    users.click_row_action("Activate")


@when("an authorized actor deactivates the user")
def when_authorized_deactivates(context):
    """Click Deactivate in the row menu for the current user."""
    username = context.current_username
    users = _users_page(context)

    # Make sure we're on the users page
    if "/users" not in context.page.url:
        users.navigate()
        users.expect_visible()

    users.open_row_menu(username)
    users.click_row_action("Deactivate")


# ===================================================================
# Then
# ===================================================================


@then('the request is rejected with a "user already exists" error')
def then_request_rejected_duplicate(context):
    """Assert an error toast containing 'already exists' appears."""
    # Wait for an error toast that contains the substring "already exists".
    notifications = NotificationsPage(context.page)
    notifications.wait_for_toast(
        "already exists", role="alert", timeout=DEFAULT_TIMEOUT_MS
    )


@then("the authentication is denied")
def then_authentication_denied(context):
    """Assert an error toast appears and the user stays on sign-in."""
    # The backend returns 401 with a message; the frontend shows it as an alert toast
    notifications = NotificationsPage(context.page)
    notifications.wait_for_toast(role="alert", timeout=DEFAULT_TIMEOUT_MS)
    # Verify we did NOT navigate away from sign-in
    assert "/sign-in" in context.page.url, (
        f"Expected to stay on /sign-in, but URL is {context.page.url}"
    )


@then("the user becomes active")
def then_user_becomes_active(context):
    """Assert the row status badge shows 'active'."""
    username = context.current_username

    # Wait for the activation success toast
    notifications = NotificationsPage(context.page)
    notifications.wait_for_toast("activated", role="status", timeout=DEFAULT_TIMEOUT_MS)

    # Verify status badge in the table row
    row = _users_page(context).user_row(username)
    badge = row.locator("text=active").first
    expect(badge).to_be_visible(timeout=SHORT_TIMEOUT_MS)


@then("the user becomes deactivated")
def then_user_becomes_deactivated(context):
    """Assert the row status badge shows 'inactive'."""
    username = context.current_username

    # Wait for the deactivation success toast
    notifications = NotificationsPage(context.page)
    notifications.wait_for_toast(
        "deactivated", role="status", timeout=DEFAULT_TIMEOUT_MS
    )

    # Verify status badge in the table row
    row = _users_page(context).user_row(username)
    badge = row.locator("text=inactive")
    expect(badge).to_be_visible(timeout=SHORT_TIMEOUT_MS)
