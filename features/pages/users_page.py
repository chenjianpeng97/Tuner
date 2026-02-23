"""Users list page object."""

from __future__ import annotations

from playwright.sync_api import Page, expect
from test_config import SHORT_TIMEOUT_MS
from pages.notifications_page import NotificationsPage


class UsersPage:
    """``/users`` page — user management table."""

    URL_PATH = "/users"

    def __init__(self, page: Page, base_url: str) -> None:
        self._page = page
        self._base_url = base_url

    # -- Locators --

    @property
    def page_title(self):
        return self._page.get_by_test_id("users-page-title")

    @property
    def table(self):
        return self._page.get_by_test_id("users-table")

    @property
    def add_user_button(self):
        return self._page.get_by_test_id("add-user-button")

    # -- Add User Dialog --

    @property
    def user_form(self):
        return self._page.get_by_test_id("user-action-form")

    @property
    def user_form_username(self):
        return self._page.get_by_test_id("user-form-username")

    @property
    def user_form_submit(self):
        return self._page.get_by_test_id("user-form-submit")

    # -- Actions --

    def navigate(self) -> None:
        self._page.goto(f"{self._base_url}{self.URL_PATH}")

    def user_row(self, username: str):
        """Locate a specific user row by username."""
        return self._page.get_by_test_id(f"user-row-{username}")

    def open_add_user_dialog(self) -> None:
        self.add_user_button.click()
        expect(self.user_form).to_be_visible()

    def fill_add_user(self, username: str, password: str, role: str = "user") -> None:
        """Fill the add-user dialog form fields."""
        self.user_form_username.fill(username)
        # Select role via the dropdown
        self._page.get_by_text("Select a role").click()
        # The frontend shows role labels (e.g. 'User', 'Admin', 'Super Admin').
        # Convert incoming role identifiers like 'user' or 'super_admin'
        # into the UI label before matching to avoid case/underscore mismatches.
        label = role.replace("_", " ").title()
        self._page.get_by_role("option", name=label, exact=True).click()
        # Fill password fields inside the dialog
        password_fields = self.user_form.locator("input[type='password']")
        password_fields.nth(0).fill(password)
        password_fields.nth(1).fill(password)

    def submit_add_user(self) -> None:
        self.user_form_submit.click()

    def create_user(self, username: str, password: str, role: str = "user") -> None:
        """Full flow: open dialog → fill → submit."""
        self.open_add_user_dialog()
        self.fill_add_user(username, password, role)
        self.submit_add_user()

    # -- Row actions --

    def open_row_menu(self, username: str) -> None:
        """Click the ⋯ menu button on a user row."""
        row = self.user_row(username)
        row.get_by_role("button").filter(has_text="Open menu").click()

    def click_row_action(self, action_name: str) -> None:
        """Click an action from the currently-open row menu."""
        self._page.get_by_role("menuitem", name=action_name).click()

    # -- Assertions --

    def expect_visible(self) -> None:
        expect(self.page_title).to_be_visible()

    def expect_table_visible(self) -> None:
        expect(self.table).to_be_visible()

    def expect_user_row(self, username: str) -> None:
        expect(self.user_row(username)).to_be_visible()

    def expect_no_user_row(self, username: str) -> None:
        expect(self.user_row(username)).not_to_be_visible()

    def expect_success_toast(self, text: str = "success") -> None:
        notifications = NotificationsPage(self._page)
        notifications.expect_toast(text, role="status", timeout=SHORT_TIMEOUT_MS)

    def expect_error_toast(self, text: str) -> None:
        notifications = NotificationsPage(self._page)
        notifications.expect_toast(text, role="alert", timeout=SHORT_TIMEOUT_MS)
