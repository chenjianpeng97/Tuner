"""Navigation bar / header component object."""

from __future__ import annotations

from playwright.sync_api import Page, expect


class NavBar:
    """Shared navigation components available on all authenticated pages."""

    def __init__(self, page: Page) -> None:
        self._page = page

    # -- Locators --

    @property
    def profile_trigger(self):
        return self._page.get_by_test_id("profile-dropdown-trigger")

    @property
    def sign_out_item(self):
        return self._page.get_by_test_id("sign-out-menu-item")

    @property
    def confirm_sign_out(self):
        return self._page.get_by_test_id("confirm-dialog-confirm")

    # -- Actions --

    def open_profile_menu(self) -> None:
        self.profile_trigger.click()

    def sign_out(self) -> None:
        """Full sign-out flow: open menu → click sign out → confirm."""
        self.open_profile_menu()
        self.sign_out_item.click()
        self.confirm_sign_out.click()

    # -- Assertions --

    def expect_username(self, username: str) -> None:
        """Verify the profile menu shows the expected username."""
        self.open_profile_menu()
        label = self._page.get_by_text(username)
        expect(label).to_be_visible()
        # Close menu by pressing Escape
        self._page.keyboard.press("Escape")
