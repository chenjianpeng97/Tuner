"""Sign-up page object."""

from __future__ import annotations

from playwright.sync_api import Page, expect
from test_config import SHORT_TIMEOUT_MS
from pages.notifications_page import NotificationsPage


class SignUpPage:
    """``/sign-up`` page — registration form."""

    URL_PATH = "/sign-up"

    def __init__(self, page: Page, base_url: str) -> None:
        self._page = page
        self._base_url = base_url

    # -- Locators --

    @property
    def username_input(self):
        return self._page.get_by_test_id("sign-up-username")

    @property
    def password_input(self):
        return self._page.get_by_test_id("sign-up-password")

    @property
    def confirm_password_input(self):
        return self._page.get_by_test_id("sign-up-confirm-password")

    @property
    def submit_button(self):
        return self._page.get_by_test_id("sign-up-submit")

    @property
    def form(self):
        return self._page.get_by_test_id("sign-up-form")

    # -- Actions --

    def navigate(self) -> None:
        self._page.goto(f"{self._base_url}{self.URL_PATH}")

    def sign_up(self, username: str, password: str) -> None:
        """Fill registration form and submit."""
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.confirm_password_input.fill(password)
        self.submit_button.click()

    # -- Assertions --

    def expect_visible(self) -> None:
        expect(self.form).to_be_visible()

    def expect_error_toast(self, text: str) -> None:
        notifications = NotificationsPage(self._page)
        notifications.expect_toast(text, role="alert", timeout=SHORT_TIMEOUT_MS)

    def expect_success_toast(self) -> None:
        notifications = NotificationsPage(self._page)
        notifications.expect_toast(
            "Account created", role="status", timeout=SHORT_TIMEOUT_MS
        )
