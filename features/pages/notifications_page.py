"""Notifications (toasts) page object for Playwright tests.

Encapsulates toast selection + wait/assert logic so tests don't repeat
fragile selectors across the codebase.
"""

from __future__ import annotations

from playwright.sync_api import Page, expect
from test_config import DEFAULT_TIMEOUT_MS, SHORT_TIMEOUT_MS


class NotificationsPage:
    """Page object for sonner notifications/toasts.

    The app's toasts should expose either semantic ARIA roles (`role="alert"`
    for errors, `role="status"` for non-errors) and may include a
    `data-toast-type` attribute (e.g. `success`, `error`). This object can be
    updated if the frontend chooses a different attribute.
    """

    def __init__(self, page: Page) -> None:
        self._page = page

    def locator(self, role: str | None = None, toast_type: str | None = None):
        # Prefer semantic ARIA roles if present, but fall back to Sonner's
        # attributes used in the app snapshot: `data-sonner-toast` elements and
        # `data-type` (e.g. "error", "success"). This keeps selectors robust
        # while the frontend migrates to ARIA.
        if role == "alert":
            # ARIA alert (errors) or Sonner toasts of type=error
            role_sel = "[role='alert'], [data-sonner-toast][data-type='error']"
        elif role == "status":
            # ARIA status (non-errors) or Sonner toasts that are not errors
            role_sel = "[role='status'], [data-sonner-toast]:not([data-type='error'])"
        else:
            role_sel = "[role='alert'],[role='status'],[data-sonner-toast]"

        if toast_type:
            # Match either the new `data-toast-type` (if frontend wrapper used)
            # or Sonner's `data-type` attribute.
            return self._page.locator(
                f"{role_sel}[data-toast-type='{toast_type}'], {role_sel}[data-type='{toast_type}']"
            )
        return self._page.locator(role_sel)

    def wait_for_toast(
        self,
        text: str | None = None,
        role: str | None = None,
        timeout: int = DEFAULT_TIMEOUT_MS,
    ) -> None:
        """Wait for a toast to appear. If `text` is provided, wait for a toast
        that contains that text; otherwise wait for any toast with the given
        role to appear.
        """
        if text:
            loc = self.locator(role).filter(has_text=text)
            loc.first.wait_for(state="visible", timeout=timeout)
        else:
            self.locator(role).first.wait_for(state="visible", timeout=timeout)

    def expect_toast(
        self, text: str, role: str | None = None, timeout: int = SHORT_TIMEOUT_MS
    ) -> None:
        loc = self.locator(role).filter(has_text=text)
        expect(loc).to_be_visible(timeout=timeout)

    def latest_toast_text(self, role: str | None = None) -> str:
        return self.locator(role).first.inner_text()
