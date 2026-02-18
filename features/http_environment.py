"""
Behave HTTP-stage environment (``--stage http``).

Uses FastAPI's ``TestClient`` with a **mocked DI container** so that
**no running server, database, or external service** is required.
Only presentation-layer dependencies are needed:
``fastapi``, ``dishka``, ``fastapi-error-map``, ``httpx``.

The mocked interactors / handlers can be configured per-step via
``context.mocks`` (a :class:`mock_app.MockRegistry` instance).
"""

from __future__ import annotations

import os
import sys

# ---------------------------------------------------------------------------
# Make ``features/`` and ``backend/src`` importable so that both
# ``mock_app`` and ``app.*`` modules can be resolved.
# ---------------------------------------------------------------------------
_FEATURES_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_SRC = os.path.normpath(
    os.path.join(_FEATURES_DIR, "..", "backend", "src"),
)
for _p in (_FEATURES_DIR, _BACKEND_SRC):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fastapi.testclient import TestClient  # noqa: E402

from mock_app import MockRegistry, create_test_app  # noqa: E402


# ---------------------------------------------------------------------------
# Hooks
# ---------------------------------------------------------------------------
def before_all(context):
    context.mocks = MockRegistry()
    context.app = create_test_app(context.mocks)


def before_scenario(context, scenario):
    context.mocks.reset_all()
    context.users = {}
    context.response = None
    context.current_username = None
    context.client = TestClient(context.app)


def after_scenario(context, scenario):
    client = getattr(context, "client", None)
    if client is not None:
        client.close()
