"""Sign-in page object."""

from __future__ import annotations

from playwright.sync_api import Page, expect
from test_config import SHORT_TIMEOUT_MS


class SignInPage:
    """``/sign-in`` page — login form with username + password."""

    URL_PATH = "/sign-in"

    def __init__(self, page: Page, base_url: str) -> None:
        self._page = page
        self._base_url = base_url

    # -- Locators (all via data-testid) --

    @property
    def username_input(self):
        return self._page.get_by_test_id("sign-in-username")

    @property
    def password_input(self):
        return self._page.get_by_test_id("sign-in-password")

    @property
    def submit_button(self):
        return self._page.get_by_test_id("sign-in-submit")

    @property
    def form(self):
        return self._page.get_by_test_id("sign-in-form")

    # -- Actions --

    def navigate(self) -> None:
        self._page.goto(f"{self._base_url}{self.URL_PATH}")

    def login(self, username: str, password: str) -> None:
        """Fill credentials and submit the sign-in form."""
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.submit_button.click()

    # -- Assertions --

    def expect_visible(self) -> None:
        expect(self.form).to_be_visible()

    def expect_error_toast(self, text: str) -> None:
        toast = self._page.locator("[data-sonner-toast]").filter(has_text=text)
        expect(toast).to_be_visible(timeout=SHORT_TIMEOUT_MS)
