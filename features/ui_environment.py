"""
Behave UI-stage environment (``--stage ui``).

Launches a **real browser** via Playwright that points at a running
frontend (``pnpm dev:api``) backed by a running backend.

Prerequisites before running:
  1. Backend is up: ``cd backend && make up APP_ENV=local``
  2. Frontend is up: ``cd frontend && pnpm dev:api``
  3. Playwright browsers installed: ``playwright install chromium``
  4. A seed super_admin user exists in the database.

Usage from workspace root:
  ``uv run behave --stage ui``
"""

from __future__ import annotations

import os
import sys

# Make sure ``features/`` is on sys.path so page objects can be imported.
_FEATURES_DIR = os.path.dirname(os.path.abspath(__file__))
if _FEATURES_DIR not in sys.path:
    sys.path.insert(0, _FEATURES_DIR)

from playwright.sync_api import sync_playwright


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
FRONTEND_BASE_URL = os.environ.get("UI_BASE_URL", "http://127.0.0.1:5173")
HEADLESS = os.environ.get("UI_HEADLESS", "true").lower() in ("true", "1", "yes")
SLOW_MO = int(os.environ.get("UI_SLOW_MO", "0"))

# Seed super_admin credentials used across scenarios.
ADMIN_USERNAME = os.environ.get("UI_ADMIN_USERNAME", "super_admin")
ADMIN_PASSWORD = os.environ.get("UI_ADMIN_PASSWORD", "admin123")


# ---------------------------------------------------------------------------
# Hooks
# ---------------------------------------------------------------------------
def before_all(context):
    """Start Playwright and launch a single browser for the whole run."""
    context.playwright = sync_playwright().start()
    context.browser = context.playwright.chromium.launch(
        headless=HEADLESS,
        slow_mo=SLOW_MO,
    )
    context.base_url = FRONTEND_BASE_URL
    context.admin_username = ADMIN_USERNAME
    context.admin_password = ADMIN_PASSWORD


def before_scenario(context, scenario):
    """Open a fresh browser context (isolated cookies/storage) per scenario."""
    context.browser_context = context.browser.new_context()
    context.page = context.browser_context.new_page()
    context.current_username = None


def after_scenario(context, scenario):
    """Take a screenshot on failure, then close the context."""
    if scenario.status == "failed":
        _save_screenshot(context, scenario)
    page = getattr(context, "page", None)
    if page:
        page.close()
    ctx = getattr(context, "browser_context", None)
    if ctx:
        ctx.close()


def after_all(context):
    """Shut down the browser and Playwright."""
    browser = getattr(context, "browser", None)
    if browser:
        browser.close()
    pw = getattr(context, "playwright", None)
    if pw:
        pw.stop()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _save_screenshot(context, scenario) -> None:
    """Save a PNG screenshot into features/screenshots/ on failure."""
    page = getattr(context, "page", None)
    if page is None:
        return
    screenshots_dir = os.path.join(_FEATURES_DIR, "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)
    safe_name = scenario.name.replace(" ", "_").replace("/", "_")[:80]
    path = os.path.join(screenshots_dir, f"{safe_name}.png")
    try:
        page.screenshot(path=path)
    except Exception:
        pass
