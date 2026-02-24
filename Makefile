## Convenience Makefile for running BDD scenarios

.PHONY: bdd-ui-headful-smoke bdd-http-generic-smoke

# Run the UI behave scenario in headed (non-headless) mode.
# Usage:
#   make bdd-ui-headful                # runs default scenario against 127.0.0.1:5173
#   UI_BASE_URL=http://127.0.0.1:5173 \
#   SCENARIO_NAME="Reject creating a user with a duplicate username" \
#   make bdd-ui-headful-smock

bdd-ui-headful-smoke:
	@echo "Running UI BDD (headful)..."
	@UI_HEADLESS=false \
	UI_BASE_URL=${UI_BASE_URL:http://127.0.0.1:5173} \
	SCENARIO_NAME="${SCENARIO_NAME:Reject creating a user with a duplicate username}" \
	uv run behave --stage ui ./features/user.feature --name "$$SCENARIO_NAME"

# Run HTTP generic smoke scenario from demo module.
bdd-http-generic-smoke:
	@echo "Running HTTP generic component smoke..."
	@uv run behave --stage http ./features/demo/generic_components_smoke.feature
