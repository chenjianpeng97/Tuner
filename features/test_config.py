"""Central test configuration for UI timeouts.

Place shared timeout values here so different test environments can
override them via environment variables (e.g. CI vs local dev).
"""

from __future__ import annotations

import os

# Milliseconds (Playwright expects ms for timeouts)
DEFAULT_TIMEOUT_MS = int(os.environ.get("UI_DEFAULT_TIMEOUT_MS", "10000"))
SHORT_TIMEOUT_MS = int(os.environ.get("UI_SHORT_TIMEOUT_MS", "5000"))

__all__ = ["DEFAULT_TIMEOUT_MS", "SHORT_TIMEOUT_MS"]
